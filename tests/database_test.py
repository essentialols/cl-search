import os

import pandas as pd
import pytest

from cl_search.class_cl_item import Gallery
from cl_search.database import create_session
from cl_search.database import insert_data_sources
from cl_search.database import insert_images
from cl_search.database import insert_listings
from cl_search.database import insert_sources
from cl_search.database import query_post_id
from cl_search.database import setup_database
from cl_search.database import update_listings
from cl_search.utils import get_current_time
from cl_search.utils import project_path


@pytest.fixture
def db_name():
    db_name = "temp/test.db"

    return db_name


@pytest.fixture
def df_sample():
    post_data = [
        Gallery(
            title="Fisher Price record player",
            price="$35.00",
            timestamp="4h ago",
            location="Kyle",
            post_url="https://austin.craigslist.org/bab/d/kyle-fisher-price-record-player/7711398932.html",
            image_url="https://images.craigslist.org/00E0E_1bVJbS06Bxv_600x450.jpg",
            post_id="7711398932",
            image_path="No image path"
        )
    ]

    current_time = get_current_time()
    source_name = "craigslist_austin"

    df_sample = pd.DataFrame([x.as_dict() for x in post_data])
    df_sample.insert(0, "time_added", current_time)
    df_sample.insert(0, "is_new", "1")
    df_sample.insert(0, "source", f"{source_name}")
    df_sample.dropna(inplace=True)

    return df_sample


@pytest.fixture
def sample_update():
    post_data = [
        Gallery(
            title="Fisher Price record player w/ vinyl",
            price="$55.00",
            timestamp="4/12",
            location="Kyle",
            post_url="https://austin.craigslist.org/bab/d/kyle-fisher-price-record-player/7711398932.html",
            image_url="https://images.craigslist.org/00r0r_9BoniKEYXBS_0CI0t2_600x450.jpg",
            post_id="7711398932",
            image_path="tests/test.jpg"
        )
    ]

    current_time = get_current_time()
    source_name = "craigslist_austin"

    df_sample = pd.DataFrame([x.as_dict() for x in post_data])
    df_sample.insert(0, "time_added", current_time)
    df_sample.insert(0, "is_new", "1")
    df_sample.insert(0, "source", f"{source_name}")
    df_sample.dropna(inplace=True)

    return df_sample


def delete_test_db(db_name: str = db_name) -> None:
    test_db_path = f'{project_path}/{db_name}'

    if os.path.isfile(test_db_path):
        os.remove(test_db_path)


def test_setup_database(db_name):
    setup_database(db_name)

    delete_test_db(db_name)


def test_create_session(db_name):

    setup_database(db_name)
    create_session(db_name)

    delete_test_db(db_name)


def test_insert_listings(db_name, df_sample):
    connection = setup_database(db_name)

    for index, row in df_sample.iterrows():
        insert_listings(connection, row)

    delete_test_db(db_name)


def test_insert_data_sources(db_name, df_sample):
    connection = setup_database(db_name)

    for index, row in df_sample.iterrows():
        insert_listings(connection, row)
        insert_sources(connection, row)
        insert_data_sources(connection, row)

    delete_test_db(db_name)


def test_insert_sources(db_name, df_sample):
    connection = setup_database(db_name)

    for index, row in df_sample.iterrows():
        insert_sources(connection, row)

    delete_test_db(db_name)


# write sample for previews coverage
def test_insert_images(db_name, df_sample):
    connection = setup_database(db_name)

    for index, row in df_sample.iterrows():
        insert_listings(connection, row)
        insert_images(connection, row)
    # insert_images(connection, df_sample2)

    delete_test_db(db_name)


def test_update_listings(db_name, df_sample, sample_update):
    connection = setup_database(db_name)

    for index, row in df_sample.iterrows():
        insert_listings(connection, row)

    for index, row in sample_update.iterrows():
        update_listings(connection, row)

    delete_test_db(db_name)


def test_delete_query():
    pass


def test_query_post_id(db_name, df_sample, sample_update):
    connection = setup_database(db_name)

    query_post_id(connection, df_sample)
    query_post_id(connection, sample_update)

    delete_test_db(db_name)
