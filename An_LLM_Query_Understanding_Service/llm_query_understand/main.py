from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter
import json
import os
import traceback
from typing import Dict, Any
from pydantic import BaseModel

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
You are a helpful assistant. You will be given a search query and you need to parse furniture searches it into a structured format. The structured format should include the following fields:

    - item_type - the core thing the user wants (sofa, table, chair, etc.)
    - material - the material of the item (wood, metal, plastic, etc.)
    - color - the color of the item (red, blue, green, etc.)

    Respond with a single line of JSON:

        {"item_type": "sofa", "material": "wood", "color": "red"}

    Omit any other information. Do not include any other text in your response. Omit a value if the user did not specify it. For example, if the user said "red sofa", you would respond with:

        {"item_type": "sofa", "color": "red"}

Here is the search query: 
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
            parsed_query_as_json = response.split("\n")[-1].strip()
            logger.debug(f"[{request_id}] Extracted JSON: {parsed_query_as_json}")
            
            parsed_query = json.loads(parsed_query_as_json)
            logger.info(f"[{request_id}] Successfully parsed query into JSON: {parsed_query}")
            
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
