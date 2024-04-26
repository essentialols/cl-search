import os
import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cl_search.class_cl_item import identify_cl_item_type
from cl_search.driver import close_driver
from cl_search.driver import get_url
from cl_search.driver import get_webdriver
from cl_search.utils import get_city_name
from cl_search.utils import get_current_time
from cl_search.utils import parse_post_id
from cl_search.utils import project_path
from cl_search.utils import selectors
from cl_search.write_dataframes import df_output
from cl_search.write_dataframes import get_default_options
from cl_search.write_dataframes import write_frames


current_time = get_current_time()


def navigate_to_category(link: str, **kwargs) -> webdriver:
    search_query = kwargs.get("search_query", None)
    category_choice = kwargs.get("category_choice")
    detailed_mode = kwargs.get("detailed_mode", False)

    city_name = get_city_name(link)
    driver = get_webdriver(**kwargs)
    wait = WebDriverWait(driver, 60)
    get_url(driver, link)

    print(
        f"Fetching {search_query}s from {city_name.capitalize()} Craigslist...")

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
    # post_data = []

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

        parse_results(search_results, link, **kwargs)

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

    # if output == "clipboard":
    #     return post_data


def parse_results(search_results: WebElement, link: str, **kwargs):
    output = kwargs.get("output", "csv").lower()
    location = kwargs.get("location")
    file_extension = kwargs.get("file_extension")
    search_query = kwargs.get("search_query", None)
    file_read = kwargs.get("file_read")

    default_options = get_default_options()
    sheets = f"{project_path}/sheets"

    if output in default_options:
        write_options, append_options, read_options = default_options[output]

    soup = BeautifulSoup(search_results.get_attribute("innerHTML"), "html.parser")
    for data in soup.find_all("li", {"class": "cl-search-result"}):
        if data.find("div", "spacer"):
            continue

        post_url = (data.find("a", "posting-title").get("href")
                    if data.find("a", "posting-title") else "")
        post_id = parse_post_id(post_url)

        if output == "clipboard":
            # check if post_id exists inside post_data
            # post_data.extend(data)
            pass

        elif output == 'sql':
            craigslist_posts = identify_cl_item_type(link, data, **kwargs)
            write_frames(link, craigslist_posts, **kwargs)

        else:
            output_file = f"{sheets}/{location}_{search_query}.{file_extension}"

            if os.path.isfile(output_file):
                file = file_read(output_file, **read_options)
                existing_data = file[file['post_id'].astype(
                    str).str.contains(post_id)]
                if not existing_data.empty:
                    post_data = identify_cl_item_type(link, data, **kwargs)

                    city_name = get_city_name(link)
                    source_name = f"craigslist_{city_name}"

                    post_data_df = pd.DataFrame([x.as_dict() for x in post_data])
                    post_data_df.insert(0, "last_updated", current_time)
                    post_data_df.insert(0, "time_added", current_time)
                    post_data_df.insert(0, "is_new", 0)
                    post_data_df.insert(0, "source", f"{source_name}")
                    post_data_df.dropna(inplace=True)

                    columns_to_update = ["is_new", "last_updated", "title",
                                         "price", "timestamp", "location",
                                         "image_url", "image_path"]

                    for col in columns_to_update:
                        file.loc[existing_data.index, col] = post_data_df[col].values

                    df_output(city_name, file, write_options, **kwargs)

                else:
                    craigslist_posts = identify_cl_item_type(link, data, **kwargs)
                    write_frames(link, craigslist_posts, **kwargs)

            else:
                craigslist_posts = identify_cl_item_type(link, data, **kwargs)
                write_frames(link, craigslist_posts, write_options, **kwargs)
