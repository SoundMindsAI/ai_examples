from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter
import json
import os
import traceback
from typing import Dict, Any
from pydantic import BaseModel
import re

from llm_query_understand.llm import LargeLanguageModel
from llm_query_understand.cache import QueryCache
from llm_query_understand.logging_config import get_logger

# Get the configured logger
logger = get_logger()

# Initialize the FastAPI application
logger.info("Initializing LLM Query Understanding Service")
app = FastAPI(
    title="LLM Query Understanding Service",
    description="A service that transforms unstructured search queries into structured data",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt template for furniture query parsing
FURNITURE_PROMPT = """
You are a JSON processor for furniture queries. Your job is to extract structured data from search queries.

IMPORTANT: Your ENTIRE response must be a SINGLE valid JSON object. Do not include ANY explanatory text.

Extract these fields from the query:
- item_type: The main furniture item (sofa, table, chair, etc.)
- material: The material mentioned (wood, metal, plastic, etc.)
- color: The color mentioned (red, blue, green, etc.)

Omit a field if not specified in the query.

Examples:
Query: "black leather couch"
Response: {"item_type": "couch", "material": "leather", "color": "black"}

Query: "wooden dining table"
Response: {"item_type": "dining table", "material": "wood"}

Query: "blue metal office chair with armrests"
Response: {"item_type": "office chair", "material": "metal", "color": "blue"}

YOUR TURN - Parse this query ONLY (output just one JSON object, nothing else): 
"""

# Record startup time
startup_time = perf_counter()

# Initialize the LLM and cache
logger.info("Initializing language model")
llm = LargeLanguageModel()

logger.info("Initializing query cache")
cache = QueryCache()

# Log when application is fully initialized
logger.info(f"Service initialized in {perf_counter() - startup_time:.2f} seconds")

# Define Pydantic models for request and response
class QueryRequest(BaseModel):
    """
    Request model for query understanding
    
    Example:
        ```json
        {
            "query": "red wooden sofa with armrests"
        }
        ```
    """
    query: str

class ParsedQuery(BaseModel):
    item_type: str = None
    material: str = None
    color: str = None

class QueryResponse(BaseModel):
    generation_time: float
    parsed_query: ParsedQuery
    query: str
    cached: bool
    total_time: float
    cache_lookup_time: float = None

@app.get("/")
async def root():
    """Root endpoint that returns service information"""
    logger.debug("Root endpoint called")
    return {
        "service": "LLM Query Understanding Service",
        "version": "1.0.0",
        "endpoints": {
            "/parse": "Parse a search query into structured data",
            "/health": "Health check endpoint",
            "/docs": "Swagger UI interactive API documentation",
            "/redoc": "ReDoc API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

@app.post("/parse", response_model=QueryResponse)
async def query_understand(request: QueryRequest):
    """
    Parse a search query into structured data using an LLM
    
    The request should include a 'query' field with the text to parse.
    
    Example:
        ```json
        {
            "query": "red wooden sofa with armrests"
        }
        ```
    """
    request_id = f"req_{perf_counter():.0f}"
    logger.info(f"[{request_id}] Received parse request")
    start = perf_counter()
    
    try:
        query = request.query
        
        logger.info(f"[{request_id}] Processing query: '{query}'")
        
        # Check cache first
        cache_start = perf_counter()
        cached_result = cache.get(query)
        cache_time = perf_counter() - cache_start
        
        if cached_result:
            logger.info(f"[{request_id}] Cache hit, returning cached result (lookup took {cache_time:.4f}s)")
            cached_result["cached"] = True
            cached_result["cache_lookup_time"] = round(cache_time, 4)
            cached_result["total_time"] = round(perf_counter() - start, 4)
            return cached_result
        
        logger.info(f"[{request_id}] Cache miss, generating response with LLM")
        
        # Not in cache, generate response with LLM
        prompt = FURNITURE_PROMPT + query
        logger.debug(f"[{request_id}] Using prompt: {prompt[:100]}...")
        
        # Generate response from LLM
        response = llm.generate(prompt, max_new_tokens=100)
        generation_time = perf_counter() - start
        logger.info(f"[{request_id}] Generation time: {generation_time:.2f} seconds")
        
        # Process the response
        try:
            # Extract the JSON part from the response
            logger.debug(f"[{request_id}] Raw LLM response: {response}")
            
            # Try to extract JSON from the response using different methods
            parsed_query = None
            
            # Method 1: Clean and attempt to parse the entire response first
            try:
                cleaned_response = response.strip()
                if cleaned_response.startswith("{") and cleaned_response.endswith("}"):
                    # Try parsing the entire response as JSON if it looks like a JSON object
                    candidate = json.loads(cleaned_response)
                    if isinstance(candidate, dict) and any(key in candidate for key in ["item_type", "material", "color"]):
                        parsed_query = candidate
                        logger.info(f"[{request_id}] Successfully parsed complete response as JSON: {parsed_query}")
            except json.JSONDecodeError:
                pass
            
            # Method 2: Use regex to find JSON patterns, skip known example patterns
            if parsed_query is None:
                known_examples = [
                    '{"item_type": "couch", "material": "leather", "color": "black"}',
                    '{"item_type": "dining table", "material": "wood"}',
                    '{"item_type": "office chair", "material": "metal", "color": "blue"}'
                ]
                
                json_patterns = re.findall(r'(\{.*?\})', response, re.DOTALL)
                
                for pattern in json_patterns:
                    pattern_str = pattern.strip()
                    # Skip if this is one of our examples from the prompt
                    if any(example in pattern_str for example in known_examples):
                        continue
                    
                    try:
                        candidate = json.loads(pattern_str)
                        if isinstance(candidate, dict) and any(key in candidate for key in ["item_type", "material", "color"]):
                            parsed_query = candidate
                            logger.info(f"[{request_id}] Successfully parsed query into JSON using regex: {parsed_query}")
                            break
                    except json.JSONDecodeError:
                        continue
            
            # Method 3: Check for JSON code blocks (``` or `)
            if parsed_query is None:
                code_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if not code_blocks:
                    code_blocks = re.findall(r'`(\{.*?\})`', response, re.DOTALL)
                
                for block in code_blocks:
                    try:
                        # Skip if this is one of our examples from the prompt
                        if any(example in block for example in known_examples):
                            continue
                            
                        candidate = json.loads(block)
                        if isinstance(candidate, dict) and any(key in candidate for key in ["item_type", "material", "color"]):
                            parsed_query = candidate
                            logger.info(f"[{request_id}] Successfully parsed query into JSON from code block: {parsed_query}")
                            break
                    except json.JSONDecodeError:
                        continue
            
            # If we successfully parsed a query, prepare the result
            if parsed_query is not None:
                # Ensure parsed query matches the query's main elements
                query_terms = query.lower().split()
                
                # Do a basic sanity check - if item_type is completely wrong, try to fix it
                if 'item_type' in parsed_query and parsed_query['item_type'] is not None:
                    furniture_terms = ['chair', 'table', 'sofa', 'couch', 'desk', 'bed', 'cabinet', 'dresser', 'bookshelf']
                    
                    # Check if the right furniture type is in the query
                    query_furniture = next((term for term in query_terms if any(furniture in term for furniture in furniture_terms)), None)
                    parsed_furniture = parsed_query['item_type'].lower() if parsed_query['item_type'] else None
                    
                    # If our query mentions furniture, but the parsed result has the wrong type
                    if query_furniture and parsed_furniture and query_furniture not in parsed_furniture:
                        logger.warning(f"[{request_id}] Parsed item_type '{parsed_furniture}' doesn't match query furniture '{query_furniture}'. Fixing.")
                        parsed_query['item_type'] = query_furniture
                
                # Handle detected material - similarly, validate and fix if needed
                if 'material' in parsed_query and parsed_query['material'] is not None:
                    materials = ['wood', 'wooden', 'metal', 'plastic', 'glass', 'leather', 'fabric', 'cotton']
                    query_material = next((term for term in query_terms if any(material in term for material in materials)), None)
                    parsed_material = parsed_query['material'].lower() if parsed_query['material'] else None
                    
                    if query_material and parsed_material and query_material not in parsed_material:
                        logger.warning(f"[{request_id}] Parsed material '{parsed_material}' doesn't match query material '{query_material}'. Fixing.")
                        parsed_query['material'] = query_material
                
                # Handle detected color - validate and fix if needed
                if 'color' in parsed_query and parsed_query['color'] is not None:
                    colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'purple', 'orange', 'pink', 'gray', 'grey']
                    query_color = next((term for term in query_terms if term in colors), None)
                    parsed_color = parsed_query['color'].lower() if parsed_query['color'] else None
                    
                    if query_color and parsed_color and query_color != parsed_color:
                        logger.warning(f"[{request_id}] Parsed color '{parsed_color}' doesn't match query color '{query_color}'. Fixing.")
                        parsed_query['color'] = query_color
                
                # Prepare the result
                result = {
                    "generation_time": round(generation_time, 2),
                    "parsed_query": parsed_query,
                    "query": query,
                    "cached": False,
                    "total_time": round(perf_counter() - start, 4)
                }
                
                # Store in cache for future use
                cache_store_start = perf_counter()
                cache_success = cache.set(query, result)
                cache_store_time = perf_counter() - cache_store_start
                
                if cache_success:
                    logger.debug(f"[{request_id}] Result cached successfully in {cache_store_time:.4f}s")
                
                return result
            
            # If we reached here, we couldn't parse any valid JSON
            error_msg = "Failed to find valid JSON in LLM response"
            logger.error(f"[{request_id}] {error_msg}")
            logger.error(f"[{request_id}] Problematic LLM response: {response}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to parse response from LLM",
                    "details": error_msg,
                    "response": response
                }
            )
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from LLM response: {str(e)}"
            logger.error(f"[{request_id}] {error_msg}")
            logger.error(f"[{request_id}] Problematic LLM response: {response}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to parse response from LLM",
                    "details": str(e),
                    "response": response
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        # Catch and log any unexpected errors
        error_trace = traceback.format_exc()
        logger.error(f"[{request_id}] Unexpected error processing request: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "details": str(e)
            }
        )
