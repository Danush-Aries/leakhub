"""
LeakHub / APIRadar — FastAPI backend
Provides REST endpoints for API discovery, scraping, and endpoint cataloguing.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from ..core.database import init_db, get_session
from ..db.models import API, Endpoint, Provider, DiscoverySource
from ..scrapers.apis_guru import scrape_apis_guru
from ..scrapers.github import scrape_github

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leakhub")

app = FastAPI(
    title="LeakHub APIRadar",
    description="AI-powered intelligence tool for discovering exposed API endpoints.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("Database initialised.")


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ping", tags=["system"])
async def ping():
    """Quick heartbeat."""
    return {"message": "pong"}


@app.get("/dependencies", tags=["system"])
async def check_dependencies():
    """Check connectivity to external dependencies."""
    results: dict = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in [
            ("github_api", "https://api.github.com"),
            ("apis_guru", "https://api.apis.guru/v2/list.json"),
        ]:
            try:
                resp = await client.get(url)
                results[name] = "reachable" if resp.status_code < 400 else f"error_{resp.status_code}"
            except Exception as exc:
                results[name] = f"unreachable: {exc}"
    return results


# ---------------------------------------------------------------------------
# Provider endpoints
# ---------------------------------------------------------------------------

@app.get("/providers", response_model=List[dict], tags=["providers"])
def list_providers(session: Session = Depends(get_session)):
    providers = session.exec(select(Provider)).all()
    return [{"id": p.id, "name": p.name, "url": p.url, "description": p.description} for p in providers]


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/apis", tags=["apis"])
def list_apis(
    search: Optional[str] = Query(None, description="Filter by name or description"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    """List catalogued APIs with optional search."""
    stmt = select(API)
    if search:
        stmt = stmt.where(
            (API.name.contains(search)) | (API.description.contains(search))
        )
    stmt = stmt.offset(offset).limit(limit)
    apis = session.exec(stmt).all()
    return {
        "total": len(apis),
        "offset": offset,
        "limit": limit,
        "results": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "base_url": a.base_url,
                "version": a.version,
                "provider_id": a.provider_id,
                "created_at": a.created_at.isoformat(),
            }
            for a in apis
        ],
    }


@app.get("/apis/{api_id}", tags=["apis"])
def get_api(api_id: int, session: Session = Depends(get_session)):
    api = session.get(API, api_id)
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    endpoints = session.exec(select(Endpoint).where(Endpoint.api_id == api_id)).all()
    return {
        "id": api.id,
        "name": api.name,
        "description": api.description,
        "base_url": api.base_url,
        "openapi_spec_url": api.openapi_spec_url,
        "version": api.version,
        "endpoints": [
            {
                "id": e.id,
                "path": e.path,
                "method": e.method,
                "description": e.description,
            }
            for e in endpoints
        ],
    }


# ---------------------------------------------------------------------------
# Endpoint search
# ---------------------------------------------------------------------------

@app.get("/endpoints", tags=["endpoints"])
def search_endpoints(
    path: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    session: Session = Depends(get_session),
):
    stmt = select(Endpoint)
    if path:
        stmt = stmt.where(Endpoint.path.contains(path))
    if method:
        stmt = stmt.where(Endpoint.method == method.upper())
    stmt = stmt.limit(limit)
    endpoints = session.exec(stmt).all()
    return [
        {"id": e.id, "api_id": e.api_id, "path": e.path, "method": e.method, "description": e.description}
        for e in endpoints
    ]


# ---------------------------------------------------------------------------
# Scraper triggers
# ---------------------------------------------------------------------------

@app.post("/scrape/apis-guru", tags=["scrapers"])
async def trigger_apis_guru(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """Trigger an APIs.guru scrape run in the background."""
    background_tasks.add_task(scrape_apis_guru, session)
    return {"message": "APIs.guru scrape job queued."}


@app.post("/scrape/github", tags=["scrapers"])
async def trigger_github(
    background_tasks: BackgroundTasks,
    query: str = Query("openapi swagger", description="GitHub code search query"),
    session: Session = Depends(get_session),
):
    """Trigger a GitHub code-search scrape in the background."""
    background_tasks.add_task(scrape_github, session, query)
    return {"message": f"GitHub scrape queued for query: '{query}'."}


@app.get("/scrape/sources", tags=["scrapers"])
def list_sources(session: Session = Depends(get_session)):
    sources = session.exec(select(DiscoverySource)).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_url": s.source_url,
            "last_scanned": s.last_scanned.isoformat() if s.last_scanned else None,
        }
        for s in sources
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
