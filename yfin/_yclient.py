"""
This module provides a client for the Yahoo! Finance API.
"""

import datetime
import json
import logging
import urllib.parse
from typing import Any

import requests


class YClient:
    """
    Yahoo! Finance API client.
    """

    _DEFAULT_HTTP_TIMEOUT: int = 80
    _YAHOO_FINANCE_URL: str = "https://query1.finance.yahoo.com"
    _CRUMB_URL: str = _YAHOO_FINANCE_URL + "/v1/test/getcrumb"
    _COOKIE_URL: str = "https://login.yahoo.com"
    _USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"

    def __init__(self) -> None:
        self._http_client: requests.Session = requests.Session()
        self._http_client.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "text/plain",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
            "User-Agent": self._USER_AGENT,
        }

        self._expiry: datetime.datetime = datetime.datetime(1970, 1, 1)
        self._crumb: str = ""

    def __refresh_cookies(self) -> None:
        """
        Refreshes cookies from Yahoo Finance.

        The cookies are required to fetch the crumb that is in turn required to fetch quotes.
        """

        logging.debug("Refreshing cookies")

        with self._http_client.get(
            self._COOKIE_URL,
            timeout=self._DEFAULT_HTTP_TIMEOUT,
        ) as response:
            # default expiry is ten years in the future
            expiry = datetime.datetime.now() + datetime.timedelta(days=3650)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.error("Can't refresh cookies: %s", e)
                return

            for cookie in response.cookies:
                logging.debug("Considering cookie: %s", cookie)

                if cookie.name == "AS" or cookie.expires is None:
                    logging.debug(
                        "Cookie ignored based on name: %s or lack of expiry",
                        cookie.name,
                    )
                    continue

                # compute expiry as now + cookie expiry
                cookie_expiry = datetime.datetime.fromtimestamp(cookie.expires)

                # if the cookie expires afthe the current expiry, don't update the expiry
                if cookie_expiry >= expiry:
                    logging.debug("Cookie ignored based on expiry: %s", cookie_expiry)
                    continue

                logging.debug(
                    "Cookie %s accepted. Setting expiry to %s",
                    cookie.name,
                    cookie_expiry.strftime("%Y-%m-%d %H:%M:%S"),
                )
                expiry = cookie_expiry

            self._expiry = expiry

    def __fetch_crumb(self) -> str:
        """
        Refresh the crumb required to fetch quotes.

        Returns:
            str: The retrieved crumb.
        """

        logging.debug("Fetching crumb")

        with self._http_client.get(
            self._CRUMB_URL, timeout=self._DEFAULT_HTTP_TIMEOUT
        ) as response:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.error("Can't fetch crumb: %s", e)
                return ""

            return response.text

    def __refresh_crumb(self):
        """
        Refresh the crumb required to fetch quotes."""

        logging.debug("Refreshing crumb...")
        self.__refresh_cookies()
        self._crumb = self.__fetch_crumb()

        if self._crumb is not None and self._crumb != "":
            logging.debug(
                "Crumb refreshed: %s. Expires on %s",
                self._crumb,
                self._expiry.strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            logging.debug("Crumb refresh failed")

    def _execute_request(self, api_call: str) -> dict[str, Any]:
        """
        Execute the given request and return the data from the response.

        Args:
            api_call (str): The path to the Yahoo! finance API call (with arguments) to create a request for.

        Returns:
            dict[str, Any]: The JSON response.
        """
        start = datetime.datetime.now()

        with self._http_client.get(
            self._YAHOO_FINANCE_URL + api_call, timeout=self._DEFAULT_HTTP_TIMEOUT
        ) as response:
            logging.debug("Completed in %s", datetime.datetime.now() - start)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.error("Request to api failed: %s", e)
                return {}

            res_body = response.text
            logging.debug("Response: %s", res_body)

            if res_body is None or res_body == "":
                logging.error("Can't parse response")
                return {}

            return json.loads(res_body)

    def call(
        self, api_url: str, query_params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Call the given path with the given query parameters (if any) and return the data from the response.

        Args:
            api_url (str): The path of the API to call on the Yahoo! Finance API.
            query_params (dict[str, str], optional): The query parameters to pass along with the api call. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response.
        """

        logging.debug("Calling %s with params %s", api_url, query_params)

        if self._expiry < datetime.datetime.now():
            self.__refresh_crumb()

        if query_params is None:
            query_params = {}

        if self._crumb is not None and self._crumb != "":
            query_params["crumb"] = self._crumb

        if query_params is not None and len(query_params) > 0:
            query_string = urllib.parse.urlencode(query_params)
            api_url += "?" + query_string

        return self._execute_request(api_url)
