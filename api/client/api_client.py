import logging
import time
from typing import Any, Optional

import requests
from requests.exceptions import ConnectionError, TooManyRedirects

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://automationexercise.com/",
}


class ApiResponse:
    """Thin wrapper around requests.Response for assertions in tests."""

    def __init__(self, response: requests.Response):
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def text(self) -> str:
        return self._response.text

    @property
    def headers(self) -> dict:
        return dict(self._response.headers)

    @property
    def json(self) -> Any:
        return self._response.json()

    @property
    def ok(self) -> bool:
        return self._response.ok


class ApiClient:
    """HTTP transport layer: session, base URL, timeouts, logging."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        # GHA runners may set HTTP(S)_PROXY; trusting env can cause redirect loops.
        self._session.trust_env = False
        self._session.headers.update(DEFAULT_HEADERS)

    def close(self) -> None:
        self._session.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        **kwargs: Any,
    ) -> ApiResponse:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                response = self._session.request(method, url, data=data, params=params, **kwargs)
                logger.debug("%s %s -> %s", method.upper(), url, response.status_code)
                return ApiResponse(response)
            except (TooManyRedirects, ConnectionError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
        if last_error:
            raise last_error
        raise RuntimeError("request failed without response")

    def get(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("DELETE", path, **kwargs)
