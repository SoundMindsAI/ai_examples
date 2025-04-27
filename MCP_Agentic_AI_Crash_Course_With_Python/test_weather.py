"""
MCP Weather Alerts Test Script
=============================

This script provides a direct way to test the weather alerts functionality
without going through the MCP Inspector or API endpoints. It imports and
directly calls the get_alerts function from the weather module.

Usage:
    python test_weather.py

The script will test weather alerts for two states (California and New York)
and print the results to the console.
"""

import asyncio
from server.weather import get_alerts

async def test_weather_alerts():
    """Test the weather alerts functionality.
    
    This function tests the get_alerts function by retrieving weather
    alerts for California (CA) and New York (NY). It demonstrates how
    to call the function directly without going through the MCP server.
    
    The function prints the results to the console, showing any active
    weather alerts for the specified states.
    """
    print("Testing weather alerts for California...")
    result = await get_alerts("CA")
    print("\nResults:")
    print(result)
    
    print("\n\nTesting weather alerts for New York...")
    result = await get_alerts("NY")
    print("\nResults:")
    print(result)

if __name__ == "__main__":
    # Run the test function using asyncio
    asyncio.run(test_weather_alerts())
