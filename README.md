# RapidKL MCP Server

FastMCP-based MCP service exposing RapidKL (MYRAPID) geoservice endpoints for fares, station search, journey planning and a full stations resource.

## Features
- Tool: `get_fare(frm: str, to: str)`  
  Returns fares between two station identifiers (adult, cash, cashless, concession, standard).
- Tool: `get_stations(input: str)`  
  Search stations by place or station name; returns formatted name, id, category and coordinates.
- Tool: `get_journey_planner(from_long: float, from_lat: float, to_long: float, to_lat: float, mode: str, journey_type: str, departure_datetime: str)`  
  Request journey plans between coordinates. Accepts departure time as `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`.
- Resource: `get_all_stations()`  
  Fetches full stations payload and returns a human-readable listing of routes and stops (skips empty placeholders).

## Requirements
- Python 3.10+
- Packages:
  - httpx
  - mcp

Install:
```powershell
python -m pip install httpx mcp
```

## Endpoints used
Base MYRAPID geoservice:
`https://jp.mapit.myrapid.com.my/endpoint/geoservice`

Common endpoints used by the service:
- `/geocode` — used by `get_stations`
- `/fares` — used by `get_fare`
- `/journeyPlanner` — used by `get_journey_planner`
- `/stations` — used by `get_all_stations`

## Running (Windows)
From repository root:
```powershell
python c:\Dev\RapidKL_MCP\server.py
```
The script runs the FastMCP server with `mcp.run(transport='stdio')`. Use an MCP-compatible client to call tools/resources.

## Usage notes
- `make_myrapid_request(url)` performs HTTP GET requests with a 30s timeout and returns parsed JSON (or `None` on error).
- Handlers accept responses already parsed as dicts or as JSON strings and attempt to normalize them.
- `get_all_stations()` details:
  - Validates top-level structure (`success`, `message`, `data`).
  - Formats each route and its stops to a readable multi-line string.
  - Skips empty placeholder objects often present in `stops`.
  - Normalizes accessibility (`isOKU`) into "Accessible"/"Not Accessible".
  - Shows stop id, name, coordinates and trip count if available.

## Example outputs (truncated)

get_fare:
```
Adult Fare: $2.40
Cash Fare: $2.40
Cashless Fare: $2.00
Concession Fare: $1.20
Standard Fare: $2.40
```

get_stations:
```
Station Name: Bandar Utama
Station ID: poi_12345
Category: MRT
Coordinates: (3.142857, 101.606666)
Latitude : 3.142857
Longitude: 101.606666
```

get_all_stations (route excerpt):
```
Route: MRT Putrajaya Line (PYL, MRT)
--------------------------------------------------
  Stop: KWASA DAMANSARA (ID: PY01)
    Coordinates: (3.1763324, 101.5721456)
    Accessibility: Accessible
    Trips known: 0
```

get_journey_planner (route summary excerpt):
```
Journey from (3.142857, 101.606666) to (3.076, 101.607)
Departure: 2025-10-27 08:00:00

Route 1:
  Estimated Arrival: 2025-10-27 09:00:00
  Total Duration: 3600 seconds (60.0 minutes)
  Fare (Adult/Cash/Cashless/Concession): RM2.4/RM2.4/RM2.0/RM1.2
  Legs:
    Leg 1 (Transit):
      Route: MRT Putrajaya Line (PYL)
      Departure: 2025-10-27 08:05:00
      Arrival: 2025-10-27 08:45:00
      Stops:
        - Station A (ID: S123)
        - Station B (ID: S124)
```

## Error handling & logging
- Handlers return descriptive error strings on network, parsing or API errors.
- `get_stations` and `get_journey_planner` configure `logging` at `DEBUG` level for runtime diagnostics.

## Development notes
- The code uses Python 3.10+ union type syntax (`dict[str, Any] | None`).
- Add tests to validate parsing of edge cases: missing fields, malformed coordinates, alternative boolean encodings for `isOKU`, placeholder stop objects.
- When the MYRAPID API changes structure, update parsing logic in the corresponding handlers.

## Contributing
- Improve parsing robustness, add unit tests, or expand formatting to include additional fields returned by the API.