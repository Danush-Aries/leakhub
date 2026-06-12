"""
Search screen — lets the user search for APIs in the LeakHub catalogue
by querying the local backend REST API.
"""
from __future__ import annotations

import httpx
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, DataTable, Label, Static
from textual.containers import Vertical, Horizontal
from textual import on

BACKEND_URL = "http://localhost:8000"


class SearchScreen(Screen):
    """Interactive API search screen backed by the FastAPI service."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+r", "refresh", "Refresh"),
    ]

    CSS = """
    SearchScreen {
        layout: vertical;
    }
    #search-bar {
        height: 3;
        margin: 1 2;
    }
    #results-label {
        margin: 0 2;
        color: $text-muted;
    }
    #results-table {
        margin: 0 2;
        height: 1fr;
    }
    #status {
        height: 2;
        margin: 0 2;
        color: $warning;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Input(placeholder="Search APIs by name or description...", id="search-bar")
            yield Label("Results will appear below. Press Enter to search.", id="results-label")
            yield Static("", id="status")
            yield DataTable(id="results-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("ID", "Name", "Version", "Base URL", "Description")
        self._load_all()

    def _load_all(self) -> None:
        self._do_search("")

    @on(Input.Submitted, "#search-bar")
    def on_search_submit(self, event: Input.Submitted) -> None:
        self._do_search(event.value.strip())

    def _do_search(self, query: str) -> None:
        table = self.query_one("#results-table", DataTable)
        status = self.query_one("#status", Static)
        table.clear()

        params: dict = {"limit": 100}
        if query:
            params["search"] = query

        try:
            resp = httpx.get(f"{BACKEND_URL}/apis", params=params, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            for item in results:
                table.add_row(
                    str(item.get("id", "")),
                    item.get("name", "")[:40],
                    item.get("version", "") or "",
                    (item.get("base_url", "") or "")[:50],
                    (item.get("description", "") or "")[:60],
                )
            count = len(results)
            label = self.query_one("#results-label", Label)
            label.update(f"{count} result(s) for '{query}'" if query else f"{count} total APIs indexed.")
            status.update("")
        except httpx.ConnectError:
            status.update("Backend unreachable — start the server with: uvicorn app.api.main:app")
        except Exception as exc:
            status.update(f"Error: {exc}")

    def action_refresh(self) -> None:
        query = self.query_one("#search-bar", Input).value.strip()
        self._do_search(query)
