# RapidKL MCP Server

Lightweight FastMCP-based server that exposes RapidKL (MYRAPID) station and fare data via MCP tools/resources.

## Features
- Tool: `get_fare(frm: str, to: str)` — return fare details between two station identifiers.
- Tool: `get_stations(input: str)` — search stations by place/station name and return formatted results.
- Resource: `get_all_stations()` — fetches the full stations payload and returns a human-readable listing of routes and stops.

## Requirements
- Python 3.10+
- Packages:
  - httpx
  - mcp

Install:
```powershell
python -m pip install httpx mcp
```

## Behavior / Implementation notes
- The service queries the MYRAPID geoservice:
  `https://jp.mapit.myrapid.com.my/endpoint/geoservice`
- HTTP requests performed by `make_myrapid_request(url)` return parsed JSON (or `None` on error).
- `get_all_stations()` now:
  - Accepts the endpoint response whether already parsed (dict) or returned as a JSON string.
  - Validates the top-level structure (expects `success`, `message`, `data`).
  - Iterates routes in `data` and formats each route and its stops into a readable multi-line string.
  - Skips empty placeholder stop objects often present in the source JSON.
  - Normalizes accessibility (`isOKU`) values (boolean/int/string) into "Accessible"/"Not Accessible".
  - Shows coordinates, stop id/name, and a trip count (if `trip_list` present).
  - Returns clear error messages when the endpoint response is missing or malformed.

## Example output (truncated)
```
Route: MRT Putrajaya Line (PYL, MRT)
--------------------------------------------------
  Stop: KWASA DAMANSARA (ID: PY01)
    Coordinates: (3.1763324, 101.5721456)
    Accessibility: Accessible
    Trips known: 0

  Stop: KAMPUNG SELAMAT (ID: PY03)
    Coordinates: (3.197266, 101.578499)
    Accessibility: Not Accessible
    Trips known: N/A

...
```

## Running (Windows)
Run server from repository root:
```powershell
python c:\Dev\RapidKL_MCP\server.py
```
The script runs the FastMCP server via `mcp.run(transport='stdio')`. Use an MCP-compatible client to interact.

## Troubleshooting
- If the MYRAPID API changes structure, update parsing in `get_all_stations()` and `get_stations()`.
- Network errors or non-JSON responses cause the handlers to return descriptive error strings.
- Code uses Python 3.10+ union syntax (`dict[str, Any] | None`).

## Contributing
Improve parsing robustness, add unit tests, or extend formatting for additional fields returned by the API.
```// filepath: c:\Dev\RapidKL_MCP\README.md
# RapidKL MCP Server

Lightweight FastMCP-based server that exposes RapidKL (MYRAPID) station and fare data via MCP tools/resources.

## Features
- Tool: `get_fare(frm: str, to: str)` — return fare details between two station identifiers.
- Tool: `get_stations(input: str)` — search stations by place/station name and return formatted results.
- Resource: `get_all_stations()` — fetches the full stations payload and returns a human-readable listing of routes and stops.

## Requirements
- Python 3.10+
- Packages:
  - httpx
  - mcp

Install:
```powershell
python -m pip install httpx mcp
```

## Behavior / Implementation notes
- The service queries the MYRAPID geoservice:
  `https://jp.mapit.myrapid.com.my/endpoint/geoservice`
- HTTP requests performed by `make_myrapid_request(url)` return parsed JSON (or `None` on error).
- `get_all_stations()` now:
  - Accepts the endpoint response whether already parsed (dict) or returned as a JSON string.
  - Validates the top-level structure (expects `success`, `message`, `data`).
  - Iterates routes in `data` and formats each route and its stops into a readable multi-line string.
  - Skips empty placeholder stop objects often present in the source JSON.
  - Normalizes accessibility (`isOKU`) values (boolean/int/string) into "Accessible"/"Not Accessible".
  - Shows coordinates, stop id/name, and a trip count (if `trip_list` present).
  - Returns clear error messages when the endpoint response is missing or malformed.

## Example output (truncated)
```
Route: MRT Putrajaya Line (PYL, MRT)
--------------------------------------------------
  Stop: KWASA DAMANSARA (ID: PY01)
    Coordinates: (3.1763324, 101.5721456)
    Accessibility: Accessible
    Trips known: 0

  Stop: KAMPUNG SELAMAT (ID: PY03)
    Coordinates: (3.197266, 101.578499)
    Accessibility: Not Accessible
    Trips known: N/A

...
```

## Running (Windows)
Run server from repository root:
```powershell
python c:\Dev\RapidKL_MCP\server.py
```
The script runs the FastMCP server via `mcp.run(transport='stdio')`. Use an MCP-compatible client to interact.

## Troubleshooting
- If the MYRAPID API changes structure, update parsing in `get_all_stations()` and `get_stations()`.
- Network errors or non-JSON responses cause the handlers to return descriptive error strings.
- Code uses Python 3.10+ union syntax (`dict[str, Any] | None`).

## Contributing
Improve parsing robustness, add unit tests, or extend formatting for additional fields returned by the API.