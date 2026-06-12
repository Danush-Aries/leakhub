"""
APIs.guru scraper — fetches the public APIs.guru catalogue and stores entries
in the local database.

APIs.guru exposes a free JSON catalogue at:
    https://api.apis.guru/v2/list.json

Each key is a provider name; each value contains API versions with OpenAPI
spec URLs, base URLs, and descriptions.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

import httpx
from sqlmodel import Session, select

from ..db.models import API, DiscoverySource, Endpoint, Provider

logger = logging.getLogger("leakhub.scrapers.apis_guru")

APIS_GURU_URL = "https://api.apis.guru/v2/list.json"


def _get_or_create_source(session: Session) -> DiscoverySource:
    source = session.exec(
        select(DiscoverySource).where(DiscoverySource.name == "apis.guru")
    ).first()
    if not source:
        source = DiscoverySource(name="apis.guru", source_url=APIS_GURU_URL)
        session.add(source)
        session.commit()
        session.refresh(source)
    return source


def _get_or_create_provider(session: Session, name: str) -> Provider:
    provider = session.exec(
        select(Provider).where(Provider.name == name)
    ).first()
    if not provider:
        provider = Provider(name=name)
        session.add(provider)
        session.commit()
        session.refresh(provider)
    return provider


def scrape_apis_guru(session: Session) -> int:
    """
    Fetch the APIs.guru catalogue and upsert API records.
    Returns the number of APIs processed.
    """
    logger.info("Starting APIs.guru scrape...")
    source = _get_or_create_source(session)

    try:
        response = httpx.get(APIS_GURU_URL, timeout=30.0)
        response.raise_for_status()
        catalogue: Dict[str, Any] = response.json()
    except Exception as exc:
        logger.error("Failed to fetch APIs.guru catalogue: %s", exc)
        return 0

    count = 0
    for provider_name, api_data in catalogue.items():
        try:
            provider = _get_or_create_provider(session, provider_name)
            versions: Dict[str, Any] = api_data.get("versions", {})

            # Pick the preferred or latest version
            preferred = api_data.get("preferred", "")
            version_key = preferred if preferred in versions else (list(versions.keys())[-1] if versions else None)
            if not version_key:
                continue

            version_info = versions[version_key]
            info = version_info.get("info", {})
            name = info.get("title", provider_name)
            description = info.get("description", "")
            base_url = version_info.get("swaggerUrl", "") or version_info.get("openapiVer", "")
            spec_url = version_info.get("swaggerUrl", "")

            # Upsert: skip if already stored
            existing = session.exec(
                select(API).where(API.name == name).where(API.provider_id == provider.id)
            ).first()
            if existing:
                continue

            api = API(
                name=name,
                description=description[:500] if description else None,
                base_url=base_url or None,
                openapi_spec_url=spec_url or None,
                version=version_key,
                provider_id=provider.id,
                source_id=source.id,
            )
            session.add(api)
            session.commit()
            session.refresh(api)
            count += 1

        except Exception as exc:
            logger.warning("Error processing provider '%s': %s", provider_name, exc)
            session.rollback()
            continue

    # Update last_scanned timestamp
    source.last_scanned = datetime.utcnow()
    session.add(source)
    session.commit()

    logger.info("APIs.guru scrape complete: %d new APIs stored.", count)
    return count
