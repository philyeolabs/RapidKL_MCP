# RapidKL MCP Server

Lightweight FastMCP-based server that exposes RapidKL (MYRAPID) station and fare data via MCP tools/resources.

## Contents
- `server.py` — main MCP service implementation
  - Tool: `get_fare(frm: str, to: str)` — return fare details between two station identifiers
  - Resource: `get_all_stations()` — returns a readable listing of all routes and their stops

## Requirements
- Python 3.10+
- Packages:
  - httpx
  - mcp (the FastMCP framework used by this project)

Install dependencies:
```bash
python -m pip install httpx mcp
```

## Running (Windows)
Run the MCP server from the repository root:
```powershell
python c:\Dev\RapidKL_MCP\server.py
```
The server starts via `mcp.run(transport='stdio')` (stdio transport). Use your MCP client or the FastMCP-compatible runner to communicate with the service.

## Behavior
- The server queries the MYRAPID geoservice endpoint:
  `https://jp.mapit.myrapid.com.my/endpoint/geoservice`
- `make_myrapid_request(url)` performs an HTTP GET with a short timeout and returns parsed JSON or `None` on error.
- `get_fare(frm, to)` fetches fares for a journey and returns a short multi-line string (adult/cash/cashless/concession/standard).
- `get_all_stations()` fetches the stations payload (same structure as `allstations.json`) and returns a human-readable string:
  - Lists each route by name, id and category
  - Lists stops with ID, coordinates, accessibility (isOKU) and trip count
  - Skips empty placeholder entries included in the source JSON

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
    Accessibility: Accessible
    Trips known: 0

...
```

## Notes & Troubleshooting
- The code expects the MYRAPID endpoint to return a JSON object with top-level keys: `success`, `message`, and `data` (where `data` is a list of routes). If the endpoint changes, the parsing logic in `get_all_stations()` must be updated.
- The project uses Python 3.10+ union type syntax (`dict[str, Any] | None`).
- If responses return placeholder empty objects in the `stops` arrays, `get_all_stations()` will skip them.

## Contributing
- Add tests or improve parsing robustness for additional edge cases (e.g., missing fields, alternative boolean encodings for `isOKU`).
- When updating dependencies, ensure compatibility with Python 3.10+.

```// filepath: c:\Dev\RapidKL_MCP\README.md
# RapidKL MCP Server

Lightweight FastMCP-based server that exposes RapidKL (MYRAPID) station and fare data via MCP tools/resources.

## Contents
- `server.py` — main MCP service implementation
  - Tool: `get_fare(frm: str, to: str)` — return fare details between two station identifiers
  - Resource: `get_all_stations()` — returns a readable listing of all routes and their stops

## Requirements
- Python 3.10+
- Packages:
  - httpx
  - mcp (the FastMCP framework used by this project)

Install dependencies:
```bash
python -m pip install httpx mcp
```

## Running (Windows)
Run the MCP server from the repository root:
```powershell
python c:\Dev\RapidKL_MCP\server.py
```
The server starts via `mcp.run(transport='stdio')` (stdio transport). Use your MCP client or the FastMCP-compatible runner to communicate with the service.

## Behavior
- The server queries the MYRAPID geoservice endpoint:
  `https://jp.mapit.myrapid.com.my/endpoint/geoservice`
- `make_myrapid_request(url)` performs an HTTP GET with a short timeout and returns parsed JSON or `None` on error.
- `get_fare(frm, to)` fetches fares for a journey and returns a short multi-line string (adult/cash/cashless/concession/standard).
- `get_all_stations()` fetches the stations payload (same structure as `allstations.json`) and returns a human-readable string:
  - Lists each route by name, id and category
  - Lists stops with ID, coordinates, accessibility (isOKU) and trip count
  - Skips empty placeholder entries included in the source JSON

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
    Accessibility: Accessible
    Trips known: 0

...
```

## Notes & Troubleshooting
- The code expects the MYRAPID endpoint to return a JSON object with top-level keys: `success`, `message`, and `data` (where `data` is a list of routes). If the endpoint changes, the parsing logic in `get_all_stations()` must be updated.
- The project uses Python 3.10+ union type syntax (`dict[str, Any] | None`).
- If responses return placeholder empty objects in the `stops` arrays, `get_all_stations()` will skip them.

## Contributing
- Add tests or improve parsing robustness for additional edge cases (e.g., missing fields, alternative boolean encodings for `isOKU`).
- When updating dependencies, ensure compatibility with Python 3.10+.
