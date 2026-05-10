from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, DataTable

class SearchScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search for APIs...", id="search-input")
        yield DataTable(id="search-results")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#search-results", DataTable)
        table.add_columns("API Name", "Provider", "Endpoints")
