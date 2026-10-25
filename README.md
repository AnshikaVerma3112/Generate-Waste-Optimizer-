# Waste Collection Route Optimizer — Local Edition

The latest Collection Journal scrapbook interface (public site version 10), with a working Python routing backend. All artwork and fonts are included locally. This academic prototype uses a **fictional 25-junction road network**, not live GPS navigation.

## Start on Windows

1. Extract the entire ZIP. Do not run files inside the ZIP.
2. Install **Python 3.10 or newer** if needed.
3. Open the extracted `Waste-Route-Optimizer` folder in VS Code.
4. Open Terminal → New Terminal and run:

```powershell
py -3 run.py
```

If `py` is unavailable, use `python run.py`. You can also double-click `start-windows.bat`.

5. Open **http://127.0.0.1:8000** in your browser.
6. Keep the terminal running. Press Ctrl+C there to stop.

No npm install, pip install, database, API key or .env file is required.

## macOS / Linux

```bash
python3 run.py
# Alternatively:
sh start-macos-linux.sh
```

## Port already in use?

```powershell
py -3 run.py --port 8001
```

Open http://127.0.0.1:8001 instead. Do not open index.html directly or use VS Code Live Server: the interface needs the Python API. One Python process serves both folders, so no separate frontend server or CORS configuration is needed. You can also invoke run.py by absolute path from another working directory.

## Files

| Location | Purpose |
|---|---|
| frontend/index.html | Screens, dialogs, SDG information and user guide |
| frontend/style.css | Scrapbook styling and responsive layout |
| frontend/app.js | Map, interactions, Python API requests and CSV import/export |
| frontend/solver.js | Browser validation helper; final route requests always use Python |
| frontend/assets/ | Original illustrations and local fonts |
| backend/server.py | Local HTTP server and API |
| backend/solver.py | Python validation, Dijkstra and Held-Karp |
| backend/data/graph.json | Canonical road data shared through the API |
| backend/requirements.txt | Documents that no third-party dependencies are needed |
| tests/test_app.py | Algorithm, API and validation tests |
| run.py | Application entry point |
| start-windows.bat | Windows convenience launcher |
| start-macos-linux.sh | macOS/Linux convenience launcher |
| .gitignore | Excludes caches, environments, editor settings and secrets |

## Using the app

1. Click **Plan a collection route**.
2. **Clear map** removes pickups and closures, keeping truck settings.
3. Tap + on the map to add pickups. Tap a selected place to remove it.
4. Type exact waste amounts or use ±10 kg. Truck settings include ±100 kg and presets.
5. Click **Find shortest route**. Compare the original and optimized orders and distances.
6. Arrows show direction. Use **Follow the trip** to inspect one leg when roads overlap.
7. Choose **Download stop list → Save CSV file**. If saving is blocked, use Copy CSV and save the text as collection-route.csv.
8. Use Back, Home or Change my places to navigate. SDG 11 + 13 and How to use open information panels.
9. More options includes CSV import and manual road closures. Recalculate after changes.

The browser remembers your plan when local storage is available. No shared database is used. Copy link copies a localhost address: it works only on a computer running this app. Share the ZIP or the public website, not localhost, with friends.

## Reproduce the presentation result

Use Collection yard as depot, capacity 500 kg, and all roads open. Add stops in this exact order:

| Node | Place | Waste |
|---|---|---|
| 0 | Market | 65 kg |
| 24 | Gardens | 80 kg |
| 4 | Bus stop | 50 kg |
| 20 | Apartments | 95 kg |
| 8 | School | 45 kg |

Expected: **335 kg; 13.80 km original; 8.40 km optimized; 5.40 km / 39.1% saved.** Equal-cost tours can have different visit orders. Capacity 300 kg must show an overload error.

## CSV import format

Save this text as a UTF-8 .csv file:

```csv
node,name,kg
0,Market,65
24,Gardens,80
4,Bus stop,50
20,Apartments,95
8,School,45
```

Import accepts 1–10 unique node IDs from 0–24, excluding the depot. It replaces current pickups after validation. IDs belong to the fictional network; they are not addresses or coordinates. Export uses different columns: sequence,node,name,kg,leg_km,road_path. An exported sheet cannot be reimported unchanged.

## Backend workflow

The frontend loads GET /api/graph and sends plans to POST /api/optimize. Python validates input and capacity, excludes closed roads, uses Dijkstra for road paths, and Held-Karp for an exact shortest tour through 1–10 pickups, including the depot return. Results include both the entered and optimized orders, distances and route legs. GET /api/health returns server status.

Example JSON request (Content-Type: application/json):

```json
{"depot":"12","capacity":500,"closed":[],"stops":[{"node":"0","name":"Market","kg":65}]}
```

The model uses fixed kilometre distances and two-way roads. The truck starts empty, picks up waste and does not unload during the round. Total waste must fit its capacity. Infeasible plans are rejected; it does not split trips or drop pickups. Road segments may repeat. Passing a stop early does not count as its scheduled collection.

The exact Held-Karp recurrence grows approximately as O(n² 2ⁿ), with extra overhead from copying partial routes in this implementation. The 10-stop limit keeps this small prototype responsive.

## Run tests

From the project root:

```powershell
py -3 -m unittest discover -s tests -v
```

Use python3 instead of py -3 on Linux/macOS. Tests create an isolated temporary localhost server, verify the known example, check a small optimum against every order, test invalid requests and confirm assets load. No test packages are needed.

## Troubleshooting

- Python not recognized: install Python with its launcher/PATH option and reopen the terminal.
- Port occupied: use --port 8001 and open the matching address.
- Backend unavailable: keep the run.py terminal open; use its printed URL.
- Old plan: click Clear map.
- No download: calculate a valid route first, then use Download stop list and Save CSV. Copy CSV is the fallback.
- Over capacity: choose a genuinely larger vehicle or fewer pickups for this round. Reordering cannot reduce waste mass.
- Unreachable pickup: reopen roads or change stops.
- Offline: the interface, assets and calculation work locally. Outbound UN website links need internet.

## Anything to add separately?

**Required:** Python 3.10+ and a modern browser. Nothing else is required for this local prototype.

**Future work, not included:** real road/GPS data, live traffic, vehicle restrictions, multiple vehicles, unloading trips, shared database and authentication, public production hosting, or measured fuel/emissions reporting. The OSMnx/NetworkX/OR-Tools/Streamlit/Folium stack in the PPT describes a proposed real-road extension and is not required here.

The server binds only to 127.0.0.1. It is for local academic use, not public production deployment. Backend files are not served by the frontend handler.

Original interface: version 10, source revision 5c84abc862c9ad5fcb1dc9abab7e70430a68dd3b.
Team: Anshika Verma, Meet Shinde, Sanskar Hande and Chandni Yadav, DBIT IT.
