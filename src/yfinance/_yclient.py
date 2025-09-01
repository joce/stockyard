"""
Provide low-level client interface to Yahoo! Finance API.

Implements session persistence, authentication flow, and request signing required for
reliable API communication.
"""

# pylint: disable=line-too-long

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Final

import httpx

if TYPE_CHECKING:
    from http.cookiejar import Cookie


class YClient:
    """Yahoo! Finance API client."""

    _DEFAULT_HTTP_TIMEOUT: Final[int] = 80
    _YAHOO_FINANCE_URL: Final[str] = "https://finance.yahoo.com"
    _YAHOO_FINANCE_QUERY_URL: Final[str] = "https://query1.finance.yahoo.com"
    _CRUMB_URL: Final[str] = _YAHOO_FINANCE_QUERY_URL + "/v1/test/getcrumb"
    _USER_AGENT: Final[str] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.3240.64"  # noqa: E501
    )
    _USER_AGENT_CLIENT_HINT_BRANDING_AND_VERSION: Final[str] = (
        '"Microsoft Edge";v="136", "Chromium";v="136", "Not;A=Brand";v="24"'
    )
    _USER_AGENT_CLIENT_HINT_PLATFORM: Final[str] = '"Windows"'

    _COOKIE_HEADERS: Final[dict[str, str]] = {
        "authority": "finance.yahoo.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",  # noqa: E501
        "accept-language": "en-US,en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": _USER_AGENT,
    }

    def __init__(self) -> None:
        self._client: httpx.Client = httpx.Client(
            headers={
                "authority": "query1.finance.yahoo.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,ja;q=0.8",
                "origin": self._YAHOO_FINANCE_URL,
                "user-agent": self._USER_AGENT,
            }
        )

        self._expiry: datetime = datetime(
            1970, 1, 1, tzinfo=datetime.now().astimezone().tzinfo
        )
        self._crumb: str = ""
        self._logger = logging.getLogger(__name__)

    def _refresh_cookies(self) -> None:
        """
        Log into Yahoo! finance.

        Logging in will set the cookies that are required to fetch the crumb and make
        calls to the Yahoo! finance API.
        """

        def _is_eu_consent_redirect(response: httpx.Response) -> bool:
            return (
                "guce.yahoo.com" in response.headers.get("Location", "")
                and response.is_redirect
            )

        self._logger.debug("Logging in...")

        response: httpx.Response = self._client.get(
            self._YAHOO_FINANCE_URL,
            headers=self._COOKIE_HEADERS,
            follow_redirects=False,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.is_error:
                self._logger.exception("Can't log in: %s", e.response)
                return

        cookies: httpx.Cookies = response.cookies

        if _is_eu_consent_redirect(response):
            cookies = self._get_cookies_eu()

        if not any(cookie == "A3" for cookie in cookies):
            self._logger.error("Required cookie not set")
            return

        # Figure out how long the login is valid for.
        # Default expiry is ten years in the future
        expiry: datetime = datetime.now(timezone.utc).astimezone() + timedelta(
            days=3650
        )

        cookie: Cookie
        for cookie in cookies.jar:
            if cookie.domain != ".yahoo.com" or cookie.expires is None:
                continue

            cookie_expiry: datetime = datetime.fromtimestamp(
                cookie.expires, tz=datetime.now().astimezone().tzinfo
            )

            if cookie_expiry >= expiry:
                continue

            self._logger.debug(
                "Cookie %s accepted. Setting expiry to %s",
                cookie.name,
                cookie_expiry.strftime("%Y-%m-%d %H:%M:%S"),
            )
            expiry = cookie_expiry

        self._expiry = expiry

    def _get_cookies_eu(self) -> httpx.Cookies:
        """
        Get cookies from the EU consent page.

        Returns:
            The cookies from the EU consent page.
        """

        response: httpx.Response = self._client.get(
            self._YAHOO_FINANCE_URL, headers=self._COOKIE_HEADERS, follow_redirects=True
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._logger.exception("Can't log in: %s", e.response)
            return httpx.Cookies()

        # Extract the session ID from the redirected request URL
        try:
            session_id: str = response.url.params["sessionId"]
        except (NameError, KeyError):
            self._logger.exception(
                "Unable to extract session id from redirected request URL: '%s'",
                response.url,
            )
            return httpx.Cookies()

        # Find the right URL in the redirect history, and extract the CSRF token
        # from it
        guce_url: httpx.URL = httpx.URL("")
        hist: httpx.Response
        for hist in response.history:
            if hist.url.host == "guce.yahoo.com":
                guce_url = hist.url
                break

        try:
            csrf_token: str = guce_url.params["gcrumb"]
        except (NameError, KeyError):
            self._logger.exception(
                "Unable to extract CSRF token redirected request URL: '%s'",
                response.url,
            )
            return httpx.Cookies()

        # Look in the history to find the right cookie
        gucs_cookie: httpx.Cookies = httpx.Cookies()
        for hist in response.history:
            if hist.cookies.get("GUCS") is not None:
                gucs_cookie = hist.cookies
                break

        if len(gucs_cookie) == 0:
            self._logger.error("No cookies set by finance.yahoo.com")
            return httpx.Cookies()

        referrer_url: str = (
            "https://consent.yahoo.com/v2/collectConsent?sessionId=" + session_id
        )

        consent_headers: dict[str, str] = {
            "origin": "https://consent.yahoo.com",
            "host": "consent.yahoo.com",
            "content-type": "application/x-www-form-urlencoded",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",  # noqa: E501
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br",
            "dnt": "1",
            "referer": referrer_url,
            "user-agent": self._USER_AGENT,
        }

        data = {
            "csrfToken": csrf_token,
            "sessionId": session_id,
            "namespace": "yahoo",
            "agree": "agree",
        }

        response = self._client.post(
            referrer_url,
            headers=consent_headers,
            cookies=gucs_cookie,
            data=data,
            follow_redirects=True,
        )
        for hist in response.history:
            if hist.cookies.get("A3") is not None:
                return hist.cookies

        return httpx.Cookies()

    def _refresh_crumb(self) -> None:
        """Refresh the crumb required to fetch quotes."""

        self._logger.debug("Refreshing crumb...")

        response: httpx.Response = self._client.get(
            self._CRUMB_URL, timeout=self._DEFAULT_HTTP_TIMEOUT
        )
        try:
            response.raise_for_status()
            self._crumb = response.text
        except httpx.HTTPStatusError as e:
            self._logger.exception("Can't fetch crumb: %s", e.response)

        if self._crumb:
            self._logger.debug(
                "Crumb refreshed: %s. Expires on %s",
                self._crumb,
                self._expiry.strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            self._logger.debug("Crumb refresh failed")

    def _execute_request(
        self, api_call: str, query_params: dict[str, str]
    ) -> dict[str, Any]:
        """
        Execute the given request and return the data from the response.

        Args:
            api_call (str): The path to the Yahoo! finance API call (with arguments) to
            create a request for.

            query_params (dict[str, str]): The query parameters to pass along with the
            api call.

        Returns:
            dict[str, Any]: The JSON response.
        """

        self._logger.debug("Executing request: %s", api_call)

        self._client.params = query_params

        response: httpx.Response = self._client.get(
            self._YAHOO_FINANCE_QUERY_URL + api_call, timeout=self._DEFAULT_HTTP_TIMEOUT
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._logger.exception("Request to api failed: %s", e.response)
            return {}

        res_body: str = response.text
        self._logger.debug("Response: %s", res_body)

        if not res_body:
            self._logger.error("Can't parse response")
            return {}

        return json.loads(res_body)

    def prime(self) -> None:
        """Prime the client for use."""

        self._refresh_cookies()
        self._refresh_crumb()

    def call(
        self, api_url: str, query_params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Execute Yahoo! Finance API request with optional query parameters.

        Args:
            api_url (str): The path of the API to call on the Yahoo! Finance API.
            query_params (dict[str, str], optional): The query parameters to pass along
            with the api call. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response.
        """

        self._logger.debug("Calling %s with params %s", api_url, query_params)

        if self._expiry < datetime.now(timezone.utc).astimezone():
            self._refresh_cookies()

        if not self._crumb:
            self._refresh_crumb()

        if query_params is None:
            query_params = {}

        if self._crumb:
            query_params["crumb"] = self._crumb

        return self._execute_request(api_url, query_params)

    def close(self) -> None:
        """Close the client."""
        self._client.close()
