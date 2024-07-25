import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from cl_search.class_cl_item import identify_cl_item_type
from cl_search.driver import close_driver
from cl_search.driver import get_url
from cl_search.driver import get_webdriver
from cl_search.utils import get_city_name
from cl_search.utils import get_current_time
from cl_search.utils import selectors


current_time = get_current_time()


def navigate_to_category(link: str, **kwargs) -> webdriver:
    search_query = kwargs.get("search_query", None)
    category_choice = kwargs.get("category_choice")
    detailed_mode = kwargs.get("detailed_mode", False)

    city_name = get_city_name(link)
    driver = get_webdriver(**kwargs)
    wait = WebDriverWait(driver, 60)
    get_url(driver, link)

    tqdm.write(
        f"Fetching {search_query} from {city_name.capitalize()} Craigslist...")

    category = wait.until(
        EC.visibility_of_element_located((By.XPATH, f"{category_choice}"))
    )
    category.click()
    search_field = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, selectors["selectors"]["search"]))
    )

    if search_query:
        search_field.clear()
        search_field.send_keys(search_query)
        search_field.send_keys(Keys.ENTER)
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, selectors["selectors"]["results"]))
    )

    if detailed_mode is True:
        result_options = wait.until(EC.visibility_of_element_located(
            (By.XPATH, selectors['selectors']['result_options']['box_button'])))
        result_options.click()

        result_list = wait.until(EC.visibility_of_element_located(
            (By.XPATH, selectors['selectors']['result_options']['list'])))
        result_list.click()
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, selectors['selectors']['results'])))

    # add a time sleep if your internet is slow
    time.sleep(5)

    return driver


def wait_for_images(driver: webdriver, timeout=15) -> None:
    try:
        driver.implicitly_wait(timeout)

        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )

        time.sleep(.5)

    except TimeoutException:
        print("Images did not load within the timeout period")


def get_listing_data(link: str, driver: webdriver, **kwargs) -> None:
    to_stop = False
    current_page = 0
    total_items = 0
    post_data = []

    scroll_offset = 1000
    actions = ActionChains(driver)

    # write custom actions for Preview (detailed)

    while not to_stop:
        while True:
            prev_url = driver.current_url
            prev_gallery = prev_url.split("#")[1] if "#" in prev_url else None
            actions.scroll_by_amount(0, scroll_offset).perform()
            wait_for_images(driver)
            current_url = driver.current_url
            current_gallery = current_url.split(
                "#")[1] if "#" in current_url else None
            if current_gallery == prev_gallery:
                break
        search_results = driver.find_element(
            By.XPATH, selectors["selectors"]["results"]
        )

        soup = BeautifulSoup(search_results.get_attribute("innerHTML"), "html.parser")
        results = [data for data in soup.find_all("li", {"class": "cl-search-result"}) if not data.find("div", "spacer")]

        cl_data = identify_cl_item_type(link, results, **kwargs)
        post_data.extend(cl_data)

        page_num = driver.find_element(By.CLASS_NAME, "cl-page-number").text
        pattern = r"([\d,]+)\s*of\s*([\d,]+)"
        match = re.search(pattern, page_num)
        if match:
            current_page = int(match.group(1).replace(",", ""))
            total_items = int(match.group(2).replace(",", ""))

        try:
            driver.execute_script("window.scrollTo(0, 0)")
            button_next = driver.find_element(
                By.XPATH, selectors["selectors"]["next"])
            button_next.click()
            time.sleep(1)
            if current_page == total_items:
                to_stop = True
            else:
                to_stop = False

        except ElementNotInteractableException:
            to_stop = True

        except NoSuchElementException as e:
            print(f"Error: {e}")
            break

    close_driver(driver)

    return post_data
