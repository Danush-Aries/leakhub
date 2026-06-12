"""
Dashboard screen — shows system health and scraper source status fetched
from the backend. Falls back to showing connection error if the server
is not running.
"""
from __future__ import annotations

import httpx
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Label, Static

BACKEND_URL = "http://localhost:8000"


class DashboardScreen(Screen):
    """Main dashboard: backend health + discovery source status."""

    BINDINGS = [
        ("ctrl+r", "refresh", "Refresh"),
        ("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    DashboardScreen {
        layout: vertical;
    }
    #title {
        text-align: center;
        padding: 1;
        text-style: bold;
        color: $accent;
    }
    #section-health, #section-sources {
        margin: 0 2;
        text-style: bold;
    }
    DataTable {
        margin: 0 2 1 2;
    }
    #status-bar {
        height: 2;
        margin: 0 2;
        color: $warning;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("LeakHub APIRadar — Dashboard", id="title")
        yield Static("Backend Health", id="section-health")
        yield DataTable(id="health-table")
        yield Static("Discovery Sources", id="section-sources")
        yield DataTable(id="sources-table")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        health_table = self.query_one("#health-table", DataTable)
        health_table.add_columns("Check", "Result")

        sources_table = self.query_one("#sources-table", DataTable)
        sources_table.add_columns("Source", "URL", "Last Scanned")

        self._refresh_data()

    def _refresh_data(self) -> None:
        self._load_health()
        self._load_sources()

    def _load_health(self) -> None:
        table = self.query_one("#health-table", DataTable)
        table.clear()
        status = self.query_one("#status-bar", Static)

        try:
            resp = httpx.get(f"{BACKEND_URL}/health", timeout=4.0)
            data = resp.json()
            table.add_row("Backend API", "UP")
            table.add_row("Version", data.get("version", "?"))
            table.add_row("Timestamp", data.get("timestamp", "?"))

            dep_resp = httpx.get(f"{BACKEND_URL}/dependencies", timeout=6.0)
            for key, val in dep_resp.json().items():
                table.add_row(key, val)

            status.update("")
        except httpx.ConnectError:
            table.add_row("Backend API", "OFFLINE")
            status.update("Start backend: cd apiradar/backend && uvicorn app.api.main:app --reload")
        except Exception as exc:
            table.add_row("Error", str(exc)[:60])

    def _load_sources(self) -> None:
        table = self.query_one("#sources-table", DataTable)
        table.clear()

        try:
            resp = httpx.get(f"{BACKEND_URL}/scrape/sources", timeout=4.0)
            resp.raise_for_status()
            for src in resp.json():
                last = src.get("last_scanned") or "Never"
                table.add_row(src.get("name", "?"), src.get("source_url", "?")[:50], last[:19])
        except httpx.ConnectError:
            table.add_row("—", "Backend offline", "—")
        except Exception as exc:
            table.add_row("Error", str(exc)[:60], "—")

    def action_refresh(self) -> None:
        self._refresh_data()
