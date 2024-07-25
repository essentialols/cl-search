import pandas as pd
import pytest

from cl_search.class_cl_item import Gallery
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


@pytest.fixture
def test_args():
    args = {
        'search_query': 'iphone',
        'output': 'csv',
        'location': 'austin'
    }

    return args


def test_get_export_formats(craigslist_posts):
    df = pd.DataFrame([x.as_dict() for x in craigslist_posts])

    get_export_formats(df)


def test_df_output(craigslist_posts, test_args):
    df = pd.DataFrame([x.as_dict() for x in craigslist_posts])

    df_output(df, **test_args)


def test_write_frames(craigslist_posts, test_args):
    write_frames(craigslist_posts, **test_args)
