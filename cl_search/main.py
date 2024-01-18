from __future__ import annotations

import argparse

from categories import VALID_CATEGORIES
from class_cl_item import identify_cl_item_type
from craigslist import get_listing_data
from craigslist import navigate_to_category
from driver import drivers
from locations import VALID_LOCATIONS
from utils import get_links
from write_dataframes import get_export_formats
from write_dataframes import write_frames

export_formats = get_export_formats()


def run_script(
    search_query,
    browser_arg,
    headless_arg,
    image_arg,
    output_arg,
    cl_links,
    category_xpath,
):
    run_times = 0
    for link in cl_links:
        run_times += 1
        print(f"Running Script {run_times}/{len(cl_links)}.")
        driver = navigate_to_category(
            link, search_query, browser_arg, headless_arg, category_xpath
        )
        posts_data = get_listing_data(driver)
        craigslist_posts = identify_cl_item_type(link, posts_data, image_arg)
        write_frames(link, craigslist_posts, image_arg, output_arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-L",
        "--location",
        action="store",
        type=str,
        default="",
        required=True,
        help="Location: Choose a URL, City Name, State / Province, Country, or Continent",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str.lower,
        choices=export_formats.keys(),
        default="csv",
        help="Output: CSV, EXCEL, ETC",
    )
    parser.add_argument(
        "-b",
        "--browser",
        type=str.lower,
        choices=drivers.keys(),
        default="firefox",
        help="Driver: Firefox, Chrome, Safari, Chromium",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Headless mode: True or False",
    )
    parser.add_argument(
        "-s",
        "--search",
        action="store",
        type=str,
        default="",
        help="Search query: Whatcha lookin for?",
    )
    parser.add_argument(
        "-i",
        "--image",
        action="store_true",
        default=False,
        help="Images: Download images",
    )
    parser.add_argument(
        "-C",
        "--category",
        type=str.lower,
        choices=VALID_CATEGORIES.keys(),
        default="sale",
        help="Category: Select the category to search in.",
    )
    args = parser.parse_args()

    location_arg = args.location
    output_arg = args.output
    browser_arg = args.browser
    headless_arg = args.headless
    search_query = args.search
    image_arg = args.image
    category_arg = args.category

    cl_links = get_links(location_arg, VALID_LOCATIONS)

    if category_arg in VALID_CATEGORIES:
        category_xpath = VALID_CATEGORIES[category_arg]

    if cl_links == []:
        raise argparse.ArgumentTypeError(f"Invalid location: {location_arg}")

    run_script(
        search_query,
        browser_arg,
        headless_arg,
        image_arg,
        output_arg,
        cl_links,
        category_xpath,
    )
