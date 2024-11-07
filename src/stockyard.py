"""Main entry point for the application."""

from pathlib import Path

from appui import StockyardApp

home_dir: Path = Path("~").expanduser()
config_file_name: str = (home_dir / ".stockyard").as_posix()

app: StockyardApp = StockyardApp()
app.load_config(config_file_name)
app.run()
app.save_config(config_file_name)
