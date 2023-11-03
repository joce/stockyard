"""Main entry point for the application."""

import os.path

from appui import StockyardApp

home_dir: str = os.path.expanduser("~")
config_file: str = os.path.join(home_dir, ".stockyard")

app: StockyardApp = StockyardApp()
app.load_config(config_file)
app.run()
app.save_config(config_file)
