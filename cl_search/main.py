from __future__ import annotations

import argparse

from cl_search.categories import VALID_CATEGORIES
from cl_search.craigslist import get_listing_data
from cl_search.craigslist import navigate_to_category
from cl_search.driver import drivers
from cl_search.locations import VALID_LOCATIONS
from cl_search.utils import get_links
from cl_search.write_dataframes import get_export_formats


def main(**kwargs) -> None:
    output = kwargs.get("output", "csv")
    location_links = kwargs.get("location_links")
    location = kwargs.get("location", "")
    file_extension = kwargs.get("file_extension", "")
    search_query = kwargs.get("search_query", "")

    count = 0

    for link in location_links:
        count += 1
        print(f"Running Script {count}/{len(location_links)}.")
        driver = navigate_to_category(link, **kwargs)

        try:
            get_listing_data(link, driver, **kwargs)

        except TimeoutError as e:
            print(f"Timeout error occurred for URL: {link}. Error: {e}")

    if output == "clipboard":
        # send post data to clipboard
        print("Data is ready to paste")

    elif output == "sql":
        print(f"Created craigslist.{file_extension}")

    else:
        if search_query:
            print(f"Created {location}_{search_query}.{file_extension}")
        else:
            print(f"Created {location}.{file_extension}")


def parse_my_args() -> dict:
    export_formats = get_export_formats()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-L",
        "--location",
        action="store",
        type=str,
        default="",
        required=True,
        help="Location: URL, City, State, Province, Country, or Continent.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str.lower,
        choices=export_formats.keys(),
        default="csv",
        help="Output: CSV, JSON, EXCEL or SQL",
    )
    parser.add_argument(
        "-b",
        "--browser",
        type=str.lower,
        choices=drivers.keys(),
        default="firefox",
        help="Driver: Firefox, Chrome, Safari, Chromium, or Edge.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Headless mode",
    )
    parser.add_argument(
        "-s",
        "--search",
        action="store",
        type=str.lower,
        default="",
        help="Search query: Whatcha lookin for?",
    )
    parser.add_argument(
        "-i",
        "--image",
        action="store_true",
        default=False,
        help="Download images",
    )
    parser.add_argument(
        "-C",
        "--category",
        type=str.lower,
        # choices=VALID_CATEGORIES.keys(),
        default="sale",
        help="Category: Select the category to search in.",
    )
    parser.add_argument(
        "path",
        type=str,
        nargs="?",
        help="Custom Output path",
    )
    parser.add_argument(
        "-D",
        "--delete",
        action="store_true",
        default=False,
        help="Remove old data from SQL Tables",
    )
    parser.add_argument(
        "-d",
        "--detailed",
        action="store_true",
        default=False,
        help="Use Detailed to get the most data possible",
    )
    parser.add_argument(
        "-do",
        "--driver-options",
        type=str,
        default="",
        help="Custom driver options",
    )
    args = parser.parse_args()
    sql = ["sql", "sqlite", "db"]

    location = args.location
    output = args.output
    browser = args.browser
    headless_mode = args.headless
    search_query = args.search
    images_mode = args.image
    category = args.category
    # output_path = args.path
    delete_mode = args.delete
    # detailed_mode = args.detailed
    # driver_options = args.driver_options

    location_links = get_links(location, VALID_LOCATIONS)

    if category in VALID_CATEGORIES:
        category_choice = VALID_CATEGORIES[category]

    if location_links == []:
        raise argparse.ArgumentTypeError(f"Invalid location: {location}")

    if output in sql:
        output = "sql"

    if output == 'xlsx':
        output = 'excel'

    if output in export_formats:
        function_name, file_extension, file_read = export_formats[output]

    return {
        'search_query': search_query,
        'browser': browser,
        'headless_mode': headless_mode,
        'images_mode': images_mode,
        'output': output,
        'location_links': location_links,
        'category_choice': category_choice,
        'location': location,
        # 'output_path': output_path,
        'delete_mode': delete_mode,
        # 'detailed_mode': detailed_mode,
        # 'driver_options': driver_options,
        'function_name': function_name,
        'file_extension': file_extension,
        'file_read': file_read
    }


def run() -> None:
    args = parse_my_args()
    main(**args)


# does not run as __main__ and I dont know why
if __name__ == '__main__':
    run()
