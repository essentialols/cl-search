import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cl_search.driver import close_driver
from cl_search.driver import get_url
from cl_search.driver import get_webdriver
from cl_search.utils import get_current_time
from cl_search.utils import parse_url
from cl_search.utils import selectors

current_time = get_current_time()


def navigate_to_category(
    link: str, search_query: str, browser_arg: str, headless_arg: bool, category_xpath
) -> webdriver:
    city_name = parse_url(link)
    driver = get_webdriver(browser_arg, headless_arg)
    wait = WebDriverWait(driver, 60)
    get_url(driver, link)

    print(f"Fetching {search_query}s from {city_name.capitalize()} Craigslist...")

    category = wait.until(
        EC.visibility_of_element_located((By.XPATH, f"{category_xpath}"))
    )
    category.click()
    search_field = wait.until(
        EC.visibility_of_element_located((By.XPATH, selectors["selectors"]["search"]))
    )

    if search_query:
        search_field.clear()
        search_field.send_keys(search_query)
        search_field.send_keys(Keys.ENTER)
    wait.until(
        EC.visibility_of_element_located((By.XPATH, selectors["selectors"]["results"]))
    )

    # result_options = wait.until(EC.visibility_of_element_located((By.XPATH, selectors['selectors']['result_options']['box_button'])))
    # result_options.click()

    # result_list = wait.until(EC.visibility_of_element_located((By.XPATH, selectors['selectors']['result_options']['list'])))
    # result_list.click()
    # wait.until(EC.visibility_of_element_located((By.XPATH, selectors['selectors']['results'])))

    return driver


def get_listing_data(driver: webdriver) -> dict:
    posts_data = []
    scraped_img_tag_src = set()
    to_stop = False
    current_page = 0
    total_items = 0

    scroll_pause_time = 1.4  # find a method to wait for images to load
    scroll_offset = 1000
    actions = ActionChains(driver)

    while not to_stop:  # write custom actions for Preview
        while True:
            prev_url = driver.current_url
            prev_gallery = prev_url.split("#")[1] if "#" in prev_url else None
            actions.scroll_by_amount(0, scroll_offset).perform()
            time.sleep(scroll_pause_time)
            current_url = driver.current_url
            current_gallery = current_url.split("#")[1] if "#" in current_url else None
            if current_gallery == prev_gallery:
                break
        search_results = driver.find_element(
            By.XPATH, selectors["selectors"]["results"]
        )
        soup = BeautifulSoup(search_results.get_attribute("innerHTML"), "html.parser")
        for div in soup.find_all("li", {"class": "cl-search-result"}):
            img_tag = div.find("img")
            if img_tag:
                img_tag_src = img_tag.get("src")
                if img_tag_src not in scraped_img_tag_src:
                    posts_data.extend(div)
                    scraped_img_tag_src.add(img_tag_src)
            else:
                post_url = div.find("a", {"class": "posting-title"})
                if post_url:
                    img_tag_src = post_url.get("href")
                    if img_tag_src not in scraped_img_tag_src:
                        posts_data.extend(div)
                        scraped_img_tag_src.add(img_tag_src)

        page_num = driver.find_element(By.CLASS_NAME, "cl-page-number").text
        pattern = r"([\d,]+)\s*of\s*([\d,]+)"
        match = re.search(pattern, page_num)
        if match:
            current_page = int(match.group(1).replace(",", ""))
            total_items = int(match.group(2).replace(",", ""))
        if posts_data == []:
            driver.close()
            raise NoSuchElementException(
                "No listings found on the page. Check if the page loaded properly."
            )

        try:
            driver.execute_script("window.scrollTo(0, 0)")
            button_next = driver.find_element(By.XPATH, selectors["selectors"]["next"])
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

    print("Collected {0} listings".format(len(posts_data)))
    close_driver(driver)

    return posts_data
