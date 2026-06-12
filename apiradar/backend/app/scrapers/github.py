"""
GitHub code-search scraper — searches public repositories for OpenAPI/Swagger
spec files and stores discovered APIs in the local database.

Uses the GitHub REST Search API (unauthenticated: 10 req/min; with token: 30 req/min).
Set GITHUB_TOKEN env var to a personal access token to raise the rate limit.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlmodel import Session, select

from ..db.models import API, DiscoverySource, Endpoint, Provider

logger = logging.getLogger("leakhub.scrapers.github")

GITHUB_SEARCH_URL = "https://api.github.com/search/code"
RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/{full_name}/{default_branch}/{path}"


def _headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github.v3+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get_or_create_source(session: Session) -> DiscoverySource:
    source = session.exec(
        select(DiscoverySource).where(DiscoverySource.name == "github")
    ).first()
    if not source:
        source = DiscoverySource(name="github", source_url=GITHUB_SEARCH_URL)
        session.add(source)
        session.commit()
        session.refresh(source)
    return source


def _get_or_create_provider(session: Session, name: str, url: Optional[str] = None) -> Provider:
    provider = session.exec(select(Provider).where(Provider.name == name)).first()
    if not provider:
        provider = Provider(name=name, url=url)
        session.add(provider)
        session.commit()
        session.refresh(provider)
    return provider


def _extract_endpoints_from_spec(spec: Dict[str, Any]) -> List[Dict[str, str]]:
    """Parse OpenAPI 2/3 spec and extract path + method pairs."""
    endpoints: List[Dict[str, str]] = []
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            op = methods.get(method)
            if op and isinstance(op, dict):
                endpoints.append(
                    {
                        "path": path,
                        "method": method.upper(),
                        "description": op.get("summary", op.get("description", "")),
                    }
                )
    return endpoints


def scrape_github(session: Session, query: str = "openapi swagger filename:openapi.json") -> int:
    """
    Search GitHub for OpenAPI spec files matching *query* and store findings.
    Returns the number of new APIs stored.
    """
    logger.info("Starting GitHub scrape with query: '%s'", query)
    source = _get_or_create_source(session)

    params = {
        "q": query + " extension:json extension:yaml",
        "per_page": 30,
        "page": 1,
    }

    try:
        resp = httpx.get(GITHUB_SEARCH_URL, headers=_headers(), params=params, timeout=20.0)
        if resp.status_code == 403:
            logger.warning("GitHub rate limit hit. Set GITHUB_TOKEN to increase limits.")
            return 0
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.error("GitHub search request failed: %s", exc)
        return 0

    items: List[Dict[str, Any]] = data.get("items", [])
    count = 0

    for item in items:
        try:
            repo = item.get("repository", {})
            repo_name = repo.get("full_name", "unknown/unknown")
            html_url = item.get("html_url", "")
            file_path = item.get("path", "")

            # Build raw URL for downloading the spec
            default_branch = repo.get("default_branch", "main")
            raw_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}/{file_path}"

            raw_resp = httpx.get(raw_url, headers=_headers(), timeout=10.0)
            if raw_resp.status_code != 200:
                continue

            # Try to parse as JSON or YAML
            try:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    import yaml  # optional dep
                    spec = yaml.safe_load(raw_resp.text)
                else:
                    spec = raw_resp.json()
            except Exception:
                continue

            if not isinstance(spec, dict):
                continue

            info = spec.get("info", {})
            api_name = info.get("title", repo_name)
            description = info.get("description", "")
            version = info.get("version", "")

            # Derive a base URL
            servers = spec.get("servers", [])
            base_url = servers[0].get("url", "") if servers else spec.get("host", "")

            provider = _get_or_create_provider(session, repo_name, html_url)

            existing = session.exec(
                select(API).where(API.name == api_name).where(API.openapi_spec_url == raw_url)
            ).first()
            if existing:
                continue

            api = API(
                name=api_name,
                description=description[:500] if description else None,
                base_url=str(base_url) if base_url else None,
                openapi_spec_url=raw_url,
                version=str(version) if version else None,
                provider_id=provider.id,
                source_id=source.id,
            )
            session.add(api)
            session.commit()
            session.refresh(api)

            # Store endpoints
            for ep_data in _extract_endpoints_from_spec(spec):
                ep = Endpoint(
                    api_id=api.id,
                    path=ep_data["path"],
                    method=ep_data["method"],
                    description=ep_data.get("description", ""),
                )
                session.add(ep)
            session.commit()
            count += 1

        except Exception as exc:
            logger.warning("Error processing GitHub item: %s", exc)
            session.rollback()
            continue

    source.last_scanned = datetime.utcnow()
    session.add(source)
    session.commit()

    logger.info("GitHub scrape complete: %d new APIs stored.", count)
    return count
