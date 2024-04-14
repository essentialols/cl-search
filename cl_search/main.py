from __future__ import annotations

import argparse

from cl_search.categories import VALID_CATEGORIES
from cl_search.craigslist import get_listing_data
from cl_search.craigslist import navigate_to_category
from cl_search.driver import drivers
from cl_search.locations import VALID_LOCATIONS
from cl_search.utils import get_links
from cl_search.write_dataframes import get_export_formats

export_formats = get_export_formats()


def run_script(
    search_query: str,
    browser_arg: str,
    headless_arg: bool,
    image_arg: bool,
    output_arg: str,
    cl_links: str or list,
    category_xpath: str,
    location_arg: str
):
    if output_arg in export_formats:
        function_name, file_extension, file_read = export_formats[output_arg]

    run_times = 0

    for link in cl_links:
        run_times += 1
        print(f"Running Script {run_times}/{len(cl_links)}.")
        driver = navigate_to_category(
            link, search_query, browser_arg, headless_arg, category_xpath
        )

        try:
            get_listing_data(link, driver, image_arg,
                             output_arg, location_arg, search_query)

        except TimeoutError as e:
            print(f"Timeout error occurred for URL: {link}. Error: {e}")

    # this is where we can sum and combine dataframes for outputs that don't append
    if output_arg == "clipboard":
        # send post data to clipboard
        pass

    elif output_arg == "sql":
        print(f"Created craigslist.{file_extension}")

    else:
        print(f"Created {location_arg}.{file_extension}")


def main():
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
        # choices=VALID_CATEGORIES.keys(),
        default="sale",
        help="Category: Select the category to search in.",
    )
    args = parser.parse_args()
    sql = ["sql", "sqlite", "db"]

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

    if output_arg in sql:
        output_arg = "sql"

    if output_arg == 'xlsx':
        output_arg = 'excel'

    run_script(
        search_query,
        browser_arg,
        headless_arg,
        image_arg,
        output_arg,
        cl_links,
        category_xpath,
        location_arg
    )


if __name__ == "__main__":
    main()
