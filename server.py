from typing import Any
import httpx
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

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')