"""Provide structured access to financial market quotes from Yahoo! Finance."""

# ruff: noqa: PLR0904
# ruff: noqa: PLR0915

from __future__ import annotations

import sys
from datetime import date, datetime
from typing import Any

from .enums import MarketState, OptionType, PriceAlertConfidence, QuoteType

if sys.version_info >= (3, 11):
    from datetime import UTC as UTC_DT
    from zoneinfo import ZoneInfo

    UTC = UTC_DT
else:
    import pytz

    UTC = pytz.UTC


class YQuote:
    """Structured representation of financial market quote data from Yahoo! Finance."""

    @property
    def ask(self) -> float | None:
        """
        Lowest price a seller is willing to accept for the security.

        Note:
            Applies to CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION quotes.
        """

        return self._ask

    @property
    def ask_size(self) -> int | None:
        """
        Number of units available at current ask price.

        Note:
            Applies to CURRENCY, EQUITY, ETF and INDEX quotes.
        """

        return self._ask_size

    @property
    def average_analyst_rating(self) -> str | None:
        """
        Consensus rating from financial analysts for the stock.

        Note:
            Applies to EQUITY quotes.
        """

        return self._average_analyst_rating

    @property
    def average_daily_volume_10_day(self) -> int | None:
        """
        Average number of shares traded each day over the last 10 days.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._average_daily_volume_10_day

    @property
    def average_daily_volume_3_month(self) -> int | None:
        """
        Average number of shares traded each day over the last 3 months.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._average_daily_volume_3_month

    @property
    def bid(self) -> float | None:
        """
        Highest price a buyer is willing to pay for the security.

        Note:
            Applies to CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION quotes.
        """

        return self._bid

    @property
    def bid_size(self) -> int | None:
        """
        Total number of shares that buyers want to buy at the bid price.

        Note:
            Applies to CURRENCY, EQUITY, ETF and INDEX quotes.
        """

        return self._bid_size

    @property
    def book_value(self) -> float | None:
        """
        Net accounting value of a company's assets.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._book_value

    @property
    def circulating_supply(self) -> int | None:
        """
        Number of cryptocurrency units currently in public circulation.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._circulating_supply

    @property
    def coin_image_url(self) -> str | None:
        """
        URL of the image representing the cryptocurrency.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._coin_image_url

    @property
    def coin_market_cap_link(self) -> str | None:
        """
        URL of the MarketCap site for the cryptocurrency.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._coin_market_cap_link

    @property
    def contract_symbol(self) -> bool | None:
        """
        Ticker symbol for a futures contract.

        Note:
            Applies to FUTURE quotes.
        """

        return self._contract_symbol

    @property
    def crypto_tradeable(self) -> bool | None:
        """
        Whether the cryptocurrency can be traded.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._crypto_tradeable

    @property
    def currency(self) -> str:
        """
        Currency in which the security is traded.

        Note:
            Applies to ALL quotes.
        """

        return self._currency

    @property
    def custom_price_alert_confidence(self) -> PriceAlertConfidence:
        """
        Value whose meaning is not clear at the moment.

        Note:
            Seen values have been NONE, LOW and HIGH.
            Applies to ALL quotes.
        """

        return self._custom_price_alert_confidence

    @property
    def display_name(self) -> str | None:
        """
        User-friendly name of the stock or security.

        Note:
            Applies to EQUITY quotes.
        """

        return self._display_name

    @property
    def dividend_date(self) -> date | None:
        """
        Date when the company is expected to pay its next dividend.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._dividend_date

    @property
    def dividend_rate(self) -> float | None:
        """
        Amount of dividends that a company is expected to pay over the next year.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._dividend_rate

    @property
    def dividend_yield(self) -> float | None:
        """
        Annual dividend as a percentage of the security's current price.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._dividend_yield

    @property
    def earnings_datetime(self) -> datetime | None:
        """
        Date and time of the company's earnings announcement.

        Note:
            Applies to EQUITY quotes.
        """

        return self._earnings_datetime

    @property
    def earnings_datetime_end(self) -> datetime | None:
        """
        Date and time of the end of the company's earnings announcement.

        Note:
            Applies to EQUITY quotes.
        """

        return self._earnings_datetime_end

    @property
    def earnings_datetime_start(self) -> datetime | None:
        """
        Date and time of the start of the company's earnings announcement.

        Note:
            Applies to EQUITY quotes.
        """

        return self._earnings_datetime_start

    @property
    def eps_current_year(self) -> float | None:
        """
        Company's earnings per share (EPS) for the current year.

        Note:
            Applies to EQUITY quotes.
        """

        return self._eps_current_year

    @property
    def eps_forward(self) -> float | None:
        """
        Company's projected earnings per share (EPS) for the next fiscal year.

        Note:
            Applies to EQUITY quotes.
        """

        return self._eps_forward

    @property
    def eps_trailing_twelve_months(self) -> float | None:
        """
        Company's earnings per share (EPS) for the past 12 months.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._eps_trailing_twelve_months

    @property
    def esg_populated(self) -> bool:
        """
        Availability status of ESG ratings data.

        Note:
            Applies to ALL quotes.
        """

        return self._esg_populated

    @property
    def exchange(self) -> str:
        """
        Securities exchange on which the security is traded.

        Note:
            Applies to ALL quotes.
        """

        return self._exchange

    @property
    def exchange_data_delayed_by(self) -> int:
        """
        Delay in data from the exchange, typically in minutes.

        Note:
            Applies to ALL quotes.
        """

        return self._exchange_data_delayed_by

    @property
    def exchange_timezone_name(self) -> str:
        """
        Name of the timezone of the exchange.

        Note:
            Applies to ALL quotes.
        """

        return self._exchange_timezone_name

    @property
    def exchange_timezone_short_name(self) -> str:
        """
        Short name of the timezone of the exchange.

        Note:
            Applies to ALL quotes.
        """

        return self._exchange_timezone_short_name

    @property
    def expire_date(self) -> date | None:
        """
        Date on which the option contract expires.

        Note:
            Applies to OPTION quotes.
        """

        return self._expire_date

    @property
    def expire_iso_date(self) -> str | None:
        """
        Date on which the option contract expires, in ISO 8601 format.

        Note:
            Applies to OPTION quotes.
        """

        return self._expire_iso_date

    @property
    def fifty_day_average(self) -> float | None:
        """
        Average closing price of the stock over the past 50 trading days.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._fifty_day_average

    @property
    def fifty_day_average_change(self) -> float | None:
        """
        Change in the 50-day average price from the previous trading day.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._fifty_day_average_change

    @property
    def fifty_day_average_change_percent(self) -> float | None:
        """
        Percent change in the 50-day average price from the previous trading day.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._fifty_day_average_change_percent

    @property
    def fifty_two_week_change_percent(self) -> float | None:
        """
        Percentage change in price over the past 52 weeks.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._fifty_two_week_change_percent

    @property
    def fifty_two_week_high(self) -> float:
        """
        Highest price the stock has traded at in the past 52 weeks.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_high

    @property
    def fifty_two_week_high_change(self) -> float:
        """
        Change in the 52-week high price from the previous trading day.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_high_change

    @property
    def fifty_two_week_high_change_percent(self) -> float:
        """
        Percent change in the 52-week high price from the previous trading day.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_high_change_percent

    @property
    def fifty_two_week_low(self) -> float:
        """
        Lowest price the stock has traded at in the past 52 weeks.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_low

    @property
    def fifty_two_week_low_change(self) -> float:
        """
        Change in the 52-week low price from the previous trading day.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_low_change

    @property
    def fifty_two_week_low_change_percent(self) -> float:
        """
        Percent change in the 52-week low price from the previous trading day.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_low_change_percent

    @property
    def fifty_two_week_range(self) -> str:
        """
        Trading price range over the past 52 weeks.

        Note:
            Applies to ALL quotes.
        """

        return self._fifty_two_week_range

    @property
    def financial_currency(self) -> str | None:
        """
        Currency in which the company reports its financial results.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._financial_currency

    @property
    def first_trade_datetime(self) -> datetime:
        """
        Timestamp of the first trade of this security, in milliseconds.

        Note:
            Applies to ALL quotes.
        """

        return self._first_trade_datetime

    @property
    def forward_pe(self) -> float | None:
        """
        Projected price-to-earnings ratio for the next 12 months.

        Note:
            Applies to EQUITY quotes.
        """

        return self._forward_pe

    @property
    def from_currency(self) -> str | None:
        """
        Base currency in exchange pair.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._from_currency

    @property
    def full_exchange_name(self) -> str:
        """
        Full name of the securities exchange on which the security is traded.

        Note:
            Applies to ALL quotes.
        """

        return self._full_exchange_name

    @property
    def gmt_off_set_milliseconds(self) -> int:
        """
        Offset from GMT of the exchange, in milliseconds.

        Note:
            Applies to ALL quotes.
        """

        return self._gmt_off_set_milliseconds

    @property
    def head_symbol_as_string(self) -> str | None:
        """
        Symbol of the contract's underlying security.

        Note:
            Applies to OPTION quotes.
        """

        return self._head_symbol_as_string

    @property
    def ipo_expected_date(self) -> date | None:
        """
        Expected date of the initial public offering (IPO).

        Note:
            Applies to EQUITY quotes.
        """

        return self._ipo_expected_date

    @property
    def language(self) -> str:
        """
        Language in which financial results are reported.

        Note:
            Applies to ALL quotes.
        """

        return self._language

    @property
    def last_market(self) -> str | None:
        """
        Last market in which the security was traded.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._last_market

    @property
    def logo_url(self) -> str | None:
        """
        URL of the company's logo.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._logo_url

    @property
    def long_name(self) -> str | None:
        """
        Official name of the company.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, INDEX and MUTUALFUND
            quotes.
        """

        return self._long_name

    @property
    def market(self) -> str:
        """
        Primary market for the security.

        Note:
            Applies to ALL quotes.
        """

        return self._market

    @property
    def market_cap(self) -> int | None:
        """
        Total market value of the security in trading currency.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._market_cap

    @property
    def market_state(self) -> MarketState:
        """
        Current state of the market for a security.

        Note:
            Applies to ALL quotes.
        """

        return self._market_state

    @property
    def message_board_id(self) -> str | None:
        """
        Identifier for the Yahoo! Finance message board for this security.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, INDEX and MUTUALFUND
            quotes.
        """

        return self._message_board_id

    @property
    def name_change_date(self) -> date | None:
        """
        Date on which the company last changed its name.

        Note:
            Applies to EQUITY quotes.
        """

        return self._name_change_date

    @property
    def net_assets(self) -> float | None:
        """
        Total net assets of the company.

        Note:
            Applies to ETF and MUTUALFUND quotes.
        """

        return self._net_assets

    @property
    def net_expense_ratio(self) -> float | None:
        """
        Ratio of total expenses to total net assets.

        Note:
            Applies to ETF and MUTUALFUND quotes.
        """

        return self._net_expense_ratio

    @property
    def open_interest(self) -> int | None:
        """
        Total number of open contracts on a futures or options market.

        Note:
            Applies to FUTURE and OPTION quotes.
        """

        return self._open_interest

    @property
    def option_type(self) -> OptionType | None:
        """
        Type of option.

        Note:
            Applies to OPTION quotes.
        """

        return self._option_type

    @property
    def post_market_change(self) -> float | None:
        """
        Change in the security's price in post-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._post_market_change

    @property
    def post_market_change_percent(self) -> float | None:
        """
        Percent change in the security's price in post-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._post_market_change_percent

    @property
    def post_market_price(self) -> float | None:
        """
        Price of the security in post-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._post_market_price

    @property
    def post_market_datetime(self) -> datetime | None:
        """
        Time of the most recent post-market trade.

        Note:
            Applies to ALL quotes.
        """

        return self._post_market_datetime

    @property
    def pre_market_change(self) -> float | None:
        """
        Change in the security's price in pre-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._pre_market_change

    @property
    def pre_market_change_percent(self) -> float | None:
        """
        Percent change in the security's price in pre-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._pre_market_change_percent

    @property
    def pre_market_price(self) -> float | None:
        """
        Price of the security in pre-market trading.

        Note:
            Applies to ALL quotes.
        """

        return self._pre_market_price

    @property
    def pre_market_datetime(self) -> datetime | None:
        """
        Time of the most recent pre-market trade.

        Note:
            Applies to ALL quotes.
        """

        return self._pre_market_datetime

    @property
    def prev_name(self) -> str | None:
        """
        Name of the company prior to its most recent name change.

        Note:
            Applies to EQUITY quotes.
        """

        return self._prev_name

    @property
    def price_eps_current_year(self) -> float | None:
        """
        Current-year price-to-earnings ratio.

        Note:
            Applies to EQUITY quotes.
        """

        return self._price_eps_current_year

    @property
    def price_hint(self) -> int:
        """
        Decimal precision indicator for price values.

        Note:
            Applies to ALL quotes.
        """

        return self._price_hint

    @property
    def price_to_book(self) -> float | None:
        """
        Market value relative to book value per share.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._price_to_book

    @property
    def quote_source_name(self) -> str | None:
        """
        Name of the source providing the quote.

        Note:
            Applies to ALL quotes.
        """

        return self._quote_source_name

    @property
    def quote_type(self) -> QuoteType:
        """
        Type of quote.

        Note:
            Applies to ALL quotes.
        """

        return self._quote_type

    @property
    def region(self) -> str:
        """
        Region in which the company is located.

        Note:
            Applies to ALL quotes.
        """

        return self._region

    @property
    def regular_market_change(self) -> float:
        """
        Change in the security's price in regular trading.

        Note:
            Applies to ALL quotes.
        """

        return self._regular_market_change

    @property
    def regular_market_change_percent(self) -> float:
        """
        Percent change in the security's price in regular trading.

        Note:
            Applies to ALL quotes.
        """

        return self._regular_market_change_percent

    @property
    def regular_market_day_high(self) -> float | None:
        """
        Highest price during regular trading session.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
            quotes.
        """

        return self._regular_market_day_high

    @property
    def regular_market_day_low(self) -> float | None:
        """
        Lowest price during regular trading session.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
            quotes.
        """

        return self._regular_market_day_low

    @property
    def regular_market_day_range(self) -> str | None:
        """
        Price range during regular trading session.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
            quotes.
        """

        return self._regular_market_day_range

    @property
    def regular_market_open(self) -> float | None:
        """
        Opening price for regular trading session.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
            quotes.
        """
        return self._regular_market_open

    @property
    def regular_market_previous_close(self) -> float:
        """
        Closing price of the security in the previous regular trading session.

        Note:
            Applies to ALL quotes.
        """

        return self._regular_market_previous_close

    @property
    def regular_market_price(self) -> float:
        """
        Latest price from regular trading session.

        Note:
            Applies to ALL quotes.
        """

        return self._regular_market_price

    @property
    def regular_market_datetime(self) -> datetime:
        """
        Time of the most recent trade in the regular trading session.

        Note:
            Applies to ALL quotes.
        """

        return self._regular_market_datetime

    @property
    def regular_market_volume(self) -> int | None:
        """
        Number of units traded in regular session.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
            quotes.
        """

        return self._regular_market_volume

    @property
    def shares_outstanding(self) -> int | None:
        """
        Number of shares currently held by all shareholders.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._shares_outstanding

    @property
    def short_name(self) -> str:
        """
        Short, user-friendly name for the stock or security.

        Note:
            Applies to ALL quotes.
        """

        return self._short_name

    @property
    def source_interval(self) -> int:
        """
        Interval at which the data source provides updates, in seconds.

        Note:
            Applies to ALL quotes.
        """

        return self._source_interval

    @property
    def start_date(self) -> date | None:
        """
        Date on which the coin started trading.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._start_date

    @property
    def strike(self) -> float | None:
        """
        Contractually specified price for options exercise.

        Note:
            Applies to OPTION quotes.
        """

        return self._strike

    @property
    def symbol(self) -> str:
        """
        Ticker symbol of the security.

        Note:
            Applies to ALL quotes.
        """

        return self._symbol

    @property
    def to_currency(self) -> str | None:
        """
        Counter currency in exchange pair.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._to_currency

    @property
    def tradeable(self) -> bool:
        """
        Whether the security is currently tradeable.

        Note:
            Applies to ALL quotes.
        """

        return self._tradeable

    @property
    def trailing_annual_dividend_rate(self) -> float | None:
        """
        Dividend payment per share over the past 12 months.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._trailing_annual_dividend_rate

    @property
    def trailing_annual_dividend_yield(self) -> float | None:
        """
        Dividend yield over the past 12 months.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._trailing_annual_dividend_yield

    @property
    def trailing_pe(self) -> float | None:
        """
        Trailing price-to-earnings ratio based on past twelve-month results.

        Note:
            Applies to EQUITY, ETF and MUTUALFUND quotes.
        """

        return self._trailing_pe

    @property
    def trailing_three_month_nav_returns(self) -> float | None:
        """
        Trailing 3-month net asset value (NAV) returns.

        Note:
            Applies to ETF quotes.
        """

        return self._trailing_three_month_nav_returns

    @property
    def trailing_three_month_returns(self) -> float | None:
        """
        Trailing 3-month returns.

        Note:
            Applies to ETF and MUTUALFUND quotes.
        """

        return self._trailing_three_month_returns

    @property
    def triggerable(self) -> bool:
        """
        Internal Yahoo! Finance flag with undocumented and unknown purpose.

        Note:
            Applies to ALL quotes.
        """

        return self._triggerable

    @property
    def two_hundred_day_average(self) -> float | None:
        """
        Average closing price of the stock over the past 200 trading days.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._two_hundred_day_average

    @property
    def two_hundred_day_average_change(self) -> float | None:
        """
        Change in the 200-day average price from the previous trading day.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._two_hundred_day_average_change

    @property
    def two_hundred_day_average_change_percent(self) -> float | None:
        """
        Percent change in the 200-day average price from the previous trading day.

        Note:
            Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and
            MUTUALFUND quotes.
        """

        return self._two_hundred_day_average_change_percent

    @property
    def type_disp(self) -> str:
        """
        User-friendly representation of the QuoteType.

        Note:
            Applies to ALL quotes.
        """

        return self._type_disp

    @property
    def underlying_exchange_symbol(self) -> str | None:
        """
        Exchange symbol for the underlying asset's trading venue.

        Note:
            Applies to FUTURE quotes.
        """

        return self._underlying_exchange_symbol

    @property
    def underlying_short_name(self) -> str | None:
        """
        Short name of the underlying security of a derivative.

        Note:
            Applies to OPTION quotes.
        """

        return self._underlying_short_name

    @property
    def underlying_symbol(self) -> str | None:
        """
        Ticker symbol of the underlying security of a derivative.

        Note:
            Applies to FUTURE and OPTION quotes.
        """

        return self._underlying_symbol

    @property
    def volume_24_hr(self) -> int | None:
        """
        Total trading volume of a cryptocurrency in the past 24 hours.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._volume_24_hr

    @property
    def volume_all_currencies(self) -> int | None:
        """
        Aggregate 24-hour volume across all currency pairs.

        Note:
            Applies to CRYPTOCURRENCY quotes.
        """

        return self._volume_all_currencies

    @property
    def ytd_return(self) -> float | None:
        """
        Year-to-date return on the security.

        Note:
            Applies to ETF and MUTUALFUND quotes.
        """

        return self._ytd_return

    def __init__(self, input_data: dict[str, Any]) -> None:
        """
        Create a quote from Yahoo! Finance API response data.

        Args:
            input_data (dict[str, any]): the JSON data returned by the Yahoo! Finance
            API.
        """

        # load the values of the dictionary into the object, if they exist. Otherwise
        # set them to None

        # start with timezone, since it's going to be required for parsing the
        # timestamps
        self._exchange_timezone_name: str = input_data["exchangeTimezoneName"]
        self._exchange_timezone_short_name: str = input_data[
            "exchangeTimezoneShortName"
        ]

        if sys.version_info >= (3, 11):
            tz_info: ZoneInfo = ZoneInfo(self._exchange_timezone_name)

            def get_datetime(timestamp: int) -> datetime:
                return datetime.fromtimestamp(timestamp, tz_info)

        else:
            tz_info = pytz.timezone(self._exchange_timezone_name)

            def get_datetime(timestamp: int) -> datetime:
                return datetime.fromtimestamp(timestamp).astimezone(tz_info)

        self._ask: float | None = input_data.get("ask")
        self._ask_size: int | None = input_data.get("askSize")
        self._average_analyst_rating: str | None = input_data.get(
            "averageAnalystRating"
        )
        self._average_daily_volume_10_day: int | None = input_data.get(
            "averageDailyVolume10Day"
        )
        self._average_daily_volume_3_month: int | None = input_data.get(
            "averageDailyVolume3Month"
        )
        self._bid: float | None = input_data.get("bid")
        self._bid_size: int | None = input_data.get("bidSize")
        self._book_value: float | None = input_data.get("bookValue")
        self._circulating_supply: int | None = input_data.get("circulatingSupply")
        self._coin_image_url: str | None = input_data.get("coinImageUrl")
        self._coin_market_cap_link: str | None = input_data.get("coinMarketCapLink")
        self._contract_symbol: bool | None = input_data.get("contractSymbol")
        self._crypto_tradeable: bool | None = input_data.get("cryptoTradeable")
        self._currency: str = input_data["currency"]
        self._custom_price_alert_confidence: PriceAlertConfidence = input_data[
            "customPriceAlertConfidence"
        ]
        self._display_name: str | None = input_data.get("displayName")
        self._dividend_date: date | None = (
            get_datetime(input_data["dividendDate"])
            if "dividendDate" in input_data
            else None
        )
        self._dividend_rate: float | None = input_data.get("dividendRate")
        self._dividend_yield: float | None = input_data.get("dividendYield")
        self._earnings_datetime: datetime | None = (
            get_datetime(input_data["earningsTimestamp"])
            if "earningsTimestamp" in input_data
            else None
        )
        self._earnings_datetime_end: datetime | None = (
            get_datetime(input_data["earningsTimestampEnd"])
            if "earningsTimestampEnd" in input_data
            else None
        )
        self._earnings_datetime_start: datetime | None = (
            get_datetime(input_data["earningsTimestampStart"])
            if "earningsTimestampStart" in input_data
            else None
        )
        self._eps_current_year: float | None = input_data.get("epsCurrentYear")
        self._eps_forward: float | None = input_data.get("epsForward")
        self._eps_trailing_twelve_months: float | None = input_data.get(
            "epsTrailingTwelveMonths"
        )
        self._esg_populated: bool = input_data["esgPopulated"]
        self._exchange: str = input_data["exchange"]
        self._exchange_data_delayed_by: int = input_data["exchangeDataDelayedBy"]
        self._expire_date: date | None = (
            datetime.fromtimestamp(input_data["expireDate"], UTC).date()
            if "expireDate" in input_data
            else None
        )
        self._expire_iso_date: str | None = input_data.get("expireIsoDate")
        self._fifty_day_average: float | None = input_data.get("fiftyDayAverage")
        self._fifty_day_average_change: float | None = input_data.get(
            "fiftyDayAverageChange"
        )
        self._fifty_day_average_change_percent: float | None = input_data.get(
            "fiftyDayAverageChangePercent"
        )
        self._fifty_two_week_change_percent: float | None = input_data.get(
            "fiftyTwoWeekChangePercent"
        )
        self._fifty_two_week_high: float = input_data["fiftyTwoWeekHigh"]
        self._fifty_two_week_high_change: float = input_data["fiftyTwoWeekHighChange"]
        self._fifty_two_week_high_change_percent: float = input_data[
            "fiftyTwoWeekHighChangePercent"
        ]
        self._fifty_two_week_low: float = input_data["fiftyTwoWeekLow"]
        self._fifty_two_week_low_change: float = input_data["fiftyTwoWeekLowChange"]
        self._fifty_two_week_low_change_percent: float = input_data[
            "fiftyTwoWeekLowChangePercent"
        ]
        self._fifty_two_week_range: str = input_data["fiftyTwoWeekRange"]
        self._financial_currency: str | None = input_data.get("financialCurrency")
        # We need to pass the timestamp in seconds, not milliseconds
        self._first_trade_datetime: datetime = (
            get_datetime(input_data["firstTradeDateMilliseconds"] / 1000)
        ).replace(  # Now add the milliseconds back in
            microsecond=(input_data["firstTradeDateMilliseconds"] % 1000) * 1000
        )
        self._forward_pe: float | None = input_data.get("forwardPE")
        self._from_currency: str | None = input_data.get("fromCurrency")
        self._full_exchange_name: str = input_data["fullExchangeName"]
        self._gmt_off_set_milliseconds: int = input_data["gmtOffSetMilliseconds"]
        self._head_symbol_as_string: str | None = input_data.get("headSymbolAsString")
        self._ipo_expected_date: date | None = (
            date.fromisoformat(input_data["ipoExpectedDate"])
            if "ipoExpectedDate" in input_data
            else None
        )
        self._language: str = input_data["language"]
        self._last_market: str | None = input_data.get("lastMarket")
        self._logo_url: str | None = input_data.get("logoUrl")
        self._long_name: str | None = input_data.get("longName")
        self._market: str = input_data["market"]
        self._market_cap: int | None = input_data.get("marketCap")
        self._market_state: MarketState = MarketState(input_data["marketState"])
        self._message_board_id: str | None = input_data.get("messageBoardId")
        self._name_change_date: date | None = (
            date.fromisoformat(input_data["nameChangeDate"])
            if "nameChangeDate" in input_data
            else None
        )
        self._net_assets: float | None = input_data.get("netAssets")
        self._net_expense_ratio: float | None = input_data.get("netExpenseRatio")
        self._open_interest: int | None = input_data.get("openInterest")
        self._option_type: OptionType | None = (
            OptionType(input_data["optionType"]) if "optionType" in input_data else None
        )
        self._post_market_change: float | None = input_data.get("postMarketChange")
        self._post_market_change_percent: float | None = input_data.get(
            "postMarketChangePercent"
        )
        self._post_market_price: float | None = input_data.get("postMarketPrice")
        self._post_market_datetime: datetime | None = (
            get_datetime(input_data["postMarketTime"])
            if "postMarketTime" in input_data
            else None
        )
        self._pre_market_change: float | None = input_data.get("preMarketChange")
        self._pre_market_change_percent: float | None = input_data.get(
            "preMarketChangePercent"
        )
        self._pre_market_price: float | None = input_data.get("preMarketPrice")
        self._pre_market_datetime: datetime | None = (
            get_datetime(input_data["preMarketTime"])
            if "preMarketTime" in input_data
            else None
        )
        self._prev_name: str | None = input_data.get("prevName")
        self._price_eps_current_year: float | None = input_data.get(
            "priceEpsCurrentYear"
        )
        self._price_hint: int = input_data["priceHint"]
        self._price_to_book: float | None = input_data.get("priceToBook")
        self._quote_source_name: str | None = input_data.get("quoteSourceName")
        self._quote_type: QuoteType = QuoteType(input_data["quoteType"])
        self._region: str = input_data["region"]
        self._regular_market_change: float = input_data["regularMarketChange"]
        self._regular_market_change_percent: float = input_data[
            "regularMarketChangePercent"
        ]
        self._regular_market_day_high: float | None = input_data.get(
            "regularMarketDayHigh"
        )
        self._regular_market_day_low: float | None = input_data.get(
            "regularMarketDayLow"
        )
        self._regular_market_day_range: str | None = input_data.get(
            "regularMarketDayRange"
        )
        self._regular_market_open: float | None = input_data.get("regularMarketOpen")
        self._regular_market_previous_close: float = input_data[
            "regularMarketPreviousClose"
        ]
        self._regular_market_price: float = input_data["regularMarketPrice"]
        self._regular_market_datetime: datetime = get_datetime(
            input_data["regularMarketTime"]
        )
        self._regular_market_volume: int | None = input_data.get("regularMarketVolume")
        self._shares_outstanding: int | None = input_data.get("sharesOutstanding")
        self._short_name: str = input_data["shortName"]
        self._source_interval: int = input_data["sourceInterval"]
        self._start_date: date | None = (
            get_datetime(input_data["startDate"]) if "startDate" in input_data else None
        )
        self._strike: float | None = input_data.get("strike")
        self._symbol: str = input_data["symbol"]
        self._to_currency: str | None = input_data.get("toCurrency")
        self._tradeable: bool = input_data["tradeable"]
        self._trailing_annual_dividend_rate: float | None = input_data.get(
            "trailingAnnualDividendRate"
        )
        self._trailing_annual_dividend_yield: float | None = input_data.get(
            "trailingAnnualDividendYield"
        )
        self._trailing_pe: float | None = input_data.get("trailingPE")
        self._trailing_three_month_nav_returns: float | None = input_data.get(
            "trailingThreeMonthNavReturns"
        )
        self._trailing_three_month_returns: float | None = input_data.get(
            "trailingThreeMonthReturns"
        )
        self._triggerable: bool = input_data["triggerable"]
        self._two_hundred_day_average: float | None = input_data.get(
            "twoHundredDayAverage"
        )
        self._two_hundred_day_average_change: float | None = input_data.get(
            "twoHundredDayAverageChange"
        )
        self._two_hundred_day_average_change_percent: float | None = input_data.get(
            "twoHundredDayAverageChangePercent"
        )
        self._type_disp: str = input_data["typeDisp"]
        self._underlying_exchange_symbol: str | None = input_data.get(
            "underlyingExchangeSymbol"
        )
        self._underlying_short_name: str | None = input_data.get("underlyingShortName")
        self._underlying_symbol: str | None = input_data.get("underlyingSymbol")
        self._volume_24_hr: int | None = input_data.get("volume24Hr")
        self._volume_all_currencies: int | None = input_data.get("volumeAllCurrencies")
        self._ytd_return: float | None = input_data.get("ytdReturn")

    def __str__(self) -> str:
        """
        Return string representation of the financial quote.

        Returns:
            str: Formatted as 'symbol: price (percent%) -- datetime'.
        """

        return (
            f"YQuote({self._symbol}: {self._regular_market_price} "
            f"({self._regular_market_change_percent:.2f}%) "
            f"-- {self._regular_market_datetime:%Y-%m-%d %H:%M})"
        )
