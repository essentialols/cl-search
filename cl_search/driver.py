from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.service import ChromiumService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as GeckoOptions
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.safari.options import Options as SafariOptions

from cl_search.utils import selectors


def get_webdriver(webdriver: str = "firefox", **kwargs) -> webdriver:
    driver_options = kwargs.get("driver_options", None)

    use_driver = set_driver(webdriver)
    options = driver_options or set_options(webdriver, **kwargs)
    service = set_service(webdriver)

    if service:
        driver = use_driver(service=service, options=options)

    else:
        driver = use_driver(options=options)

    driver.implicitly_wait(9)
    driver.set_window_size(1280, 1000)

    return driver


def set_driver(webdriver: str) -> webdriver:
    if webdriver in drivers:
        return drivers[webdriver]


def set_options(webdriver: str, **kwargs):
    headless_mode = kwargs.get("headless_mode", False)

    try:
        if webdriver in preferences:
            return preferences[webdriver](headless_mode)

    except Exception:
        print(f"{webdriver} is not supported")


def set_service(webdriver: str):
    if webdriver in services:
        return services[webdriver]()

    return None


def chrome_driver_preferences(headless_mode: bool) -> ChromeOptions:
    user_agent = selectors["user_agent"]

    options = ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")

    if headless_mode is True:
        options.add_argument("-headless")

    return options


def firefox_driver_preferences(headless_mode: bool) -> GeckoOptions:
    user_agent = selectors["user_agent"]

    options = GeckoOptions()
    options.set_preference("general.useragent.override", user_agent)
    options.set_preference("permissions.default.desktop-notification", 2)

    if headless_mode is True:
        options.add_argument("-headless")

    return options


def safari_driver_preferences(headless_mode: bool) -> SafariOptions:
    user_agent = selectors["user_agent"]

    options = SafariOptions()
    options.add_argument(f"--user-agent={user_agent}")

    if headless_mode is True:
        options.add_argument("-headless")

    return options


def edge_driver_preferences(headless_mode: bool) -> EdgeOptions:
    user_agent = selectors["user_agent"]

    options = EdgeOptions()
    options.add_argument(f"--user-agent={user_agent}")

    if headless_mode is True:
        options.add_argument("-headless")

    return options


def chromium_driver_preferences(headless_mode: bool) -> ChromeOptions:
    user_agent = selectors["user_agent"]

    options = ChromiumOptions()
    options.add_argument(f"--user-agent={user_agent}")

    if headless_mode is True:
        options.add_argument("-headless")

    return options


drivers = {
    "chrome": webdriver.Chrome,
    "firefox": webdriver.Firefox,
    "safari": webdriver.Safari,
    "edge": webdriver.ChromiumEdge,
    "chromium": webdriver.chromium.webdriver.ChromiumDriver,
}

preferences = {
    "chrome": chrome_driver_preferences,
    "firefox": firefox_driver_preferences,
    "safari": safari_driver_preferences,
    "edge": edge_driver_preferences,
    "chromium": chromium_driver_preferences,
}

services = {
    "chrome": lambda: ChromeService(),
    "firefox": lambda: GeckoService(),
    "edge": lambda: EdgeService(),
    "chromium": lambda: ChromiumService(),
}


def get_url(driver: webdriver, url: str) -> None:
    page_load_timeout = 60

    try:
        driver.set_page_load_timeout(page_load_timeout)
        driver.get(url)

    except TimeoutException as e:
        close_driver(driver)
        raise TimeoutError(f"Selenium timed out waiting for page to load: {e}")


def close_driver(driver: webdriver = None) -> None:
    window_handles = driver.window_handles
    if driver:
        for handle in window_handles:
            driver.switch_to.window(handle)
            driver.close()
        driver.quit()
