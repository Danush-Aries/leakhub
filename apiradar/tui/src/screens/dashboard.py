from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Label, DataTable
import httpx
from textual import work

class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("System Health & Scraper Status", id="title")

        # System Health Section
        yield Static("--- System Health ---", id="health-section-header")
        yield DataTable(id="health-table")

        # Scraper Status Section
        yield Static("--- Scraper Status ---", id="scraper-section-header")
        yield DataTable(id="scraper-table")

        yield Footer()

    def on_mount(self) -> None:
        health_table = self.query_one("#health-table", DataTable)
        health_table.add_columns("Metric", "Status", "Value")

        scraper_table = self.query_one("#scraper-table", DataTable)
        scraper_table.add_columns("Scraper Name", "State", "Last Run")

        self.update_data()

    @work(exclusive=True)
    async def update_data(self) -> None:
        async with httpx.AsyncClient() as client:
            try:
                # Fetch health status
                health_response = await client.get("http://127.0.0.1:8000/status/health")
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    health_table = self.query_one("#health-table", DataTable)
                    health_table.clear()
                    for item in health_data:
                        health_table.add_row(item["metric"], item["status"], item["value"])
            except Exception as e:
                health_table = self.query_one("#health-table", DataTable)
                health_table.clear()
                health_table.add_row("Backend", "Error", "Unreachable")

            try:
                # Fetch scraper status
                scraper_response = await client.get("http://127.0.0.1:8000/status/scrapers")
                if scraper_response.status_code == 200:
                    scraper_data = scraper_response.json()
                    scraper_table = self.query_one("#scraper-table", DataTable)
                    scraper_table.clear()
                    for item in scraper_data:
                        scraper_table.add_row(item["name"], item["state"], item["last_run"])
            except Exception as e:
                scraper_table = self.query_one("#scraper-table", DataTable)
                scraper_table.clear()
                scraper_table.add_row("Backend", "Error", "Unreachable")
