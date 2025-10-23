from typing import Any
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("rapidkl")

# Constants
MYRAPID_API_BASE = "https://jp.mapit.myrapid.com.my/endpoint/geoservice"
USER_AGENT = "mcp"

async def make_myrapid_request(url: str) -> dict[str, Any] | None:
    """Make a request to the MYRAPID API with proper error handling."""
    headers = {
        "Accept": "application/json, text/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_fare(frm: str, to: str) -> str:
    """Get the ticket fares for a train journey from a start station to a destination station.

    Args:
        from: the start station location (can only be stop_id or poi_id)
        to: the destination station location (can only be stop_id or poi_id)
    """
    url = f"{MYRAPID_API_BASE}/fares?agency=rapidkl&from={frm}&to={to}"
    data = await make_myrapid_request(url)

    if not data:
        return "Unable to fetch forecast data for this location."

    try:
        # Parse the JSON data
        fare_data = json.loads(data) if isinstance(data, str) else data

        # Check if 'fares' key exists in the response
        if "fares" not in fare_data:
            return "Invalid fare data received from the API."

        fares = fare_data["fares"]
        
        # Format the fare information
        fare_lines = [
            f"Adult Fare: ${fares.get('adult', 'N/A')}",
            f"Cash Fare: ${fares.get('cash', 'N/A')}",
            f"Cashless Fare: ${fares.get('cashless', 'N/A')}",
            f"Concession Fare: ${fares.get('consession', 'N/A')}",
            f"Standard Fare: ${fares.get('fare', 'N/A')}"
        ]
        
        return "\n".join(fare_lines)
    
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return f"Error processing fare data: {str(e)}"

# Resources - provide all stations info
@mcp.resource("https://jp.mapit.myrapid.com.my/endpoint/geoservice/stations")
async def get_all_stations() -> str:
    """
    Resource for all stations

    Returns:
        All the stations categorized by different routes (route_id). Each route
        will have sets of stations
    """
    # Fetch the data explicitly using make_myrapid_request
    url = f"{MYRAPID_API_BASE}/stations"
    data = await make_myrapid_request(url)

    # Check if the request was successful and extract data
    if not data.get('success', False):
        return f"Error: {data.get('message', 'Failed to fetch stations')}"

    # Initialize output list for formatted text
    output = []

    # Iterate through each route in the data
    for route in data.get('data', []):
        route_id = route.get('route_id', 'Unknown')
        route_name = route.get('route_long_name', 'Unknown Route')
        route_category = route.get('category', 'Unknown Category')
        
        # Add route header
        output.append(f"Route: {route_name} ({route_id}, {route_category})")
        output.append("-" * 50)
        
        # Iterate through stops in the route
        for stop in route.get('stops', []):
            stop_name = stop.get('stop_name', 'Unknown Stop')
            stop_id = stop.get('stop_id', 'N/A')
            is_oku = stop.get('isOKU', 'false').lower() == 'true'
            stop_lat = stop.get('stop_lat', 'N/A')
            stop_lon = stop.get('stop_lon', 'N/A')
            
            # Format stop details
            oku_status = "Accessible" if is_oku else "Not Accessible"
            output.append(f"  Stop: {stop_name} (ID: {stop_id})")
            output.append(f"    Coordinates: ({stop_lat}, {stop_lon})")
            output.append(f"    Accessibility: {oku_status}")
            output.append("")  # Blank line for readability
        
        output.append("")  # Blank line between routes

    # Join the output lines into a single string
    return "\n".join(output)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')