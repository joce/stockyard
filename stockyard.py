"""Main entry point for the application."""

import os.path

from appui import StockyardApp, StockyardAppState
from yfinance import YFinance

home_dir: str = os.path.expanduser("~")
config_file: str = os.path.join(home_dir, ".stockyard")

app_state: StockyardAppState = StockyardAppState(YFinance())
app: StockyardApp = StockyardApp(app_state)
app.load_config(config_file)
app.run()
app.save_config(config_file)
