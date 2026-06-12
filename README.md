# LeakHub — APIRadar

![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![Textual](https://img.shields.io/badge/TUI-Textual-8A2BE2)
![License](https://img.shields.io/badge/license-MIT-green)

**LeakHub APIRadar** is an intelligence tool for discovering exposed API endpoints across the web. It scrapes public sources — [APIs.guru](https://apis.guru) and GitHub — to catalogue APIs, parse their OpenAPI specs, and index every endpoint they expose. Results are stored in a local SQLite database and browsable through both a REST API and an interactive terminal UI.

---

## What It Does

1. **Scrapes** APIs.guru (2,500+ public APIs) and GitHub (OpenAPI/Swagger files) on demand.
2. **Parses** OpenAPI 2 and 3 specs to extract every path and HTTP method.
3. **Stores** providers, APIs, and endpoints in a local SQLite database (swappable for PostgreSQL).
4. **Serves** a FastAPI REST layer with search, pagination, and background scrape triggers.
5. **Displays** results in a Textual terminal UI with a live search screen and a dashboard showing backend health and scrape source status.

---

## Features

- Full FastAPI backend with `/apis`, `/endpoints`, `/providers`, `/scrape/*` routes
- Background scrape jobs (APIs.guru + GitHub code search)
- SQLModel ORM with automatic schema creation — no migrations needed to get started
- Textual TUI: Dashboard screen (backend health, source status) + Search screen (real-time API lookup)
- Portable config — no hardcoded paths
- `.env` support via `python-dotenv`
- Docker-ready (`Dockerfile.backend` + `docker-compose.yml`)
- Test suite with in-memory SQLite (no external services required)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI, Uvicorn |
| ORM / DB | SQLModel, SQLite (default) |
| HTTP client | httpx |
| TUI | Textual |
| Config | python-dotenv, configparser |
| Containerisation | Docker, Docker Compose |
| Tests | pytest, FastAPI TestClient |

---

## Installation

### 1. Clone and set up

```bash
git clone https://github.com/your-org/leakhub.git
cd leakhub
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set GITHUB_TOKEN for higher GitHub rate limits (optional)
```

### 3. Start the backend

```bash
python main.py backend
# or:  uvicorn apiradar.backend.app.api.main:app --reload
```

The API is now live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Usage

### Run a scrape

```bash
# One-shot APIs.guru scrape from the CLI
python main.py scrape

# Or trigger via the REST API (runs in the background)
curl -X POST http://localhost:8000/scrape/apis-guru
curl -X POST "http://localhost:8000/scrape/github?query=openapi+swagger"
```

### Search APIs

```bash
# List all indexed APIs
curl http://localhost:8000/apis

# Search by name/description
curl "http://localhost:8000/apis?search=stripe&limit=10"

# Get a specific API with its endpoints
curl http://localhost:8000/apis/1

# Search endpoints by path
curl "http://localhost:8000/endpoints?path=/payments&method=POST"
```

### Launch the TUI

```bash
# Backend must be running first
python main.py tui
```

**TUI keybindings:**

| Key | Action |
|-----|--------|
| `d` | Switch to Dashboard |
| `s` | Switch to Search |
| `Ctrl+R` | Refresh current screen |
| `Escape` | Go back |
| `q` | Quit |

### Docker

```bash
cd apiradar/devops
docker compose up --build
```

---

## Project Structure

```
leakhub/
├── main.py                         # Root entry point (backend / tui / scrape)
├── requirements.txt
├── .env.example
├── Makefile
├── tests/
│   └── test_api.py                 # Pytest integration tests
└── apiradar/
    ├── backend/
    │   └── app/
    │       ├── api/main.py         # FastAPI application
    │       ├── db/models.py        # SQLModel schema (API, Endpoint, Provider, DiscoverySource)
    │       ├── core/database.py    # Engine setup and session factory
    │       └── scrapers/
    │           ├── apis_guru.py    # APIs.guru catalogue scraper
    │           └── github.py       # GitHub code-search scraper
    ├── tui/
    │   └── src/
    │       ├── app.py              # Textual App + keybindings
    │       └── screens/
    │           ├── dashboard.py    # Backend health + source status
    │           └── search_screen.py # Live API search
    ├── devops/
    │   ├── Dockerfile.backend
    │   └── docker-compose.yml
    ├── shared/
    │   └── types.py                # Shared dataclasses
    └── project_config.ini
```

---

## Running Tests

```bash
pytest tests/ -v
# or via Make
make test
```

Tests use an in-memory SQLite database — no running server or network access required.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./leakhub.db` | SQLAlchemy database URL |
| `GITHUB_TOKEN` | _(empty)_ | GitHub PAT — raises rate limit from 10 to 30 req/min |
| `BACKEND_HOST` | `0.0.0.0` | Uvicorn bind address |
| `BACKEND_PORT` | `8000` | Uvicorn port |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
