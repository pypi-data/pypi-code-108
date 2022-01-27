import os
from contextlib import asynccontextmanager
from typing import Any, cast

from playwright.async_api import async_playwright
from playwright.sync_api import BrowserContext, sync_playwright

_test_context: BrowserContext | None = None


def playwright_test(*, url: str = '', storage_state: str | None = None):
    global _test_context
    if not _test_context:
        import nest_asyncio
        nest_asyncio.apply()
        os.environ['PWDEBUG'] = 'console'
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, channel='chrome')
        _test_context = browser.new_context(storage_state=cast(str, storage_state))
    page = _test_context.new_page()
    if url:
        page.goto(url)
    return page


@asynccontextmanager
async def playwright_page(
    *,
    browser_kwargs: dict[str, Any] = {},
    context_kwargs: dict[str, Any] = {},
    page_kwargs: dict[str, Any] = {},
):
    '''
    ```py
    browser_kwargs={
        'headless': False,    # 显示浏览器UI
        'channel': 'chrome',  # 使用系统 Chrome 浏览器
    },
    context_kwargs={
        'storage_state': FILE_STATE,
    },
    ```
    '''
    async with async_playwright() as p:
        async with await p.chromium.launch(**browser_kwargs) as browser:
            async with await browser.new_context(**context_kwargs) as context:
                async with await context.new_page(**page_kwargs) as page:
                    yield page


@asynccontextmanager
async def playwright_context(
    *,
    browser_kwargs: dict[str, Any] = {},
    context_kwargs: dict[str, Any] = {},
):
    '''
    ```py
    browser_kwargs={
        'headless': False,    # 显示浏览器UI
        'channel': 'chrome',  # 使用系统 Chrome 浏览器
    },
    context_kwargs={
        'storage_state': FILE_STATE,
    },
    ```
    '''
    async with async_playwright() as p:
        async with await p.chromium.launch(**browser_kwargs) as browser:
            async with await browser.new_context(**context_kwargs) as context:
                yield context


@asynccontextmanager
async def playwright_browser(
    *,
    browser_kwargs: dict[str, Any] = {},
):
    '''
    ```py
    browser_kwargs={
        'headless': False,    # 显示浏览器UI
        'channel': 'chrome',  # 使用系统 Chrome 浏览器
    }
    ```
    '''
    async with async_playwright() as p:
        async with await p.chromium.launch(**browser_kwargs) as browser:
            yield browser
