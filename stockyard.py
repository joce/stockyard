# TODO provide an OK docstring for this currently embryonic utility for displaying stock quotes

from appui import StockyardApp, StockyardAppState
from yfinance import YFinance

app_state: StockyardAppState = StockyardAppState(YFinance())
app = StockyardApp(app_state)
app.run()
