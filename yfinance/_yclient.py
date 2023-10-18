"""This module provides a client for the Yahoo! Finance API."""

import json
import logging
import re
import urllib.parse
from datetime import datetime, timedelta
from http.cookiejar import Cookie
from typing import Any, Optional

import requests
from requests.cookies import RequestsCookieJar


class YClient:
    """Yahoo! Finance API client."""

    _DEFAULT_HTTP_TIMEOUT: int = 80
    _LOGIN_URL: str = "https://login.yahoo.com"
    _YAHOO_FINANCE_URL: str = "https://query1.finance.yahoo.com"
    _CRUMB_URL: str = _YAHOO_FINANCE_URL + "/v1/test/getcrumb"
    _USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    _USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION = (
        '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"'
    )
    _USER_AGENT_CLIENT_HINT_PLATFORM = '"Windows"'

    def __init__(self) -> None:
        self._session: requests.Session = requests.Session()
        self._session.headers.update(
            {
                "authority": "query1.finance.yahoo.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,ja;q=0.8",
                "origin": "https://finance.yahoo.com",
                "sec-ch-ua": self._USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": self._USER_AGENT_CLIENT_HINT_PLATFORM,
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": self._USER_AGENT,
            }
        )
        self._session.params = {
            "formatted": "true",
            "lang": "en-US",
            "region": "US",
            "corsDomain": "finance.yahoo.com",
        }

        self._expiry: datetime = datetime(1970, 1, 1)
        self._crumb: str = ""

    def __refresh_cookies(self) -> None:
        """
        Logging to Yahoo! finance.

        Logging in will set the cookies that are required to fetch the crumb and make calls to the Yahoo! finance API.
        """

        headers: dict[str, str] = {
            "authority": "finance.yahoo.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": self._USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": self._USER_AGENT_CLIENT_HINT_PLATFORM,
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self._USER_AGENT,
        }

        def _is_eu_consent_redirect(response: requests.Response) -> bool:
            return "guce.yahoo.com" in response.headers.get("Location", "") and str(
                response.status_code
            ).startswith("3")

        logging.debug("Logging in...")

        response: requests.Response
        with self._session.get(
            "https://finance.yahoo.com/",
            headers=headers,
            allow_redirects=False,
        ) as response:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.exception("Can't log in: %s", e)
                return

            cookies: RequestsCookieJar = response.cookies

            if _is_eu_consent_redirect(response):
                cookies = self.__get_cookies_eu()

            if not any(cookie.name == "A3" for cookie in cookies):
                logging.error("Required cookie not set")
                return

            # Figure out how long the login is valid for.
            # Default expiry is ten years in the future
            expiry: datetime = datetime.now() + timedelta(days=3650)

            cookie: Cookie
            for cookie in cookies:
                if cookie.domain != ".yahoo.com" or cookie.expires is None:
                    continue

                cookie_expiry: datetime = datetime.fromtimestamp(cookie.expires)

                if cookie_expiry >= expiry:
                    continue

                logging.debug(
                    "Cookie %s accepted. Setting expiry to %s",
                    cookie.name,
                    cookie_expiry.strftime("%Y-%m-%d %H:%M:%S"),
                )
                expiry = cookie_expiry

            self._expiry = expiry

    def __get_cookies_eu(self) -> RequestsCookieJar:
        headers: dict[str, str] = {
            "authority": "finance.yahoo.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": self._USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": self._USER_AGENT_CLIENT_HINT_PLATFORM,
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self._USER_AGENT,
        }

        res1: requests.Response
        with self._session.get(
            "https://finance.yahoo.com/", headers=headers, allow_redirects=True
        ) as res1:
            try:
                res1.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.exception("Can't log in: %s", e)
                return RequestsCookieJar()

            re_session_id: re.Pattern = re.compile("sessionId=(?:([A-Za-z0-9_-]*))")
            session_id_match_result: list[str] = re_session_id.findall(res1.url)

            if len(session_id_match_result) != 1:
                logging.error(
                    "error unable to extract session id from redirected request URL: '%s'",
                    res1.url,
                )
                return RequestsCookieJar()

            session_id: str = session_id_match_result[0]

            # Find the right URL in the history
            guce_response: Optional[requests.Response] = None
            hist: requests.Response
            for hist in res1.history:
                if hist.url.startswith("https://guce.yahoo.com"):
                    guce_response = hist
                    break

            if guce_response is None:
                logging.error("No redirect found")
                return RequestsCookieJar()

            re_csrf_token: re.Pattern = re.compile("gcrumb=(?:([A-Za-z0-9_]*))")
            csrf_token_match_result: list[str] = re_csrf_token.findall(
                guce_response.url
            )

            if len(csrf_token_match_result) != 1:
                logging.error(
                    "error unable to extract CSRF token from Location header: '%s'",
                    res1.headers.get("Location", ""),
                )
                return RequestsCookieJar()

            csrf_token: str = csrf_token_match_result[0]

            # Look for the history with cookies
            guce_response: Optional[requests.Response] = None
            for hist in res1.history:
                if hist.cookies.get("GUCS") is not None:
                    guce_response = hist
                    break

            if guce_response is None:
                logging.error("No redirect found")
                return RequestsCookieJar()

            gucs_cookie: RequestsCookieJar = guce_response.cookies

            if len(gucs_cookie) == 0:
                logging.error("no cookies set by finance.yahoo.com")
                return RequestsCookieJar()

            headers2: dict[str, str] = {
                "origin": "https://consent.yahoo.com",
                "host": "consent.yahoo.com",
                "content-type": "application/x-www-form-urlencoded",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "accept-encoding": "gzip, deflate, br",
                "dnt": "1",
                "sec-ch-ua": self._USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": self._USER_AGENT_CLIENT_HINT_PLATFORM,
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "referer": "https://consent.yahoo.com/v2/collectConsent?sessionId="
                + session_id,
                "user-agent": self._USER_AGENT,
            }

            data = {
                "csrfToken": csrf_token,
                "sessionId": session_id,
                "namespace": "yahoo",
                "agree": "agree",
            }

            with self._session.post(
                "https://consent.yahoo.com/v2/collectConsent?sessionId=" + session_id,
                headers=headers2,
                cookies=gucs_cookie,
                data=data,
                allow_redirects=True,
            ) as res2:
                for hist in res2.history:
                    if hist.cookies.get("A3") is not None:
                        return hist.cookies

            return RequestsCookieJar()

    def __refresh_crumb(self) -> None:
        """Refresh the crumb required to fetch quotes."""

        logging.debug("Refreshing crumb...")

        response: requests.Response
        with self._session.get(
            self._CRUMB_URL, timeout=self._DEFAULT_HTTP_TIMEOUT
        ) as response:
            try:
                response.raise_for_status()
                self._crumb = response.text
            except requests.exceptions.HTTPError as e:
                logging.exception("Can't fetch crumb: %s", e)

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

        logging.debug("Executing request: %s", api_call)

        response: requests.Response
        with self._session.get(
            self._YAHOO_FINANCE_URL + api_call, timeout=self._DEFAULT_HTTP_TIMEOUT
        ) as response:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logging.exception("Request to api failed: %s", e)
                return {}

            res_body: str = response.text
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

        if self._expiry < datetime.now():
            self.__refresh_cookies()

        if self._crumb == "":
            self.__refresh_crumb()

        if query_params is None:
            query_params = {}

        if self._crumb is not None and self._crumb != "":
            query_params["crumb"] = self._crumb

        if query_params is not None and len(query_params) > 0:
            query_string = urllib.parse.urlencode(query_params)
            api_url += "?" + query_string

        return self._execute_request(api_url)
