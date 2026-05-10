from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Label, DataTable

class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("System Health & Scraper Status", id="title")

        # System Health Section
        yield Static("--- System Health ---", id="section-header")
        yield DataTable(id="health-table")

        # Scraper Status Section
        yield Static("--- Scraper Status ---", id="section-header")
        yield DataTable(id="scraper-table")

        yield Footer()

    def on_mount(self) -> None:
        # Mock data for health table
        health_table = self.query_one("#health-table", DataTable)
        health_table.add_columns("Metric", "Status", "Value")
        health_table.add_row("CPU Usage", "OK", "12%")
        health_table.add_row("Memory", "OK", "450MB")
        health_table.add_row("Disk I/O", "Warning", "High")

        # Mock data for scraper table
        scraper_table = self.query_one("#scraper-table", DataTable)
        scraper_table.add_columns("Scraper Name", "State", "Last Run")
        scraper_table.add_row("Google API", "Running", "2m ago")
        scraper_table.add_row("Twitter API", "Idle", "1h ago")
        scraper_table.add_row("Reddit API", "Error", "10m ago")

# CSS would typically be in a separate file or as a string,
# but for this implemention we will stick to the logic.
