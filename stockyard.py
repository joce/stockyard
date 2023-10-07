from appui import StockyardApp, StockyardAppState
from yfinance import YFinance

app_state: StockyardAppState = StockyardAppState(YFinance())
app = StockyardApp(app_state)
app.run()
