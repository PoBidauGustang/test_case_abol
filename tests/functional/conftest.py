import contextlib
import json
from json import JSONDecodeError
from typing import Any

import aiohttp
import pytest

from tests.functional.settings import settings

pytest_plugins = (
    "tests.functional.fixtures.connections",
    "tests.functional.fixtures.db_operations",
)


@pytest.fixture
def make_request(http_session: aiohttp.ClientSession):
    async def inner(
        method: str,
        path: str,
        query_data: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, int, aiohttp.CookieJar]:
        url = f"http://{settings.get_api_host}/book/v1{path}"

        if cookies:
            http_session.cookie_jar.update_cookies(cookies)

        if data:
            async with http_session.request(
                method,
                url,
                params=query_data,
                data=data,
                cookies=cookies,
                headers=headers,
            ) as response:
                response_body = await response.read()
        else:
            async with http_session.request(
                method,
                url,
                params=query_data,
                json=body,
                cookies=cookies,
                headers=headers,
            ) as response:
                response_body = await response.read()

        with contextlib.suppress(JSONDecodeError):
            response_body = json.loads(response_body)

        status = response.status
        response_cookies = response.cookies

        http_session.cookie_jar.clear()

        return response_body, status, response_cookies

    return inner


@pytest.fixture
def make_get_request(make_request):
    async def inner(
        path: str,
        query_data: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, int, aiohttp.CookieJar]:
        return await make_request(
            "GET", path, query_data=query_data, cookies=cookies, headers=headers
        )

    return inner


@pytest.fixture
def make_post_request(make_request):
    async def inner(
        path: str,
        query_data: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, int, aiohttp.CookieJar]:
        return await make_request(
            "POST",
            path,
            query_data=query_data,
            body=body,
            data=data,
            cookies=cookies,
            headers=headers,
        )

    return inner


@pytest.fixture
def make_patch_request(make_request):
    async def inner(
        path: str,
        query_data: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, int, aiohttp.CookieJar]:
        return await make_request(
            "PATCH",
            path,
            query_data=query_data,
            body=body,
            cookies=cookies,
            headers=headers,
        )

    return inner


@pytest.fixture
def make_delete_request(make_request):
    async def inner(
        path: str,
        query_data: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, int, aiohttp.CookieJar]:
        return await make_request(
            "DELETE",
            path,
            query_data=query_data,
            body=body,
            cookies=cookies,
            headers=headers,
        )

    return inner
