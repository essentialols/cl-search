from __future__ import annotations

import argparse

from class_cl_item import identify_cl_item_type
from driver import VALID_DRIVERS
from for_sale import get_listing_data
from for_sale import navigate_to_category
from for_sale import write_the_data_frames
from locations import VALID_LOCATIONS
from utils import get_export_formats
from utils import get_links

# VALID_CATEGORIES = ''
export_formats = get_export_formats()


def run_script(
    search_query, browser_arg, headless_arg, image_arg, output_arg, cl_links
):
    run_times = 0
    for link in cl_links:
        run_times += 1
        print(f"Running Script {run_times}/{len(cl_links)}.")
        driver = navigate_to_category(link, search_query, browser_arg, headless_arg)
        posts_data = get_listing_data(driver)
        craigslist_posts = identify_cl_item_type(link, posts_data, image_arg)
        write_the_data_frames(link, craigslist_posts, image_arg, output_arg)


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
        choices=export_formats.keys(),
        default="csv",
        help="Output: CSV, EXCEL, ETC",
    )
    parser.add_argument(
        "-b",
        "--browser",
        choices=VALID_DRIVERS,
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
    # parser.add_argument("-C", "--category", choices=VALID_CATEGORIES, default='sss', help="Category: Where are you searching")
    args = parser.parse_args()

    location_arg = args.location
    output_arg = args.output
    browser_arg = args.browser
    headless_arg = args.headless
    search_query = args.search
    image_arg = args.image
    # category_arg = args.category

    cl_links = get_links(location_arg, VALID_LOCATIONS)

    if cl_links == []:
        raise argparse.ArgumentTypeError(f"Invalid location: {location_arg}")

    run_script(search_query, browser_arg, headless_arg, image_arg, output_arg, cl_links)
