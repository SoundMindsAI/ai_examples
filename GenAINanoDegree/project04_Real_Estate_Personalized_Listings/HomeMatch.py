# HomeMatch.py

import os
import re
import json
import logging
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import time
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to capture more detailed logs.
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('homematch.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Set your OpenAI API key and base URL
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_API_BASE"] = ""

# Initialize the OpenAI LLM (via LangChain) and the sentence transformer for embeddings
logger.info("Initializing OpenAI LLM and sentence transformer")
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
embedder = SentenceTransformer('all-MiniLM-L6-v2')


def generate_listings(total_count=30, batch_size=10):
    """
    Generate real estate listings using multiple API calls.
    
    Args:
        total_count (int): Total number of listings to generate
        batch_size (int): Number of listings to generate per API call
    
    Returns:
        list: List of all generated listings
    """
    logger.info(f"Starting listing generation for {total_count} listings")
    all_listings = []
    
    while len(all_listings) < total_count:
        logger.info(f"Generating batch of {batch_size} listings ({len(all_listings)}/{total_count} total)")
        
        system_message = SystemMessage(content=(
            "You are a real estate listing generator. You generate JSON arrays of realistic property listings. "
            "Each listing should be unique and detailed, with realistic prices and descriptions based on the neighborhood."
        ))
        
        human_message = HumanMessage(content=(
            f"Generate a JSON array of {batch_size} real estate listings. Each listing should be an object with these exact fields:\n"
            "- Neighborhood (string)\n"
            "- Price (string, format: $X,XXX,XXX)\n"
            "- Bedrooms (number)\n"
            "- Bathrooms (number)\n"
            "- House Size (string, format: X,XXX sqft)\n"
            "- Description (string)\n"
            "- Neighborhood Description (string)\n\n"
            "Here's an example listing object:\n"
            "{\n"
            '  "Neighborhood": "Green Oaks",\n'
            '  "Price": "$800,000",\n'
            '  "Bedrooms": 3,\n'
            '  "Bathrooms": 2,\n'
            '  "House Size": "2,000 sqft",\n'
            '  "Description": "Welcome to this eco-friendly oasis nestled in the heart of Green Oaks. This charming 3-bedroom, 2-bathroom home boasts energy-efficient features such as solar panels and a well-insulated structure. Natural light floods the living spaces, highlighting the beautiful hardwood floors and eco-conscious finishes. The open-concept kitchen and dining area lead to a spacious backyard with a vegetable garden, perfect for the eco-conscious family. Embrace sustainable living without compromising on style in this Green Oaks gem.",\n'
            '  "Neighborhood Description": "Green Oaks is a close-knit, environmentally-conscious community with access to organic grocery stores, community gardens, and bike paths. Take a stroll through the nearby Green Oaks Park or grab a cup of coffee at the cozy Green Bean Cafe. With easy access to public transportation and bike lanes, commuting is a breeze."\n'
            "}\n\n"
            "Return ONLY a valid JSON array of similar listings. Do not include any markdown formatting, extra text, or explanations."
        ))
        
        logger.info("Sending request to OpenAI API")
        response = llm([system_message, human_message])
        logger.debug("Raw response received (first 500 characters): %s", response.content[:500])
        
        try:
            content = response.content.strip()
            logger.debug("Stripped response content: %s", content)
            
            try:
                # Try parsing the content directly as JSON first
                batch_listings = json.loads(content)
                logger.debug("Successfully parsed content directly as JSON")
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from markdown or other formatting
                match = re.search(r'```(?:json)?\s*(\[[\s\S]*\])\s*```', content)
                if match:
                    json_str = match.group(1)
                    logger.debug("Extracted JSON string using markdown regex")
                    batch_listings = json.loads(json_str)
                else:
                    # Second fallback: try to extract anything that looks like a JSON array
                    match = re.search(r'(\[[\s\S]*\])', content)
                    if match:
                        json_str = match.group(1)
                        logger.debug("Extracted JSON string using fallback regex")
                        batch_listings = json.loads(json_str)
                    else:
                        logger.error("Could not find JSON array in response")
                        # Write the full response to a file for further inspection
                        with open("raw_llm_response.txt", "w") as raw_file:
                            raw_file.write(content)
                        raise ValueError("Could not find JSON array in response")
            
            all_listings.extend(batch_listings)
            logger.info(f"Successfully generated batch of {len(batch_listings)} listings")
            
            # Add a small delay between batches to avoid rate limiting
            if len(all_listings) < total_count:
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error generating listings: {str(e)}")
            continue
    
    return all_listings[:total_count]  # Ensure we don't return more than requested


def store_listings_in_vector_db(listings, embedder, collection):
    """
    Store listings in the vector database with embeddings.
    """
    logger.info("Starting to store listings in vector database")
    
    # Add IDs to listings if they don't exist
    for i, listing in enumerate(listings):
        listing["id"] = f"listing_{i+1}"
    
    try:
        # Convert listings to JSON strings for storage
        documents = [json.dumps(listing) for listing in listings]
        
        # Generate embeddings for each listing description
        descriptions = [listing["Description"] + " " + listing["Neighborhood Description"] for listing in listings]
        embeddings = embedder.encode(descriptions)
        
        # Store listings with their embeddings
        collection.add(
            ids=[listing["id"] for listing in listings],
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=listings
        )
        logger.info("Successfully stored listings in vector database")
    except Exception as e:
        logger.error("Error storing listings in vector database: %s", str(e))
        raise


def get_buyer_preferences():
    """
    In a real application, you might collect these interactively.
    For this example, we hard-code the buyer's answers.
    """
    questions = [
        "How big do you want your house to be?",
        "What are 3 most important things for you in choosing this property?",
        "Which amenities would you like?",
        "Which transportation options are important to you?",
        "How urban do you want your neighborhood to be?",
    ]
    answers = [
        "A comfortable three-bedroom house with a spacious kitchen and a cozy living room.",
        "A quiet neighborhood, good local schools, and convenient shopping options.",
        "A backyard for gardening, a two-car garage, and a modern, energy-efficient heating system.",
        "Easy access to a reliable bus line, proximity to a major highway, and bike-friendly roads.",
        "A balance between suburban tranquility and access to urban amenities like restaurants and theaters."
    ]
    # Combine questions and answers into a single query string
    buyer_query = " ".join([f"Q: {q} A: {a}" for q, a in zip(questions, answers)])
    return buyer_query


def personalize_listing_description(listing, buyer_preferences):
    """
    Personalize a listing description while maintaining the original content.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a real estate agent who specializes in highlighting property features that match buyer preferences.
                    IMPORTANT: Your task is to maintain the EXACT SAME FACTS and STRUCTURE as the original description, while subtly emphasizing 
                    features that align with the buyer's preferences. Follow these rules strictly:
                    1. Keep all original facts, features, and details EXACTLY as they are
                    2. Maintain the same paragraph structure and flow
                    3. Do not add any new features or amenities that weren't in the original
                    4. Do not remove any details from the original
                    5. Only make minimal wording adjustments to emphasize features that match buyer preferences
                    6. If a buyer preference isn't mentioned in the original, do not add it"""
                },
                {
                    "role": "user",
                    "content": f"""Below are buyer preferences:
Q: How big do you want your house to be? A: A comfortable three-bedroom house with a spacious kitchen and a cozy living room.
Q: What are 3 most important things for you in choosing this property? A: A quiet neighborhood, good local schools, and convenient shopping options.
Q: Which amenities would you like? A: A backyard for gardening, a two-car garage, and a modern, energy-efficient heating system.
Q: Which transportation options are important to you? A: Easy access to a reliable bus line, proximity to a major highway, and bike-friendly roads.
Q: How urban do you want your neighborhood to be? A: A balance between suburban tranquility and access to urban amenities like restaurants and theaters.

Here is the original property description:
{listing['Description']}

Please generate a personalized property description that subtly emphasizes the aspects of the property that align with the buyer's needs.
Remember: Keep the exact same facts, features, and structure. Only make minimal adjustments to emphasize matching features."""
                }
            ],
            temperature=0.0,
            max_tokens=None,
            n=1,
            stream=False,
        )
        
        personalized_description = response.choices[0].message.content.strip()
        return personalized_description
    except Exception as e:
        logger.error(f"Error personalizing listing description: {str(e)}")
        return listing['Description']  # Return original if there's an error


def write_listing_to_markdown(f, listing, personalized_description):
    """Write a listing to the markdown file."""
    f.write(f"### {listing['Neighborhood']} - {listing['Price']}\n\n")
    f.write(f"{listing['Description']}\n\n")
    f.write("#### Personalized Highlights\n\n")
    f.write(f"{personalized_description}\n\n")
    f.write("---\n\n")


def evaluate_listing_accuracy(listing, user_preferences):
    """
    Evaluate how well a listing matches user preferences with enhanced scoring.
    Returns a dictionary with weighted scores for different preference categories.
    """
    # Define category weights (total = 100)
    weights = {
        'size_match': 35,        # Most important - exact size match
        'price_range': 20,       # Price considerations
        'location_priorities': 15, # Schools, quiet, shopping
        'amenities': 10,         # Specific features requested
        'transportation': 10,     # Transit options
        'urban_balance': 10      # Neighborhood feel
    }
    
    scores = {category: 0 for category in weights.keys()}
    
    # Size match (3 bedroom preference) with penalties for larger sizes
    if listing['Bedrooms'] == 3:
        scores['size_match'] = 100
    else:
        # Larger penalty for more deviation from 3 bedrooms
        deviation = abs(listing['Bedrooms'] - 3)
        scores['size_match'] = max(0, 100 - (deviation * 30))  # 30% penalty per bedroom difference
    
    # Price range analysis (assuming target range $600k-$900k)
    price = int(listing['Price'].replace('$', '').replace(',', ''))
    if 600000 <= price <= 900000:
        scores['price_range'] = 100
    else:
        # 10% penalty for every $100k outside the range
        deviation = min(abs(price - 600000), abs(price - 900000))
        penalty = (deviation / 100000) * 10
        scores['price_range'] = max(0, 100 - penalty)
    
    # Location priorities with contextual analysis
    priority_keywords = {
        'quiet_neighborhood': ['quiet', 'peaceful', 'tranquil', 'serene'],
        'schools': ['school', 'education', 'academic', 'learning'],
        'shopping': ['shop', 'store', 'retail', 'market', 'commercial']
    }
    
    description = (listing['Description'] + ' ' + listing['Neighborhood Description']).lower()
    
    # Check each priority with context
    priority_scores = []
    for category, keywords in priority_keywords.items():
        # Base score on keyword presence
        keyword_matches = sum(1 for keyword in keywords if keyword in description)
        # Add contextual analysis
        if category == 'quiet_neighborhood' and any(neg in description for neg in ['busy', 'noisy', 'traffic']):
            keyword_matches = max(0, keyword_matches - 1)
        priority_scores.append(min(100, (keyword_matches / len(keywords)) * 100))
    
    scores['location_priorities'] = sum(priority_scores) / len(priority_scores)
    
    # Amenities with specific feature matching
    amenity_features = {
        'backyard': ['backyard', 'garden', 'patio', 'outdoor'],
        'garage': ['garage', 'parking', 'car'],
        'modern_systems': ['modern', 'energy', 'efficient', 'heating', 'cooling', 'hvac']
    }
    
    amenity_scores = []
    for feature, keywords in amenity_features.items():
        matches = sum(1 for keyword in keywords if keyword in description)
        feature_score = min(100, (matches / len(keywords)) * 100)
        # Bonus for multiple matches in the same category
        if matches > 1:
            feature_score = min(100, feature_score + 10)
        amenity_scores.append(feature_score)
    
    scores['amenities'] = sum(amenity_scores) / len(amenity_scores)
    
    # Transportation with negative scoring
    transport_keywords = {
        'positive': ['bus', 'transit', 'highway', 'bike', 'commute', 'transportation'],
        'negative': ['limited transit', 'no bus', 'poor access']
    }
    
    transport_score = 0
    positive_matches = sum(1 for keyword in transport_keywords['positive'] if keyword in description)
    transport_score = min(100, (positive_matches / len(transport_keywords['positive'])) * 100)
    
    # Apply penalties for negative transport mentions
    if any(neg in description for neg in transport_keywords['negative']):
        transport_score = max(0, transport_score - 30)  # 30-point penalty for negative transport mentions
    
    scores['transportation'] = transport_score
    
    # Urban balance with context analysis
    balance_keywords = {
        'suburban': ['suburban', 'quiet', 'peaceful', 'residential'],
        'urban_amenities': ['restaurant', 'theater', 'shopping', 'entertainment']
    }
    
    # Check for balance between suburban and urban features
    suburban_matches = sum(1 for keyword in balance_keywords['suburban'] if keyword in description)
    urban_matches = sum(1 for keyword in balance_keywords['urban_amenities'] if keyword in description)
    
    # Perfect balance would be equal representation of both
    balance_ratio = min(suburban_matches, urban_matches) / max(suburban_matches, urban_matches) if max(suburban_matches, urban_matches) > 0 else 0
    scores['urban_balance'] = balance_ratio * 100
    
    # Calculate weighted overall match percentage
    overall_match = sum(scores[category] * (weights[category] / 100) for category in weights.keys())
    scores['overall_match'] = overall_match
    
    # Add detailed subscores for analysis
    scores['details'] = {
        'bedroom_count': listing['Bedrooms'],
        'price_actual': price,
        'keyword_matches': {
            'location': priority_scores,
            'amenities': amenity_scores,
            'transport': transport_score,
            'balance': {'suburban': suburban_matches, 'urban': urban_matches}
        }
    }
    
    return scores


def analyze_listings_accuracy(listings):
    """
    Analyze all listings and return detailed accuracy statistics.
    """
    user_preferences = {
        'size': '3 bedrooms',
        'price_range': {'min': 600000, 'max': 900000},
        'priorities': ['quiet neighborhood', 'good schools', 'convenient shopping'],
        'amenities': ['backyard', 'two-car garage', 'modern heating'],
        'transportation': ['bus line', 'highway', 'bike-friendly'],
        'urban_preference': 'suburban with urban amenities'
    }
    
    all_scores = []
    for listing in listings:
        scores = evaluate_listing_accuracy(listing, user_preferences)
        all_scores.append(scores)
    
    # Calculate average scores
    avg_scores = {
        category: sum(score[category] for score in all_scores) / len(all_scores)
        for category in all_scores[0].keys()
        if category != 'details'
    }
    
    # Find best and worst matches
    best_match = max(all_scores, key=lambda x: x['overall_match'])
    worst_match = min(all_scores, key=lambda x: x['overall_match'])
    
    # Calculate standard deviation for each category
    std_dev = {}
    for category in avg_scores.keys():
        if category != 'details':
            values = [score[category] for score in all_scores]
            std_dev[category] = (sum((x - avg_scores[category]) ** 2 for x in values) / len(values)) ** 0.5
    
    return {
        'average_scores': avg_scores,
        'best_match_score': best_match['overall_match'],
        'worst_match_score': worst_match['overall_match'],
        'standard_deviation': std_dev,
        'total_listings': len(listings),
        'price_distribution': {
            'min': min(score['details']['price_actual'] for score in all_scores),
            'max': max(score['details']['price_actual'] for score in all_scores),
            'avg': sum(score['details']['price_actual'] for score in all_scores) / len(all_scores)
        },
        'bedroom_distribution': {
            count: sum(1 for score in all_scores if score['details']['bedroom_count'] == count)
            for count in range(1, 7)
        }
    }


def main():
    try:
        logger.info("Starting HomeMatch application")
        
        # Initialize components
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        client = chromadb.PersistentClient(path="./chromadb_storage")
        
        # Delete existing collection if it exists and create a new one
        try:
            client.delete_collection("home_listings")
            logger.info("Deleted existing collection 'home_listings'")
        except Exception as e:
            logger.info(f"No existing collection to delete: {str(e)}")
        
        collection = client.create_collection("home_listings")
        logger.info("Created new collection 'home_listings'")

        # Generate and store listings
        num_listings = 100
        logger.info(f"Starting listing generation for {num_listings} listings")
        listings = generate_listings(total_count=num_listings, batch_size=10)
        if not listings:
            logger.error("No listings generated")
            return
        
        logger.info(f"Successfully generated {len(listings)} listings")
        
        # Analyze listing accuracy
        logging.info("Analyzing listing accuracy...")
        accuracy_stats = analyze_listings_accuracy(listings)
        logging.info(f"Accuracy Analysis Results:")
        logging.info(f"Average Overall Match: {accuracy_stats['average_scores']['overall_match']:.2f}%")
        logging.info(f"Best Match Score: {accuracy_stats['best_match_score']:.2f}%")
        logging.info(f"Worst Match Score: {accuracy_stats['worst_match_score']:.2f}%")
        
        logging.info("\nCategory Averages:")
        for category, score in accuracy_stats['average_scores'].items():
            if category != 'overall_match':
                logging.info(f"  {category}: {score:.2f}% (std dev: {accuracy_stats['standard_deviation'][category]:.2f})")
        
        logging.info("\nBedroom Distribution:")
        for bedrooms, count in accuracy_stats['bedroom_distribution'].items():
            if count > 0:
                logging.info(f"  {bedrooms} bedrooms: {count} listings")
        
        logging.info("\nPrice Distribution:")
        logging.info(f"  Min: ${accuracy_stats['price_distribution']['min']:,}")
        logging.info(f"  Max: ${accuracy_stats['price_distribution']['max']:,}")
        logging.info(f"  Avg: ${accuracy_stats['price_distribution']['avg']:,.2f}")

        # Store all listings in vector database
        store_listings_in_vector_db(listings, embedder, collection)
        
        # Get buyer preferences
        logger.info("Getting buyer preferences")
        buyer_preferences_text = get_buyer_preferences()
        
        # Search for matching listings
        logger.info("Searching for matching listings")
        buyer_embedding = embedder.encode(buyer_preferences_text).tolist()
        query_result = collection.query(
            query_embeddings=[buyer_embedding],
            n_results=30,  # Request all results to filter
            include=["distances", "metadatas", "documents"]
        )

        # Set a threshold for similarity (lower distance means higher similarity)
        threshold = 0.2  # Lower threshold for more precise matching; adjust as needed

        # Filter results that are within the threshold
        filtered_results = []
        distances = query_result.get("distances", [[]])[0]
        for idx, distance in enumerate(distances):
            if distance < threshold:
                filtered_results.append(idx)

        # If no results pass the threshold, fall back to the top n_results
        if not filtered_results:
            logger.warning("No listings found within the threshold. Using top results instead.")
            filtered_results = list(range(len(query_result["metadatas"][0])))

        logger.info("Found %d matching listings after filtering", len(filtered_results))
        
        # Write results to markdown
        with open("output.md", "w") as f:
            f.write("# HomeMatch - Top Property Matches\n\n")
            f.write("Here are your top 3 property matches based on your preferences:\n\n")
            f.write("## Buyer Preferences\n\n")
            f.write(f"{buyer_preferences_text}\n\n")
            
            # Write top 3 matches
            for idx in filtered_results[:3]:  
                matched_listing = query_result["metadatas"][0][idx]
                personalized_description = personalize_listing_description(matched_listing, buyer_preferences_text)
                write_listing_to_markdown(f, matched_listing, personalized_description)

        logger.info("HomeMatch application completed successfully")
        
    except Exception as e:
        logger.error(f"Error in HomeMatch application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
