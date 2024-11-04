"""
This module contains the YQuote class, which represents a quote for a security, as
retrieved from the Yahoo! Finance API.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

if sys.version_info < (3, 11):
    import pytz

    UTC = pytz.UTC
else:
    from datetime import UTC as UTC_DT
    from zoneinfo import ZoneInfo

    UTC = UTC_DT


class QuoteType(Enum):
    """
    Enum for asset classification.

    Attributes:
        EQUITY (str): Equity.
        INDEX (str): Index.
        OPTION (str): Option.
        CURRENCY (str): Currency.
        CRYPTOCURRENCY (str): Cryptocurrency.
        FUTURE (str): Future.
        ETF (str): ETF.
        MUTUALFUND (str): Mutual Fund.
    """

    EQUITY = "EQUITY"
    INDEX = "INDEX"
    OPTION = "OPTION"
    CURRENCY = "CURRENCY"
    CRYPTOCURRENCY = "CRYPTOCURRENCY"
    FUTURE = "FUTURE"
    ETF = "ETF"
    MUTUALFUND = "MUTUALFUND"


class MarketState(Enum):
    """
    Enum for market state.

    Attributes:
        PREPRE (str): Pre-pre market state.
        PRE (str): Pre market state;
            usually weekdays from 4:00am - 9:30am Eastern, excluding holidays.
        REGULAR (str): Regular market state;
            usually weekdays from 9:30am - 4:00pm Eastern, excluding holidays.
        POST (str): Post market state;
            usually weekdays from 4:00pm - 8:00pm Eastern, excluding holidays.
        POSTPOST (str): Post-post market.
        CLOSED (str): Closed market.
    """

    PREPRE = "PREPRE"
    PRE = "PRE"
    REGULAR = "REGULAR"
    POST = "POST"
    POSTPOST = "POSTPOST"
    CLOSED = "CLOSED"


class OptionType(Enum):
    """
    Enum for option type.

    Attributes:
        CALL (str): Call option.
        PUT (str): Put option.
    """

    CALL = "CALL"
    PUT = "PUT"


class PriceAlertConfidence(Enum):
    """
    Enum for price alert confidence.

    Attributes:
        NONE (str): No confidence.
        LOW (str): Low confidence.
        HIGH (str): High confidence.
    """

    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"


class YQuote:
    """
    YQuote is a class representing a quote for a stock or security, as retrieved from
    the Yahoo! Finance API.
    """

    @property
    def ask(self) -> Optional[float]:
        """
        The asking price, or the lowest price that a seller is willing to accept for a
        unit of the security.

        Applies to CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION quotes.
        """
        return self._ask

    @property
    def ask_size(self) -> Optional[int]:
        """
        The total number of shares that are currently being asked for at the asking
        price.

        Applies to CURRENCY, EQUITY, ETF and INDEX quotes.
        """
        return self._ask_size

    @property
    def average_analyst_rating(self) -> Optional[str]:
        """
        A measure of the consensus recommendation for a given stock by financial
        analysts.

        Applies to EQUITY quotes.
        """
        return self._average_analyst_rating

    @property
    def average_daily_volume_10_day(self) -> Optional[int]:
        """
        The average number of shares traded each day over the last 10 days.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._average_daily_volume_10_day

    @property
    def average_daily_volume_3_month(self) -> Optional[int]:
        """
        The average number of shares traded each day over the last 3 months.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._average_daily_volume_3_month

    @property
    def bid(self) -> Optional[float]:
        """
        The bid price, or the highest price that a buyer is willing to pay for a unit
        of the security.

        Applies to CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION quotes.
        """
        return self._bid

    @property
    def bid_size(self) -> Optional[int]:
        """
        The total number of shares that buyers want to buy at the bid price.

        Applies to CURRENCY, EQUITY, ETF and INDEX quotes.
        """
        return self._bid_size

    @property
    def book_value(self) -> Optional[float]:
        """
        The net asset value of a company, calculated by total assets minus intangible
        assets (patents, goodwill) and liabilities.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._book_value

    @property
    def circulating_supply(self) -> Optional[int]:
        """
        In the context of cryptocurrencies, the amount of coins that are publicly
        available and circulating in the market.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._circulating_supply

    @property
    def coin_image_url(self) -> Optional[str]:
        """
        The URL of the image representing the cryptocurrency.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._coin_image_url

    @property
    def coin_market_cap_link(self) -> Optional[str]:
        """
        The URL of the MarketCap site for the cryptocurrency.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._coin_market_cap_link

    @property
    def contract_symbol(self) -> Optional[bool]:
        """
        The ticker symbol for a futures contract.

        Applies to FUTURE quotes.
        """
        return self._contract_symbol

    @property
    def crypto_tradeable(self) -> Optional[bool]:
        """
        Whether the cryptocurrency can be traded.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._crypto_tradeable

    @property
    def currency(self) -> str:
        """
        The currency in which the security is traded.

        Applies to ALL quotes.
        """
        return self._currency

    @property
    def custom_price_alert_confidence(self) -> PriceAlertConfidence:
        """
        A value whose meaning is not clear at the moment.

        Seen values have been NONE, LOW and HIGH.
        Applies to ALL quotes.
        """
        return self._custom_price_alert_confidence

    @property
    def display_name(self) -> Optional[str]:
        """
        The user-friendly name of the stock or security.

        Applies to EQUITY quotes.
        """
        return self._display_name

    @property
    def dividend_date(self) -> Optional[date]:
        """
        The date when the company is expected to pay its next dividend.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._dividend_date

    @property
    def dividend_rate(self) -> Optional[float]:
        """
        The amount of dividends that a company is expected to pay over the next year.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._dividend_rate

    @property
    def dividend_yield(self) -> Optional[float]:
        """
        The dividend yield of a company, calculated as the amount of dividends paid per
        year divided by the stock price.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._dividend_yield

    @property
    def earnings_datetime(self) -> Optional[datetime]:
        """
        The date and time of the company's earnings announcement.

        Applies to EQUITY quotes.
        """
        return self._earnings_datetime

    @property
    def earnings_datetime_end(self) -> Optional[datetime]:
        """
        The date and time of the end of the company's earnings announcement.

        Applies to EQUITY quotes.
        """
        return self._earnings_datetime_end

    @property
    def earnings_datetime_start(self) -> Optional[datetime]:
        """
        The date and time of the start of the company's earnings announcement.

        Applies to EQUITY quotes.
        """
        return self._earnings_datetime_start

    @property
    def eps_current_year(self) -> Optional[float]:
        """
        The company's earnings per share (EPS) for the current year.

        Applies to EQUITY quotes.
        """
        return self._eps_current_year

    @property
    def eps_forward(self) -> Optional[float]:
        """
        The company's projected earnings per share (EPS) for the next fiscal year.

        Applies to EQUITY quotes.
        """
        return self._eps_forward

    @property
    def eps_trailing_twelve_months(self) -> Optional[float]:
        """
        The company's earnings per share (EPS) for the past 12 months.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._eps_trailing_twelve_months

    @property
    def esg_populated(self) -> bool:
        """
        A boolean indicating whether the company's environmental, social, and
        governance (ESG) ratings are populated.

        Applies to ALL quotes.
        """
        return self._esg_populated

    @property
    def exchange(self) -> str:
        """
        The securities exchange on which the security is traded.

        Applies to ALL quotes.
        """
        return self._exchange

    @property
    def exchange_data_delayed_by(self) -> int:
        """
        The delay in data from the exchange, typically in minutes.

        Applies to ALL quotes.
        """
        return self._exchange_data_delayed_by

    @property
    def exchange_timezone_name(self) -> str:
        """
        The name of the timezone of the exchange.

        Applies to ALL quotes.
        """
        return self._exchange_timezone_name

    @property
    def exchange_timezone_short_name(self) -> str:
        """
        The short name of the timezone of the exchange.

        Applies to ALL quotes.
        """
        return self._exchange_timezone_short_name

    @property
    def expire_date(self) -> Optional[date]:
        """
        The date on which the option contract expires.

        Applies to OPTION quotes.
        """
        return self._expire_date

    @property
    def expire_iso_date(self) -> Optional[str]:
        """
        The date on which the option contract expires, in ISO 8601 format.

        Applies to OPTION quotes.
        """
        return self._expire_iso_date

    @property
    def fifty_day_average(self) -> Optional[float]:
        """
        The average closing price of the stock over the past 50 trading days.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._fifty_day_average

    @property
    def fifty_day_average_change(self) -> Optional[float]:
        """
        The change in the 50-day average price from the previous trading day.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._fifty_day_average_change

    @property
    def fifty_day_average_change_percent(self) -> Optional[float]:
        """
        The percent change in the 50-day average price from the previous trading day.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._fifty_day_average_change_percent

    @property
    def fifty_two_week_change_percent(self) -> Optional[float]:
        """
        The percentage change in price over the past 52 weeks.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._fifty_two_week_change_percent

    @property
    def fifty_two_week_high(self) -> float:
        """
        The highest price the stock has traded at in the past 52 weeks.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_high

    @property
    def fifty_two_week_high_change(self) -> float:
        """
        The change in the 52-week high price from the previous trading day.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_high_change

    @property
    def fifty_two_week_high_change_percent(self) -> float:
        """
        The percent change in the 52-week high price from the previous trading day.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_high_change_percent

    @property
    def fifty_two_week_low(self) -> float:
        """
        The lowest price the stock has traded at in the past 52 weeks.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_low

    @property
    def fifty_two_week_low_change(self) -> float:
        """
        The change in the 52-week low price from the previous trading day.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_low_change

    @property
    def fifty_two_week_low_change_percent(self) -> float:
        """
        The percent change in the 52-week low price from the previous trading day.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_low_change_percent

    @property
    def fifty_two_week_range(self) -> str:
        """
        The range of the highest and lowest prices the stock has traded at over the
        past 52 weeks.

        Applies to ALL quotes.
        """
        return self._fifty_two_week_range

    @property
    def financial_currency(self) -> Optional[str]:
        """
        The currency in which the company reports its financial results.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._financial_currency

    @property
    def first_trade_datetime(self) -> datetime:
        """
        The timestamp of the first trade of this security, in milliseconds.

        Applies to ALL quotes.
        """
        return self._first_trade_datetime

    @property
    def forward_pe(self) -> Optional[float]:
        """
        The forward price-to-earnings ratio, calculated as the current share price
        divided by projected earnings per share for
        the next 12 months.

        Applies to EQUITY quotes.
        """
        return self._forward_pe

    @property
    def from_currency(self) -> Optional[str]:
        """
        In a currency pair, the currency that is being exchanged from.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._from_currency

    @property
    def full_exchange_name(self) -> str:
        """
        The full name of the securities exchange on which the security is traded.

        Applies to ALL quotes.
        """
        return self._full_exchange_name

    @property
    def gmt_off_set_milliseconds(self) -> int:
        """
        The offset from GMT of the exchange, in milliseconds.

        Applies to ALL quotes.
        """
        return self._gmt_off_set_milliseconds

    @property
    def head_symbol_as_string(self) -> Optional[str]:
        """
        The symbol of the contract's underlying security.

        Applies to OPTION quotes.
        """
        return self._head_symbol_as_string

    @property
    def ipo_expected_date(self) -> Optional[date]:
        """
        The expected date of the initial public offering (IPO).

        Applies to EQUITY quotes.
        """
        return self._ipo_expected_date

    @property
    def language(self) -> str:
        """
        The language in which financial results are reported.

        Applies to ALL quotes.
        """
        return self._language

    @property
    def last_market(self) -> Optional[str]:
        """
        The last market in which the security was traded.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._last_market

    @property
    def logo_url(self) -> Optional[str]:
        """
        The URL of the company's logo.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._logo_url

    @property
    def long_name(self) -> Optional[str]:
        """
        The official name of the company.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, INDEX and MUTUALFUND quotes.
        """
        return self._long_name

    @property
    def market(self) -> str:
        """
        The market in which the security is primarily traded.

        Applies to ALL quotes.
        """
        return self._market

    @property
    def market_cap(self) -> Optional[int]:
        """
        The market capitalization of the company, calculated as the current stock price
        multiplied by the number of shares
        outstanding.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._market_cap

    @property
    def market_state(self) -> MarketState:
        """
        The current state of the market for a security.

        Applies to ALL quotes.
        """
        return self._market_state

    @property
    def message_board_id(self) -> Optional[str]:
        """
        The identifier for the Yahoo! Finance message board for this security.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, INDEX and MUTUALFUND quotes.
        """
        return self._message_board_id

    @property
    def name_change_date(self) -> Optional[date]:
        """
        The date on which the company last changed its name.

        Applies to EQUITY quotes.
        """
        return self._name_change_date

    @property
    def net_assets(self) -> Optional[float]:
        """
        The total net assets of the company.

        Applies to ETF and MUTUALFUND quotes.
        """
        return self._net_assets

    @property
    def net_expense_ratio(self) -> Optional[float]:
        """
        The ratio of total expenses to total net assets.

        Applies to ETF and MUTUALFUND quotes.
        """
        return self._net_expense_ratio

    @property
    def open_interest(self) -> Optional[int]:
        """
        The total number of open contracts on a futures or options market.

        Applies to FUTURE and OPTION quotes.
        """
        return self._open_interest

    @property
    def option_type(self) -> Optional[OptionType]:
        """
        The type of option.

        Applies to OPTION quotes.
        """
        return self._option_type

    @property
    def post_market_change(self) -> Optional[float]:
        """
        The change in the security's price in post-market trading.

        Applies to ALL quotes.
        """
        return self._post_market_change

    @property
    def post_market_change_percent(self) -> Optional[float]:
        """
        The percent change in the security's price in post-market trading.

        Applies to ALL quotes.
        """
        return self._post_market_change_percent

    @property
    def post_market_price(self) -> Optional[float]:
        """
        The price of the security in post-market trading.

        Applies to ALL quotes.
        """
        return self._post_market_price

    @property
    def post_market_datetime(self) -> Optional[datetime]:
        """
        The time of the most recent post-market trade.

        Applies to ALL quotes.
        """
        return self._post_market_datetime

    @property
    def pre_market_change(self) -> Optional[float]:
        """
        The change in the security's price in pre-market trading.

        Applies to ALL quotes.
        """
        return self._pre_market_change

    @property
    def pre_market_change_percent(self) -> Optional[float]:
        """
        The percent change in the security's price in pre-market trading.

        Applies to ALL quotes.
        """
        return self._pre_market_change_percent

    @property
    def pre_market_price(self) -> Optional[float]:
        """
        The price of the security in pre-market trading.

        Applies to ALL quotes.
        """
        return self._pre_market_price

    @property
    def pre_market_datetime(self) -> Optional[datetime]:
        """
        The time of the most recent pre-market trade.

        Applies to ALL quotes.
        """
        return self._pre_market_datetime

    @property
    def prev_name(self) -> Optional[str]:
        """
        The name of the company prior to its most recent name change.

        Applies to EQUITY quotes.
        """
        return self._prev_name

    @property
    def price_eps_current_year(self) -> Optional[float]:
        """
        The price of the stock divided by the company's earnings per share (EPS) for
        the current year.

        Applies to EQUITY quotes.
        """
        return self._price_eps_current_year

    @property
    def price_hint(self) -> int:
        """
        A hint about the precision of the price data (e.g. the number of decimal
        places).

        Applies to ALL quotes.
        """
        return self._price_hint

    @property
    def price_to_book(self) -> Optional[float]:
        """
        The price-to-book ratio, calculated as the market price per share divided by
        the book value per share.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._price_to_book

    @property
    def quote_source_name(self) -> Optional[str]:
        """
        The name of the source providing the quote.

        Applies to ALL quotes.
        """
        return self._quote_source_name

    @property
    def quote_type(self) -> QuoteType:
        """
        The type of quote.

        Applies to ALL quotes.
        """
        return self._quote_type

    @property
    def region(self) -> str:
        """
        The region in which the company is located.

        Applies to ALL quotes.
        """
        return self._region

    @property
    def regular_market_change(self) -> float:
        """
        The change in the security's price in regular trading.

        Applies to ALL quotes.
        """
        return self._regular_market_change

    @property
    def regular_market_change_percent(self) -> float:
        """
        The percent change in the security's price in regular trading.

        Applies to ALL quotes.
        """
        return self._regular_market_change_percent

    @property
    def regular_market_day_high(self) -> Optional[float]:
        """
        The highest price the security has traded at in the most recent regular trading
        session.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
        quotes.
        """
        return self._regular_market_day_high

    @property
    def regular_market_day_low(self) -> Optional[float]:
        """
        The lowest price the security has traded at in the most recent regular trading
        session.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
        quotes.
        """
        return self._regular_market_day_low

    @property
    def regular_market_day_range(self) -> Optional[str]:
        """
        The range of prices at which the security has traded during the most recent
        regular trading session.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
        quotes.
        """
        return self._regular_market_day_range

    @property
    def regular_market_open(self) -> Optional[float]:
        """
        The price at which the security first traded in the most recent regular trading
        session.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
        quotes.
        """
        return self._regular_market_open

    @property
    def regular_market_previous_close(self) -> float:
        """
        The closing price of the security in the previous regular trading session.

        Applies to ALL quotes.
        """
        return self._regular_market_previous_close

    @property
    def regular_market_price(self) -> float:
        """
        The last traded price of the security in the most recent regular trading
        session.

        Applies to ALL quotes.
        """
        return self._regular_market_price

    @property
    def regular_market_datetime(self) -> datetime:
        """
        The time of the most recent trade in the regular trading session.

        Applies to ALL quotes.
        """
        return self._regular_market_datetime

    @property
    def regular_market_volume(self) -> Optional[int]:
        """
        The total number of shares traded during the most recent regular trading
        session.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and OPTION
        quotes.
        """
        return self._regular_market_volume

    @property
    def shares_outstanding(self) -> Optional[int]:
        """
        The number of shares currently held by all shareholders.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._shares_outstanding

    @property
    def short_name(self) -> str:
        """
        The short, user-friendly name for the stock or security.

        Applies to ALL quotes.
        """
        return self._short_name

    @property
    def source_interval(self) -> int:
        """
        The interval at which the data source provides updates, in seconds.

        Applies to ALL quotes.
        """
        return self._source_interval

    @property
    def start_date(self) -> Optional[date]:
        """
        The date on which the coin started trading.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._start_date

    @property
    def strike(self) -> Optional[float]:
        """
        The strike price of an options contract, which is the price at which the
        contract can be exercised.

        Applies to OPTION quotes.
        """
        return self._strike

    @property
    def symbol(self) -> str:
        """
        The ticker symbol of the security.

        Applies to ALL quotes.
        """
        return self._symbol

    @property
    def to_currency(self) -> Optional[str]:
        """
        In a currency pair, the currency that is being exchanged to.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._to_currency

    @property
    def tradeable(self) -> bool:
        """
        Whether the security is currently tradeable.

        Applies to ALL quotes.
        """
        return self._tradeable

    @property
    def trailing_annual_dividend_rate(self) -> Optional[float]:
        """
        The company's dividend payment per share over the past 12 months.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._trailing_annual_dividend_rate

    @property
    def trailing_annual_dividend_yield(self) -> Optional[float]:
        """
        The company's dividend yield over the past 12 months.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._trailing_annual_dividend_yield

    @property
    def trailing_pe(self) -> Optional[float]:
        """
        The trailing price-to-earnings ratio, calculated as the current share price
        divided by the earnings per share (EPS) over
        the past 12 months.

        Applies to EQUITY, ETF and MUTUALFUND quotes.
        """
        return self._trailing_pe

    @property
    def trailing_three_month_nav_returns(self) -> Optional[float]:
        """
        The trailing 3-month net asset value (NAV) returns.

        Applies to ETF quotes.
        """
        return self._trailing_three_month_nav_returns

    @property
    def trailing_three_month_returns(self) -> Optional[float]:
        """
        The trailing 3-month returns.

        Applies to ETF and MUTUALFUND quotes.
        """
        return self._trailing_three_month_returns

    @property
    def triggerable(self) -> bool:
        """
        A boolean value whose meaning is not clear at the moment.

        Applies to ALL quotes.
        """
        return self._triggerable

    @property
    def two_hundred_day_average(self) -> Optional[float]:
        """
        The average closing price of the stock over the past 200 trading days.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._two_hundred_day_average

    @property
    def two_hundred_day_average_change(self) -> Optional[float]:
        """
        The change in the 200-day average price from the previous trading day.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._two_hundred_day_average_change

    @property
    def two_hundred_day_average_change_percent(self) -> Optional[float]:
        """
        The percent change in the 200-day average price from the previous trading day.

        Applies to CRYPTOCURRENCY, CURRENCY, EQUITY, ETF, FUTURE, INDEX and MUTUALFUND
        quotes.
        """
        return self._two_hundred_day_average_change_percent

    @property
    def type_disp(self) -> str:
        """
        A user-friendly representation of the QuoteType.

        Applies to ALL quotes.
        """
        return self._type_disp

    @property
    def underlying_exchange_symbol(self) -> Optional[str]:
        """
        The symbol of the exchange on which the underlying security of a derivative is
        traded.

        Applies to FUTURE quotes.
        """
        return self._underlying_exchange_symbol

    @property
    def underlying_short_name(self) -> Optional[str]:
        """
        The short name of the underlying security of a derivative.

        Applies to OPTION quotes.
        """
        return self._underlying_short_name

    @property
    def underlying_symbol(self) -> Optional[str]:
        """
        The ticker symbol of the underlying security of a derivative.

        Applies to FUTURE and OPTION quotes.
        """
        return self._underlying_symbol

    @property
    def volume_24_hr(self) -> Optional[int]:
        """
        The total trading volume of a cryptocurrency in the past 24 hours.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._volume_24_hr

    @property
    def volume_all_currencies(self) -> Optional[int]:
        """
        The total trading volume of a cryptocurrency across all currencies in the past
        24 hours.

        Applies to CRYPTOCURRENCY quotes.
        """
        return self._volume_all_currencies

    @property
    def ytd_return(self) -> Optional[float]:
        """
        The year-to-date return on the security.

        Applies to ETF and MUTUALFUND quotes.
        """
        return self._ytd_return

    def __init__(self, input_data: dict[str, Any]) -> None:
        """
        Initializes a YQuote object.

        Args:
            input_data (dict[str, any]): the JSON data returned by the Yahoo Finance API

        Raises:
            ValueError: if input_data is None
        """

        # load the values of the dictionary into the object, if they exist. Otherwise
        # set them to None

        # start with timezone, since it's going to be required for parsing the
        # timestamps
        self._exchange_timezone_name: str = input_data["exchangeTimezoneName"]
        self._exchange_timezone_short_name: str = input_data[
            "exchangeTimezoneShortName"
        ]

        if sys.version_info < (3, 11):
            tz_info = pytz.timezone(self._exchange_timezone_name)

            def get_datetime(timestamp: int) -> datetime:
                return datetime.fromtimestamp(timestamp).astimezone(tz_info)

        else:
            tz_info: ZoneInfo = ZoneInfo(self._exchange_timezone_name)

            def get_datetime(timestamp: int) -> datetime:
                return datetime.fromtimestamp(timestamp, tz_info)

        self._ask: Optional[float] = input_data["ask"] if "ask" in input_data else None
        self._ask_size: Optional[int] = (
            input_data["askSize"] if "askSize" in input_data else None
        )
        self._average_analyst_rating: Optional[str] = (
            input_data["averageAnalystRating"]
            if "averageAnalystRating" in input_data
            else None
        )
        self._average_daily_volume_10_day: Optional[int] = (
            input_data["averageDailyVolume10Day"]
            if "averageDailyVolume10Day" in input_data
            else None
        )
        self._average_daily_volume_3_month: Optional[int] = (
            input_data["averageDailyVolume3Month"]
            if "averageDailyVolume3Month" in input_data
            else None
        )
        self._bid: Optional[float] = input_data["bid"] if "bid" in input_data else None
        self._bid_size: Optional[int] = (
            input_data["bidSize"] if "bidSize" in input_data else None
        )
        self._book_value: Optional[float] = (
            input_data["bookValue"] if "bookValue" in input_data else None
        )
        self._circulating_supply: Optional[int] = (
            input_data["circulatingSupply"]
            if "circulatingSupply" in input_data
            else None
        )
        self._coin_image_url: Optional[str] = (
            input_data["coinImageUrl"] if "coinImageUrl" in input_data else None
        )
        self._coin_market_cap_link: Optional[str] = (
            input_data["coinMarketCapLink"]
            if "coinMarketCapLink" in input_data
            else None
        )
        self._contract_symbol: Optional[bool] = (
            input_data["contractSymbol"] if "contractSymbol" in input_data else None
        )
        self._crypto_tradeable: Optional[bool] = (
            input_data["cryptoTradeable"] if "cryptoTradeable" in input_data else None
        )
        self._currency: str = input_data["currency"]
        self._custom_price_alert_confidence: PriceAlertConfidence = input_data[
            "customPriceAlertConfidence"
        ]
        self._display_name: Optional[str] = (
            input_data["displayName"] if "displayName" in input_data else None
        )
        self._dividend_date: Optional[date] = (
            get_datetime(input_data["dividendDate"])
            if "dividendDate" in input_data
            else None
        )
        self._dividend_rate: Optional[float] = (
            input_data["dividendRate"] if "dividendRate" in input_data else None
        )
        self._dividend_yield: Optional[float] = (
            input_data["dividendYield"] if "dividendYield" in input_data else None
        )
        self._earnings_datetime: Optional[datetime] = (
            get_datetime(input_data["earningsTimestamp"])
            if "earningsTimestamp" in input_data
            else None
        )
        self._earnings_datetime_end: Optional[datetime] = (
            get_datetime(input_data["earningsTimestampEnd"])
            if "earningsTimestampEnd" in input_data
            else None
        )
        self._earnings_datetime_start: Optional[datetime] = (
            get_datetime(input_data["earningsTimestampStart"])
            if "earningsTimestampStart" in input_data
            else None
        )
        self._eps_current_year: Optional[float] = (
            input_data["epsCurrentYear"] if "epsCurrentYear" in input_data else None
        )
        self._eps_forward: Optional[float] = (
            input_data["epsForward"] if "epsForward" in input_data else None
        )
        self._eps_trailing_twelve_months: Optional[float] = (
            input_data["epsTrailingTwelveMonths"]
            if "epsTrailingTwelveMonths" in input_data
            else None
        )
        self._esg_populated: bool = input_data["esgPopulated"]
        self._exchange: str = input_data["exchange"]
        self._exchange_data_delayed_by: int = input_data["exchangeDataDelayedBy"]
        self._expire_date: Optional[date] = (
            datetime.fromtimestamp(input_data["expireDate"], UTC).date()
            if "expireDate" in input_data
            else None
        )
        self._expire_iso_date: Optional[str] = (
            input_data["expireIsoDate"] if "expireIsoDate" in input_data else None
        )
        self._fifty_day_average: Optional[float] = (
            input_data["fiftyDayAverage"] if "fiftyDayAverage" in input_data else None
        )
        self._fifty_day_average_change: Optional[float] = (
            input_data["fiftyDayAverageChange"]
            if "fiftyDayAverageChange" in input_data
            else None
        )
        self._fifty_day_average_change_percent: Optional[float] = (
            input_data["fiftyDayAverageChangePercent"]
            if "fiftyDayAverageChangePercent" in input_data
            else None
        )
        self._fifty_two_week_change_percent: Optional[float] = (
            input_data["fiftyTwoWeekChangePercent"]
            if "fiftyTwoWeekChangePercent" in input_data
            else None
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
        self._financial_currency: Optional[str] = (
            input_data["financialCurrency"]
            if "financialCurrency" in input_data
            else None
        )
        # We need to pass the timestamp in seconds, not milliseconds
        self._first_trade_datetime: datetime = (
            get_datetime(input_data["firstTradeDateMilliseconds"] / 1000)
        ).replace(  # Now add the milliseconds back in
            microsecond=(input_data["firstTradeDateMilliseconds"] % 1000) * 1000
        )
        self._forward_pe: Optional[float] = (
            input_data["forwardPE"] if "forwardPE" in input_data else None
        )
        self._from_currency: Optional[str] = (
            input_data["fromCurrency"] if "fromCurrency" in input_data else None
        )
        self._full_exchange_name: str = input_data["fullExchangeName"]
        self._gmt_off_set_milliseconds: int = input_data["gmtOffSetMilliseconds"]
        self._head_symbol_as_string: Optional[str] = (
            input_data["headSymbolAsString"]
            if "headSymbolAsString" in input_data
            else None
        )
        self._ipo_expected_date: Optional[date] = (
            date.fromisoformat(input_data["ipoExpectedDate"])
            if "ipoExpectedDate" in input_data
            else None
        )
        self._language: str = input_data["language"]
        self._last_market: Optional[str] = (
            input_data["lastMarket"] if "lastMarket" in input_data else None
        )
        self._logo_url: Optional[str] = (
            input_data["logoUrl"] if "logoUrl" in input_data else None
        )
        self._long_name: Optional[str] = (
            input_data["longName"] if "longName" in input_data else None
        )
        self._market: str = input_data["market"]
        self._market_cap: Optional[int] = (
            input_data["marketCap"] if "marketCap" in input_data else None
        )
        self._market_state: MarketState = MarketState(input_data["marketState"])
        self._message_board_id: Optional[str] = (
            input_data["messageBoardId"] if "messageBoardId" in input_data else None
        )
        self._name_change_date: Optional[date] = (
            date.fromisoformat(input_data["nameChangeDate"])
            if "nameChangeDate" in input_data
            else None
        )
        self._net_assets: Optional[float] = (
            input_data["netAssets"] if "netAssets" in input_data else None
        )
        self._net_expense_ratio: Optional[float] = (
            input_data["netExpenseRatio"] if "netExpenseRatio" in input_data else None
        )
        self._open_interest: Optional[int] = (
            input_data["openInterest"] if "openInterest" in input_data else None
        )
        self._option_type: Optional[OptionType] = (
            OptionType(input_data["optionType"]) if "optionType" in input_data else None
        )
        self._post_market_change: Optional[float] = (
            input_data["postMarketChange"] if "postMarketChange" in input_data else None
        )
        self._post_market_change_percent: Optional[float] = (
            input_data["postMarketChangePercent"]
            if "postMarketChangePercent" in input_data
            else None
        )
        self._post_market_price: Optional[float] = (
            input_data["postMarketPrice"] if "postMarketPrice" in input_data else None
        )
        self._post_market_datetime: Optional[datetime] = (
            get_datetime(input_data["postMarketTime"])
            if "postMarketTime" in input_data
            else None
        )
        self._pre_market_change: Optional[float] = (
            input_data["preMarketChange"] if "preMarketChange" in input_data else None
        )
        self._pre_market_change_percent: Optional[float] = (
            input_data["preMarketChangePercent"]
            if "preMarketChangePercent" in input_data
            else None
        )
        self._pre_market_price: Optional[float] = (
            input_data["preMarketPrice"] if "preMarketPrice" in input_data else None
        )
        self._pre_market_datetime: Optional[datetime] = (
            get_datetime(input_data["preMarketTime"])
            if "preMarketTime" in input_data
            else None
        )
        self._prev_name: Optional[str] = (
            input_data["prevName"] if "prevName" in input_data else None
        )
        self._price_eps_current_year: Optional[float] = (
            input_data["priceEpsCurrentYear"]
            if "priceEpsCurrentYear" in input_data
            else None
        )
        self._price_hint: int = input_data["priceHint"]
        self._price_to_book: Optional[float] = (
            input_data["priceToBook"] if "priceToBook" in input_data else None
        )
        self._quote_source_name: Optional[str] = (
            input_data["quoteSourceName"] if "quoteSourceName" in input_data else None
        )
        self._quote_type: QuoteType = QuoteType(input_data["quoteType"])
        self._region: str = input_data["region"]
        self._regular_market_change: float = input_data["regularMarketChange"]
        self._regular_market_change_percent: float = input_data[
            "regularMarketChangePercent"
        ]
        self._regular_market_day_high: Optional[float] = (
            input_data["regularMarketDayHigh"]
            if "regularMarketDayHigh" in input_data
            else None
        )
        self._regular_market_day_low: Optional[float] = (
            input_data["regularMarketDayLow"]
            if "regularMarketDayLow" in input_data
            else None
        )
        self._regular_market_day_range: Optional[str] = (
            input_data["regularMarketDayRange"]
            if "regularMarketDayRange" in input_data
            else None
        )
        self._regular_market_open: Optional[float] = (
            input_data["regularMarketOpen"]
            if "regularMarketOpen" in input_data
            else None
        )
        self._regular_market_previous_close: float = input_data[
            "regularMarketPreviousClose"
        ]
        self._regular_market_price: float = input_data["regularMarketPrice"]
        self._regular_market_datetime: datetime = get_datetime(
            input_data["regularMarketTime"]
        )
        self._regular_market_volume: Optional[int] = (
            input_data["regularMarketVolume"]
            if "regularMarketVolume" in input_data
            else None
        )
        self._shares_outstanding: Optional[int] = (
            input_data["sharesOutstanding"]
            if "sharesOutstanding" in input_data
            else None
        )
        self._short_name: str = input_data["shortName"]
        self._source_interval: int = input_data["sourceInterval"]
        self._start_date: Optional[date] = (
            get_datetime(input_data["startDate"]) if "startDate" in input_data else None
        )
        self._strike: Optional[float] = (
            input_data["strike"] if "strike" in input_data else None
        )
        self._symbol: str = input_data["symbol"]
        self._to_currency: Optional[str] = (
            input_data["toCurrency"] if "toCurrency" in input_data else None
        )
        self._tradeable: bool = input_data["tradeable"]
        self._trailing_annual_dividend_rate: Optional[float] = (
            input_data["trailingAnnualDividendRate"]
            if "trailingAnnualDividendRate" in input_data
            else None
        )
        self._trailing_annual_dividend_yield: Optional[float] = (
            input_data["trailingAnnualDividendYield"]
            if "trailingAnnualDividendYield" in input_data
            else None
        )
        self._trailing_pe: Optional[float] = (
            input_data["trailingPE"] if "trailingPE" in input_data else None
        )
        self._trailing_three_month_nav_returns: Optional[float] = (
            input_data["trailingThreeMonthNavReturns"]
            if "trailingThreeMonthNavReturns" in input_data
            else None
        )
        self._trailing_three_month_returns: Optional[float] = (
            input_data["trailingThreeMonthReturns"]
            if "trailingThreeMonthReturns" in input_data
            else None
        )
        self._triggerable: bool = input_data["triggerable"]
        self._two_hundred_day_average: Optional[float] = (
            input_data["twoHundredDayAverage"]
            if "twoHundredDayAverage" in input_data
            else None
        )
        self._two_hundred_day_average_change: Optional[float] = (
            input_data["twoHundredDayAverageChange"]
            if "twoHundredDayAverageChange" in input_data
            else None
        )
        self._two_hundred_day_average_change_percent: Optional[float] = (
            input_data["twoHundredDayAverageChangePercent"]
            if "twoHundredDayAverageChangePercent" in input_data
            else None
        )
        self._type_disp: str = input_data["typeDisp"]
        self._underlying_exchange_symbol: Optional[str] = (
            input_data["underlyingExchangeSymbol"]
            if "underlyingExchangeSymbol" in input_data
            else None
        )
        self._underlying_short_name: Optional[str] = (
            input_data["underlyingShortName"]
            if "underlyingShortName" in input_data
            else None
        )
        self._underlying_symbol: Optional[str] = (
            input_data["underlyingSymbol"] if "underlyingSymbol" in input_data else None
        )
        self._volume_24_hr: Optional[int] = (
            input_data["volume24Hr"] if "volume24Hr" in input_data else None
        )
        self._volume_all_currencies: Optional[int] = (
            input_data["volumeAllCurrencies"]
            if "volumeAllCurrencies" in input_data
            else None
        )
        self._ytd_return: Optional[float] = (
            input_data["ytdReturn"] if "ytdReturn" in input_data else None
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: a string representation of the object
        """

        return (
            f"YQuote({self._symbol}: {self._regular_market_price}"
            + f" ({self._regular_market_change_percent:.2f}%)"
            + f" -- {self._regular_market_datetime:%Y-%m-%d %H:%M})"
        )
