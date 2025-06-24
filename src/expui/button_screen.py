from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button


class ButtonScreen(Screen[int]):
    """A screen with a button."""

    def compose(self) -> ComposeResult:
        """Compose the screen with a button."""
        yield Button(label="One", id="one")
        yield Button(label="Two", id="two")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        print("Button was pressed!")
