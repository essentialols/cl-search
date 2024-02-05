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


def test_get_webdriver():
    browser = "firefox"
    use_driver = set_driver(browser)
    headless = False
    options = None

    options = options or set_options(browser, headless)
    service = set_service(browser)

    if service:
        driver = use_driver(service=service, options=options)
    elif browser == "safari":
        driver = use_driver(options=options)
    else:
        driver = None

    assert (
        isinstance(get_webdriver(browser, headless, options), type(driver))
        and driver is not None
    )
    close_driver(driver)


def test_set_driver():
    browser = "firefox"
    assert set_driver(browser) == drivers[browser]


def test_set_options():
    browser = "firefox"
    headless = False
    try:
        if browser in preferences:
            assert set_options(browser, headless) == preferences[browser](headless)

    except Exception:
        print(f"{browser} is not supported")


def test_set_service():
    browser = "firefox"
    if browser in services:
        service_instance = services[browser]()
        assert isinstance(set_service(browser), type(service_instance))


def test_chrome_driver_preferences():
    headless = False
    chrome_options_instance = ChromeOptions()
    assert isinstance(
        chrome_driver_preferences(headless), type(chrome_options_instance)
    )


def test_firefox_driver_preferences():
    headless = False
    firefox_options_instance = GeckoOptions()
    assert isinstance(
        firefox_driver_preferences(headless), type(firefox_options_instance)
    )


def test_safari_driver_preferences():
    headless = False
    safari_options_instance = SafariOptions()
    assert isinstance(
        safari_driver_preferences(headless), type(safari_options_instance)
    )


def test_edge_driver_preferences():
    headless = False
    edge_options_instance = EdgeOptions()
    assert isinstance(edge_driver_preferences(headless), type(edge_options_instance))


def test_chromium_driver_preferences():
    headless = False
    chromium_options_instance = ChromiumOptions()
    assert isinstance(
        chromium_driver_preferences(headless), type(chromium_options_instance)
    )


def test_get_url():
    browser = "firefox"
    headless = False
    options = None
    driver = get_webdriver(browser, headless, options)
    url = "https://kent.craigslist.org/"
    driver.get(url)
    close_driver(driver)


def test_close_driver():
    browser = "firefox"
    headless = False
    options = None
    driver = get_webdriver(browser, headless, options)
    if driver:
        close_driver(driver)
