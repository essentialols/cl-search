import pandas as pd
import pytest

from cl_search.class_cl_item import Gallery
from cl_search.utils import parse_url
from cl_search.write_dataframes import df_output
from cl_search.write_dataframes import get_export_formats
from cl_search.write_dataframes import write_frames


@pytest.fixture
def craigslist_posts():
    craigslist_posts = [
        Gallery(
            title="Fisher Price record player",
            price="$35.00",
            timestamp="4h ago",
            location="Kyle",
            post_url="https://austin.craigslist.org/bab/d/kyle-fisher-price-record-player/7711398932.html",
            image_url="No image",
            post_id="7711398932",
            image_path="No image path",
        )
    ]

    return craigslist_posts


def test_get_export_formats(craigslist_posts):
    df = pd.DataFrame([x.as_dict() for x in craigslist_posts])

    get_export_formats(df)


def test_df_output(craigslist_posts):
    link = "https://austin.craigslist.org/"
    city_name = parse_url(link)
    output_arg = "csv"
    location_arg = "austin"
    search_query = "iphone"

    df = pd.DataFrame([x.as_dict() for x in craigslist_posts])

    df_output(city_name, df, location_arg, search_query, output_arg)


def test_write_frames(craigslist_posts):
    link = "https://austin.craigslist.org/"
    output_arg = "csv"
    location_arg = "austin"
    search_query = "iphone"

    write_frames(link, craigslist_posts, location_arg,
                 search_query, output_arg)
