"""
A conversational AI chatbot using RAG (Retrieval Augmented Generation) with Wikipedia data.
This implementation uses FAISS for efficient similarity search and vector storage,
OpenAI's GPT-3.5-turbo for text generation, and Wikipedia as the knowledge source.

See the README.md file for more details and usage instructions.
"""

import os
import sys
import time
import wikipedia
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from openai import RateLimitError

# Load environment variables from .env file
load_dotenv()

def retry_with_exponential_backoff(
    func,
    max_retries=10,    # Maximum number of retry attempts
    initial_delay=10,  # Base delay in seconds
    exponential_base=2,  # Multiplier for exponential backoff
    error_types=(RateLimitError, Exception)  # Errors to catch and retry
):
    """
    A decorator that implements exponential backoff retry logic.
    Retries the decorated function on failure, with increasing delays between attempts.
    """
    
    def wrapper(*args, **kwargs):
        delay = initial_delay
        
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if i == max_retries - 1:  # Last attempt
                    raise e
                
                if isinstance(e, RateLimitError):
                    wait_time = delay * 3  # Extended delay for rate limits
                else:
                    wait_time = delay
                    
                print(f"\nError: {str(e)}")
                print(f"Retrying in {wait_time} seconds... (Attempt {i + 1}/{max_retries})")
                time.sleep(wait_time)
                delay *= exponential_base
                
        return func(*args, **kwargs)
        
    return wrapper

@retry_with_exponential_backoff
def create_vector_store(text_content):
    """
    Creates a FAISS vector store from text content.
    Splits text into chunks, generates embeddings, and builds a searchable index.
    """
    # Configure text splitting parameters for optimal context preservation
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Number of tokens per chunk
        chunk_overlap=100,  # Overlap between chunks for context continuity
        length_function=len
    )
    chunks = text_splitter.split_text(text_content)
    
    # Initialize embedding model and batch processing parameters
    embeddings = OpenAIEmbeddings()
    batch_size = 5  # Number of chunks to process in each batch
    all_embeddings = []
    
    print("Processing text chunks...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            batch_embeddings = embeddings.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
            print(f"Processed chunks {i + 1}-{min(i + batch_size, len(chunks))} of {len(chunks)}")
            time.sleep(2)  # Delay between batches to respect rate limits
        except Exception as e:
            print(f"Error processing batch: {str(e)}")
            raise
    
    # Build the FAISS index for similarity search
    vector_store = FAISS.from_texts(
        chunks,
        embeddings
    )
    return vector_store

@retry_with_exponential_backoff
def get_qa_response(qa_chain, question, chat_history):
    """
    Generates a response using the RAG-enhanced QA chain.
    Incorporates chat history for context-aware responses.
    """
    return qa_chain.invoke({"question": question, "chat_history": chat_history})

@retry_with_exponential_backoff
def get_base_model_response(llm, question):
    """
    Generates a response using only the base language model.
    Provides a baseline response without RAG enhancement.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant knowledgeable about AI history."},
        {"role": "user", "content": question}
    ]
    response = llm.invoke(messages)
    return response.content

def main():
    # Verify API key configuration
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file")
        return

    try:
        # Initialize knowledge base from Wikipedia
        print("Fetching Wikipedia article...")
        article = wikipedia.page("History of artificial intelligence")
        content = article.content
        wiki_url = article.url  # Store source URL for attribution

        # Build vector store for similarity search
        print("Creating vector store...")
        vector_store = create_vector_store(content)

        # Initialize language models and QA chain
        print("Setting up models...")
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,  # Deterministic responses
            request_timeout=60,  # Response timeout in seconds
            max_retries=5    # Model-specific retry limit
        )
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            vector_store.as_retriever(search_kwargs={"k": 3}),  # Retrieve top 3 relevant chunks
            return_source_documents=True
        )

        # Start interactive chat session
        chat_history = []
        print("\nChat with AI History Bot (type 'quit' to exit)")
        print("----------------------------------------")
        print("You'll get two responses for each question:")
        print("1. Base GPT-3.5-turbo response (without RAG)")
        print("2. Enhanced response using RAG with Wikipedia data")
        print("----------------------------------------")

        while True:
            try:
                question = input("\nYou: ")
                if question.lower() == 'quit':
                    break

                # Generate and display base model response
                print("\n🤖 Base GPT-3.5-turbo Response:")
                print("-" * 40)
                base_response = get_base_model_response(llm, question)
                print(base_response)
                
                # Generate and display RAG-enhanced response
                print("\n📚 RAG-Enhanced Response:")
                print("-" * 40)
                result = get_qa_response(qa_chain, question, chat_history)
                answer = result["answer"]
                chat_history.append((question, answer))
                print(answer)
                print(f"\nSource: {wiki_url}")
                print("(This response is enhanced with information from the Wikipedia article)")
                
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again.")
                continue

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
