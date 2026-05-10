from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer
from .screens.dashboard import DashboardScreen
from .screens.search_screen import SearchScreen

class APIRadarApp(App):
    TITLE = "APIRadar TUI"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "switch_dashboard", "Dashboard"),
        ("s", "switch_search", "Search"),
    ]

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

    def action_switch_dashboard(self) -> None:
        self.push_screen(DashboardScreen())

    def action_switch_search(self) -> None:
        self.push_screen(SearchScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

if __name__ == "__main__":
    app = APIRadarApp()
    app.run()
