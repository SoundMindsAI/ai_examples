"""
MCP Weather Alerts Server
========================

This module implements a Model Context Protocol (MCP) server that provides
weather alerts from the National Weather Service API.

Table of Contents:
-----------------
Step 1: Import Dependencies
Step 2: Environment Setup
Step 3: MCP Server Initialization
Step 4: Constants Definition
Step 5: NWS API Request Function
Step 6: Alert Formatting Function
Step 7: Weather Alerts Tool Implementation
Step 8: Echo Resource Implementation
Step 9: Server Initialization Confirmation
"""

# Step 1: Import Dependencies
# --------------------------
# Import necessary libraries for HTTP requests, environment variables,
# type hints, and MCP functionality
from typing import Any
import httpx
import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Step 2: Environment Setup
# -----------------------
# Load environment variables from .env file and print debug information
# to help with troubleshooting
load_dotenv()

# Print debug information
print(f"Python version: {sys.version}")
print(f"Model provider: {os.getenv('MODEL_PROVIDER', 'openai')}")
print(f"OPENAI_API_KEY set: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

# Step 3: MCP Server Initialization
# -------------------------------
# Initialize the FastMCP server with a configurable model provider
# The model provider can be set using the MODEL_PROVIDER environment variable
model_provider = os.getenv("MODEL_PROVIDER", "openai")
try:
    mcp = FastMCP("weather", model_provider=model_provider)
    print(f"Successfully initialized FastMCP with provider: {model_provider}")
except Exception as e:
    print(f"Error initializing FastMCP: {e}")
    raise

# Step 4: Constants Definition
# --------------------------
# Define constants for the National Weather Service API
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Step 5: NWS API Request Function
# ------------------------------
# Function to make HTTP requests to the National Weather Service API
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API.
    
    Args:
        url (str): The full URL to the NWS API endpoint
        
    Returns:
        dict[str, Any] | None: The JSON response as a dictionary, or None if the request failed
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error making request to {url}: {e}")
            return None

# Step 6: Alert Formatting Function
# -------------------------------
# Function to format a weather alert into a human-readable string
def format_alert(feature: dict[str, Any]) -> str:
    """Format a weather alert feature into a human-readable string.
    
    Args:
        feature (dict[str, Any]): A feature object from the NWS API response
        
    Returns:
        str: A formatted string containing the alert details
    """
    properties = feature["properties"]
    return f"""
        Event:  {properties.get('event', 'Unknown')}
        Area:   {properties.get('areaDescription', 'Unknown')}
        Severity: {properties.get('severity', 'Unknown')}
        Description: {properties.get('description', 'No description available')}
        Instructions: {properties.get('instruction', 'No instructions available')}
    """

# Step 7: Weather Alerts Tool Implementation
# ---------------------------------------
# Implement the get_alerts tool using the MCP tool decorator
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state.
    
    This function fetches active weather alerts from the National Weather Service
    for the specified state and formats them into a human-readable string.
    
    Args:
        state (str): Two letter state code (e.g., 'CA', 'NY', 'TX')
    
    Returns:
        str: A formatted string of weather alerts, or a message indicating no alerts
             were found or an error occurred.
    """
    print(f"Fetching alerts for state: {state}")
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found for the specified state."
    
    if not data["features"]:
        return "No active alerts found for the specified state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# Step 8: Echo Resource Implementation
# ---------------------------------
# Implement a simple echo resource for testing purposes
@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource.
    
    This is a simple resource that echoes back the provided message.
    It's useful for testing the MCP resource functionality.
    
    Args:
        message (str): The message to echo
        
    Returns:
        str: The echoed message
    """
    print(f"Echo resource called with message: {message}")
    return f"Resource echo: {message}"

# Step 9: Server Initialization Confirmation
# ---------------------------------------
# Print a confirmation message that the server is ready to handle requests
print("Weather MCP server initialized and ready to handle requests")
