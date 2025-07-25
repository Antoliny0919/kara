import os

import pytest
from playwright.sync_api import expect, sync_playwright

from kara.accounts.factories import UserFactory

expect.set_options(timeout=5_000)


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir):
    # Skip in playwright tests.
    if settings is not None:
        settings.MEDIA_ROOT = tmpdir.strpath + "/" + settings.MEDIA_ROOT


@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(request, playwright):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    is_headless = request.config.getoption("--headed")
    browser = playwright.chromium.launch(headless=not is_headless)
    yield browser
    browser.close()


@pytest.fixture
def user(db):
    user = UserFactory(username="tester", email="tester@kara.com", password="password")
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def auth_storage_state(live_server, browser, user):
    context = browser.new_context()
    page = context.new_page()

    page.goto(f"{live_server.url}/accounts/login/")
    page.fill("input[name='username']", user.username)
    page.fill("input[name='password']", "password")
    page.click("button[type='submit']")

    page.wait_for_load_state("networkidle")
    storage_state = context.storage_state()
    page.close()
    context.close()

    return storage_state


@pytest.fixture
def auth_page(browser, auth_storage_state, live_server):
    context = browser.new_context(storage_state=auth_storage_state)
    page = context.new_page()

    yield page

    page.close()
    context.close()
