#!/usr/bin/env python3
"""
LeakHub APIRadar — root entry point.

Usage:
  python main.py backend     Start the FastAPI backend (default port 8000)
  python main.py tui         Launch the Textual TUI
  python main.py scrape      Run a one-shot APIs.guru scrape and exit
"""
from __future__ import annotations

import sys
import os

# Ensure the project root is on PYTHONPATH so sub-packages resolve correctly.
sys.path.insert(0, os.path.dirname(__file__))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def run_backend() -> None:
    import uvicorn
    uvicorn.run(
        "apiradar.backend.app.api.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
    )


def run_tui() -> None:
    from apiradar.tui.src.app import APIRadarApp
    app = APIRadarApp()
    app.run()


def run_scrape() -> None:
    from apiradar.backend.app.core.database import init_db, get_session
    from apiradar.backend.app.scrapers.apis_guru import scrape_apis_guru

    init_db()
    session = get_session()
    try:
        count = scrape_apis_guru(session)
        print(f"Scrape complete. {count} new APIs stored.")
    finally:
        session.close()


COMMANDS = {
    "backend": run_backend,
    "tui": run_tui,
    "scrape": run_scrape,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backend"
    if cmd not in COMMANDS:
        print(f"Unknown command '{cmd}'. Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()
