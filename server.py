from typing import Optional
import httpx
import json
import logging
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("rapidkl")

# Constants
MYRAPID_API_BASE = "https://jp.mapit.myrapid.com.my/endpoint/geoservice"
USER_AGENT = "mcp"
SCOPE = "WMcentral"
AGENCY = "rapidkl"

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

@mcp.tool()
async def get_stations(input: str) -> str:
    """Get station information based on a search input.

    Args:
        input: The search input which typically can be a place name or a station name e.g. Bandar Utama
    Returns:
        str: Formatted string containing station information or error message
    """
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # URL-encode the input string to handle spaces and special characters
    encoded_input = quote(input.strip(), safe='')
    #https://jp.mapit.myrapid.com.my/endpoint/geoservice/geocode?scope=WMcentral&agency=rapidkl&input=Bandar%20Utama
    url = f"{MYRAPID_API_BASE}/geocode?scope={SCOPE}&agency={AGENCY}&input={encoded_input}"
    
    try:
        logger.debug(f"Making request to URL: {url}")
        raw = await make_myrapid_request(url)
        
        if not raw:
            logger.error("No response received from API")
            return "Unable to fetch station data for this input."

        logger.debug(f"Raw API response: {raw}")

        # Validate response structure
        if not isinstance(raw, dict):
            logger.error(f"Invalid response type: {type(raw)}")
            return "Error: Invalid response format from API"

        if "results" not in raw:
            message = raw.get('message', 'No results field in response')
            logger.error(f"No 'results' in response: {message}")
            return f"Error: {message}"

        stations = raw.get("results", [])
        if not stations:
            logger.info("No stations found in response")
            return encoded_input + " No stations found matching the input."

        # Format station information
        station_lines = []
        for station in stations:
            # Safely extract station data with defaults
            name = station.get('poiname', 'N/A')
            station_id = station.get('poi_id', 'N/A')
            category = station.get('category', 'N/A')
            coordinates = station.get('geometry', {}).get('coordinates', ['N/A', 'N/A'])
            
            # Ensure coordinates are valid
            try:
                lon, lat = float(coordinates[0]), float(coordinates[1])
                coord_str = f"({lat:.6f}, {lon:.6f})"
            except (ValueError, TypeError, IndexError):
                logger.warning(f"Invalid coordinates for station {name}: {coordinates}")
                coord_str = "(N/A, N/A)"

            station_lines.extend([
                f"Station Name: {name}",
                f"Station ID: {station_id}",
                f"Category: {category}",
                f"Coordinates: {coord_str}",
                f"Latitude : {lat}",
                f"Longitude: {lon}",
                ""  # Blank line between stations
            ])

        return "\n".join(station_lines)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return "Error: Invalid JSON response from API"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error processing station data: {str(e)}" 

@mcp.tool()
async def get_journey_planner(from_long: float, from_lat: float,
                              to_long: float, to_lat: float, 
                              mode: str, journey_type: str, departure_datetime: str) -> str:
    """Get journey plan using journey planner based on coordinates and other parameters.

    Args:
        from_long: Starting longitude.
        from_lat: Starting latitude.
        to_long: Destination longitude.
        to_lat: Destination latitude.
        mode: Travel mode (e.g., 'mix', 'transit', 'walking').
        journey_type: Type of journey (e.g., 'fastest', 'leastchange').
        departure_datetime: Departure time in 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD' format.
    
    Returns:
        str: Formatted string containing journey plan.
    """
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    try:
        # Normalize departure datetime
        try:
            datetime.strptime(departure_datetime, "%Y-%m-%d %H:%M:%S")
            newdatetime = departure_datetime  # Already has time, return as is
        except ValueError:
            try:
                datetime.strptime(departure_datetime, "%Y-%m-%d")
                newdatetime = f"{departure_datetime} 00:00:00"  # Append time
            except ValueError:
                logger.error(f"Invalid datetime format: {departure_datetime}")
                raise ValueError("Input must be in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format")

        # URL-encode the datetime string
        encoded_datetime = quote(newdatetime.strip(), safe='')

        # Construct the API URL
        url = (f"{MYRAPID_API_BASE}/journeyPlanner?agency={AGENCY}&"
               f"flng={from_long}&flat={from_lat}&tlng={to_long}&tlat={to_lat}&"
               f"mode={mode}&type={journey_type}&departure_datetime={encoded_datetime}")

        try:
            logger.debug(f"Making request to URL: {url}")
            raw = await make_myrapid_request(url)
            
            if not raw:
                logger.error("No response received from API")
                return "Unable to fetch journey data for this input."

            logger.debug(f"Raw API response: {raw}")

            # Parse the JSON response
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {str(e)}")
                    return "Error: Invalid JSON response from API"

            # Check API response status
            if raw.get("status") != "OK":
                logger.error(f"API error: {raw.get('message', 'Unknown error')}")
                return f"Error in response: {raw.get('message', 'Unknown error')}"

            # Parse the journey planner response
            result = f"Journey from ({from_lat}, {from_long}) to ({to_lat}, {to_long})\n"
            result += f"Departure: {raw['departure_time']}\n\n"

            for idx, route in enumerate(raw["routes"], 1):
                result += f"Route {idx}:\n"
                result += f"  Estimated Arrival: {route['estimated_arrival_time']}\n"
                result += f"  Total Duration: {route['total_duration']} seconds ({route['total_duration'] / 60:.1f} minutes)\n"
                result += f"  Total Distance: {route.get('total_distance', 'N/A')} meters\n"
                fare = route["alt_fare_price"]
                result += f"  Fare (Adult/Cash/Cashless/Concession): RM{fare['adult']}/RM{fare['cash']}/RM{fare['cashless']}/RM{fare['consession']}\n"
                
                result += "  Legs:\n"
                for leg_idx, leg in enumerate(route["legs"], 1):
                    leg_type = leg["type"]
                    result += f"    Leg {leg_idx} ({leg_type.capitalize()}):\n"
                    result += f"      Duration: {leg['duration']} seconds\n"
                    result += f"      Distance: {leg.get('distance', 'N/A')} meters\n"
                    if leg_type == "transit":
                        rd = leg["route_details"]
                        result += f"      Route: {rd['route_long_name']} ({rd.get('route_short_name', '')})\n"
                        result += f"      Headsign: {rd.get('headsign', 'N/A')}\n"  # Handle missing headsign
                        result += f"      Departure: {leg['estimated_departure_time']}\n"
                        result += f"      Arrival: {leg['estimated_end_arrival_time']}\n"
                        result += "      Stops:\n"
                        for stop in leg["steps"]:
                            result += f"        - {stop['stop_name']} (ID: {stop['stop_id']})\n"
                    elif leg_type == "pedestrain":  # Note: API uses 'pedestrain' typo
                        result += "      Walking distance.\n"
                
                result += "\n"

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return "Error: Invalid JSON response from API"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Error: Unexpected issue occurred - {str(e)}"

    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return str(e)

# Resources - provide all stations info
@mcp.resource("https://jp.mapit.myrapid.com.my/endpoint/geoservice/stations")
async def get_all_stations() -> str:
    """
    Resource for all stations

    Returns:
        All the stations categorized by different routes (route_id). Each route
        will have sets of stations
    """
    url = f"{MYRAPID_API_BASE}/stations"
    raw = await make_myrapid_request(url)

    if not raw:
        return "Error: Unable to fetch stations data."

    # Accept either a dict (usual case) or a JSON string
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return "Error: Received invalid JSON from stations endpoint."

    if not isinstance(data, dict):
        return "Error: Unexpected response format from stations endpoint."

    if not data.get("success", False):
        return f"Error: {data.get('message', 'Failed to fetch stations')}"

    routes = data.get("data", []) or []
    if not routes:
        return "No routes found."

    output_lines: list[str] = []
    for route in routes:
        route_id = route.get("route_id") or "Unknown"
        route_name = route.get("route_long_name") or route.get("route_short_name") or "Unknown Route"
        route_category = route.get("category") or "Unknown Category"

        output_lines.append(f"Route: {route_name} ({route_id}, {route_category})")
        output_lines.append("-" * 50)

        stops = route.get("stops") or []
        if not stops:
            output_lines.append("  No stops available")
            output_lines.append("")  # blank line between routes
            continue

        for stop in stops:
            # skip empty placeholder objects often present in the source JSON
            if not isinstance(stop, dict) or not stop:
                continue

            stop_name = stop.get("stop_name") or "Unknown Stop"
            stop_id = stop.get("stop_id") or "N/A"

            # isOKU may be a string or a boolean
            is_oku_raw = stop.get("isOKU")
            if isinstance(is_oku_raw, bool):
                is_oku = is_oku_raw
            elif isinstance(is_oku_raw, (int, float)):
                is_oku = bool(is_oku_raw)
            else:
                is_oku = str(is_oku_raw).strip().lower() in {"true", "1", "yes"}

            stop_lat = stop.get("stop_lat") or "N/A"
            stop_lon = stop.get("stop_lon") or "N/A"

            # additional info: trip_list length if available
            trip_list = stop.get("trip_list", []) or []
            trip_count = len(trip_list) if isinstance(trip_list, list) else "N/A"

            oku_status = "Accessible" if is_oku else "Not Accessible"
            output_lines.append(f"  Stop: {stop_name} (ID: {stop_id})")
            output_lines.append(f"    Coordinates: ({stop_lat}, {stop_lon})")
            output_lines.append(f"    Accessibility: {oku_status}")
            output_lines.append(f"    Trips known: {trip_count}")
            output_lines.append("")  # blank line between stops

        output_lines.append("")  # blank line between routes

    return "\n".join(output_lines)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')