import os
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
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cl_search.class_cl_item import identify_cl_item_type
from cl_search.driver import close_driver
from cl_search.driver import get_url
from cl_search.driver import get_webdriver
from cl_search.utils import get_current_time
from cl_search.utils import parse_post_id
from cl_search.utils import parse_url
from cl_search.utils import project_path
from cl_search.utils import selectors
from cl_search.write_dataframes import get_default_options
from cl_search.write_dataframes import get_export_formats
from cl_search.write_dataframes import write_frames
# import pandas as pd


current_time = get_current_time()


def navigate_to_category(
    link: str, search_query: str, browser_arg: str, headless_arg: bool, category_xpath: str, detailed: bool = False
) -> webdriver:
    city_name = parse_url(link)
    driver = get_webdriver(browser_arg, headless_arg)
    wait = WebDriverWait(driver, 60)
    get_url(driver, link)

    print(
        f"Fetching {search_query}s from {city_name.capitalize()} Craigslist...")

    category = wait.until(
        EC.visibility_of_element_located((By.XPATH, f"{category_xpath}"))
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

    if detailed is True:
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

    # explicit wait strategy
    # change to this method if image_url_src.strip errors
    # time.sleep(1.5)

    try:
        driver.implicitly_wait(timeout)

        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )

        time.sleep(.5)

    except TimeoutException:
        print("Images did not load within the timeout period")


def get_listing_data(link: str, driver: webdriver, image_arg: bool, output_arg: str, location_arg: str, search_query: str) -> None:
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

        parse_results(search_results, link, image_arg,
                      output_arg, location_arg, search_query)

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

    # if output_arg == "clipboard":
    #     return post_data


def parse_results(search_results: WebElement, link: str, image_arg: bool, output_arg: str, location_arg: str, search_query: str):
    export_formats = get_export_formats()
    default_options = get_default_options()
    sheets = f"{project_path}/sheets"

    if output_arg in export_formats:
        function_name, file_extension, file_read = export_formats[output_arg]

    if output_arg in default_options:
        write_options, append_options, read_options = default_options[output_arg]

    soup = BeautifulSoup(search_results.get_attribute(
        "innerHTML"), "html.parser")
    for data in soup.find_all("li", {"class": "cl-search-result"}):
        if data.find("div", "spacer"):
            continue

        post_url = (data.find("a", "posting-title").get("href")
                    if data.find("a", "posting-title") else "")
        post_id = parse_post_id(post_url)

        if output_arg == "clipboard":
            # check if post_id exists inside post_data
            # post_data.extend(data)
            pass

        elif output_arg == 'sql':
            craigslist_posts = identify_cl_item_type(link, data, image_arg)
            write_frames(link, craigslist_posts, location_arg,
                         search_query, output_arg)

        else:
            output_file = f"{sheets}/{location_arg}_{search_query}.{file_extension}"

            if os.path.isfile(output_file):
                file = file_read(output_file, **read_options)
                existing_data = file[file['post_id'].astype(
                    str).str.contains(post_id)]
                if not existing_data.empty:
                    pass
                    # update / merge outdated data
                    # post_data = identify_cl_item_type(link, data, image_arg)
                    # post_data_df = pd.DataFrame([x.as_dict() for x in post_data])
                    # merged_data = pd.merge(file, post_data_df, on='post_id', how='left', suffixes=('_existing', '_new'))
                    # for col in file.columns:
                    #   merged_data[col] = merged_data[f"{col}_new"].fillna(merged_data[f"{col}_existing"])
                    #   merged_data.drop(columns=[f"{col}_existing" for col in file.columns] + [f"{col}_new" for col in post_data_df.columns], inplace=True)
                    # write_frames(link, post_data, location_arg, search_query, output_arg)

                else:
                    craigslist_posts = identify_cl_item_type(
                        link, data, image_arg)
                    write_frames(link, craigslist_posts,
                                 location_arg, search_query, output_arg)

            else:
                craigslist_posts = identify_cl_item_type(link, data, image_arg)
                write_frames(link, craigslist_posts, location_arg,
                             search_query, output_arg, write_options)
