# TODO provide an OK docstring for this currently embryonic utility for displaying stock quotes

from yfin import YFin, YQuote

yfin: YFin = YFin()

quotes: list[YQuote] = yfin.get_quotes(["MSFT", "AAPL"])

for q in quotes:
    print(q)
