import pytest
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as GeckoOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from cl_search.driver import chrome_driver_preferences
from cl_search.driver import chromium_driver_preferences
from cl_search.driver import close_driver
from cl_search.driver import drivers
from cl_search.driver import edge_driver_preferences
from cl_search.driver import firefox_driver_preferences
from cl_search.driver import get_url
from cl_search.driver import get_webdriver
from cl_search.driver import preferences
from cl_search.driver import safari_driver_preferences
from cl_search.driver import services
from cl_search.driver import set_driver
from cl_search.driver import set_options
from cl_search.driver import set_service


@pytest.fixture
def test_args():
    args = {
        'search_query': 'iphone',
        'output': 'csv',
        'images_mode': False,
        'location': 'austin',
        'browser': 'firefox',
        'headless_mode': False
    }

    return args


def test_get_webdriver(test_args):
    browser = test_args.get("browser")

    use_driver = set_driver(browser)
    options = None

    options = options or set_options(browser, **test_args)
    service = set_service(browser)

    if service:
        driver = use_driver(service=service, options=options)
    elif browser == "safari":
        driver = use_driver(options=options)
    else:
        driver = None

    assert (
        isinstance(get_webdriver(**test_args), type(driver))
        and driver is not None
    )
    close_driver(driver)


def test_set_driver(test_args):
    browser = test_args.get("browser")
    assert set_driver(browser) == drivers[browser]


def test_set_options(test_args):
    browser = test_args.get("browser")
    headless = test_args.get("headless_mode")

    try:
        if browser in preferences:
            assert set_options(browser, headless) == preferences[browser](headless)

    except Exception:
        print(f"{browser} is not supported")


def test_set_service(test_args):
    browser = test_args.get("browser")
    if browser in services:
        service_instance = services[browser]()
        assert isinstance(set_service(browser), type(service_instance))


def test_chrome_driver_preferences(test_args):
    headless = test_args.get("headless_mode")
    chrome_options_instance = ChromeOptions()
    assert isinstance(
        chrome_driver_preferences(headless), type(chrome_options_instance)
    )


def test_firefox_driver_preferences(test_args):
    headless = test_args.get("headless_mode")
    firefox_options_instance = GeckoOptions()
    assert isinstance(
        firefox_driver_preferences(headless), type(firefox_options_instance)
    )


def test_safari_driver_preferences(test_args):
    headless = test_args.get("headless_mode")
    safari_options_instance = SafariOptions()
    assert isinstance(
        safari_driver_preferences(headless), type(safari_options_instance)
    )


def test_edge_driver_preferences(test_args):
    headless = test_args.get("headless_mode")
    edge_options_instance = EdgeOptions()
    assert isinstance(edge_driver_preferences(headless), type(edge_options_instance))


def test_chromium_driver_preferences(test_args):
    headless = test_args.get("headless_mode")
    chromium_options_instance = ChromiumOptions()
    assert isinstance(
        chromium_driver_preferences(headless), type(chromium_options_instance)
    )


def test_get_url(test_args):
    browser = test_args.get("browser")
    driver = get_webdriver(browser, **test_args)
    url = "https://kent.craigslist.org/"
    get_url(driver, url)
    close_driver(driver)


def test_close_driver(test_args):
    browser = test_args.get("browser")
    driver = get_webdriver(browser, **test_args)
    if driver:
        close_driver(driver)
