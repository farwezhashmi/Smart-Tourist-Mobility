# Smart Tourist Mobility

Smart Tourist Mobility is a Hyderabad-first tourist mobility intelligence and decision-support platform for Smart India Hackathon 2026, Problem Statement 26204.

It helps a tourist compare fair fares and multimodal travel options without replacing booking, navigation, or public transport systems.

## Phase 1 status

The first runnable vertical slice is implemented:

- React + Vite + TypeScript + Tailwind frontend
- FastAPI backend with SQLAlchemy and PostgreSQL/PostGIS configuration
- Initial `locations` and `transport_modes` SQLAlchemy models
- Hyderabad tourism location and transport-mode seed data
- Docker Compose services for database, backend, and frontend
- Live `GET /api/health` endpoint that queries PostgreSQL
- Homepage that calls FastAPI and displays the live database counts

The fare, routing, anomaly, and recommendation features remain intentionally out of scope for this phase.

## Target MVP scenario

- City: Hyderabad
- Source: Secunderabad Railway Station
- Destination: Charminar
- Passengers: 3
- Preference: Budget
- Walking tolerance: Low
- Demonstration flow: fare range, route comparison, recommendation explanation, quoted fare alert, simulated traffic re-optimization

## Repository layout

```text
smart-tourist-mobility/
├── frontend/              # React + TypeScript tourist and admin experiences
├── backend/               # FastAPI application and service layer
├── ml/                    # Feature engineering, training, evaluation, artifacts
├── database/              # PostgreSQL/PostGIS migrations and seed data
├── data/                  # Versioned schemas, samples, and ingestion outputs
├── notebooks/             # Exploratory and model evaluation notebooks
├── docs/                  # Architecture and project contracts
├── tests/                 # Backend, ML, optimizer, and frontend test suites
├── docker/                # Container-specific configuration
├── .env.example           # Non-secret configuration template
└── docker-compose.yml     # Local multi-service environment
```

## Current documents

- [Phase 1 foundation](docs/phase-1-foundation.md)
- [Database schema](database/schema.sql)
- [API specification](docs/api-specification.md)
- [Dataset schema](docs/dataset-schema.md)
- [Team and delivery plan](docs/team-plan.md)

## Data and honesty rules

- Hyderabad is the only MVP city.
- Every fare observation records its provenance: official, public, team-collected, or synthetic demo.
- Synthetic/demo values are never described as government or real-time data.
- ML reports contain only metrics produced by reproducible experiments.
- External routing providers are adapters; optimization remains an internal service.
- Secrets belong in environment variables, never in source control.

## Proposed branch model

- `main`: reviewed, demo-ready code
- `develop`: integration branch
- `feature/<area>-<short-name>`: member work branches
- `release/<version>`: hackathon rehearsal or submission stabilization

Pull requests target `develop`, require one reviewer, and include tests or a documented reason why tests do not apply.

## Run locally without Docker

The default development configuration uses a real local SQLite database, so Docker and PostgreSQL are not required for the Phase 1 demo.

```powershell
python -m pip install -r backend/requirements.txt
npm install --prefix frontend
npm run dev
```

In a second terminal, start the backend:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

The backend automatically creates `smart_tourist_mobility.db` and seeds Hyderabad locations and transport modes. Open `http://localhost:5173` and verify the live connection card.

## Run the full PostgreSQL/PostGIS stack with Docker

Prerequisite: Docker Desktop with Compose support.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open `http://localhost:5173` for the frontend or `http://localhost:8000/docs` for the FastAPI docs. The homepage is healthy only when the API can query PostgreSQL and return the seeded location and transport-mode counts.

To stop the stack:

```powershell
docker compose down
```

To remove the local database volume and reseed from scratch:

```powershell
docker compose down -v
docker compose up --build
```

## Run with an existing PostgreSQL installation

Install PostgreSQL with PostGIS, create the database/user described in `.env.example`, set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL, and apply the schema and seed files. In PowerShell, `psql` uses its own connection arguments:

```powershell
$env:PGPASSWORD = "change_me"
psql -h localhost -U stm_user -d smart_tourist_mobility -f database/schema.sql
psql -h localhost -U stm_user -d smart_tourist_mobility -f database/seed.sql
python -m pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

The Vite development proxy forwards `/api` to `http://localhost:8000` by default. In Compose it is configured to use the `backend` service name.

## Checks

```powershell
python -m compileall backend/app backend/tests
python -m pytest backend/tests -q
Set-Location frontend
npm run build
```

## Start the frontend correctly

Do not use the VS Code Live Server/Go Live button for this React app; it serves folders as static files and can show a directory listing. From the repository root, run:

```powershell
npm run dev
```

Then open `http://localhost:5173`. You can also run `npm run dev` inside the `frontend` directory. Use `npm run build` from the root to create the production bundle.
