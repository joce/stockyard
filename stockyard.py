# TODO provide an OK docstring for this currently embryonic utility for displaying stock quotes

from appui import StockyardApp, StockyardAppState
from yfin import YFin

app_state: StockyardAppState = StockyardAppState(YFin())
app = StockyardApp(app_state)
app.run()
