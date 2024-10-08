import os
from datetime import timedelta

import pandas as pd
from sqlalchemy import Connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cl_search.utils import delete_images
from cl_search.utils import get_current_datetime
from cl_search.utils import get_current_time


def setup_database(db_name: str = "craigslist.db", **kwargs) -> Connection:
    path = kwargs.get("output_path", os.getcwd())

    db_path = os.path.join(path, db_name)
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
    create_tables(session)

    return session


def create_session(db_name: str = "craigslist.db", **kwargs) -> Connection:
    path = kwargs.get("output_path", os.getcwd())

    db_path = os.path.join(path, db_name)
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def create_tables(db: Connection):
    cursor = db.connection().connection.cursor()

    create_sources_table = """
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY,
        source VARCHAR(255) UNIQUE
    );
    """

    create_listings_table = """
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY,
        newly_added BIT DEFAULT 1,
        time_added DATETIME(255),
        last_updated DATETIME(255),
        title VARCHAR(500),
        post_description VARCHAR(1000),
        price VARCHAR(255),
        location VARCHAR(255),
        post_id VARCHAR(255) UNIQUE,
        address_info VARCHAR(500),
        attribute VARCHAR(500),
        post_timestamp VARCHAR(255),
        post_url VARCHAR(500)
    );
    """

    create_data_sources_table = """
    CREATE TABLE IF NOT EXISTS data_sources (
        id INTEGER PRIMARY KEY,
        listing_id INT,
        source_id INT,
        FOREIGN KEY (source_id) REFERENCES sources(id),
        FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
        UNIQUE (listing_id, source_id)
    );
    """

    create_images_table = """
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        listing_id INT,
        image_url VARCHAR(500),
        image_path VARCHAR(500),
        FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
        UNIQUE (listing_id, image_url)
    );
    """

    cursor.execute(create_sources_table)
    cursor.execute(create_listings_table)
    cursor.execute(create_data_sources_table)
    cursor.execute(create_images_table)

    db.commit()
    cursor.close()


def insert_listings(db: Connection, row: pd.DataFrame) -> None:
    cursor = db.connection().connection.cursor()
    current_time = get_current_time()

    insert_listing_query = """
        INSERT INTO listings (
            newly_added,
            time_added,
            last_updated,
            title,
            post_description,
            price,
            location,
            post_id,
            address_info,
            attribute,
            post_timestamp,
            post_url
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        );
    """

    cursor.execute(
        insert_listing_query,
        (
            1,
            row["time_added"],
            current_time,
            row["title"],
            row.get(["post_description"], ""),
            row["price"],
            row["location"],
            row["post_id"],
            row.get(["address_info"], ""),
            row.get(["attribute"], ""),
            row["timestamp"],
            row["post_url"]
        ),
    )

    db.commit()
    cursor.close()


def insert_data_sources(db: Connection, row: pd.DataFrame) -> None:
    cursor = db.connection().connection.cursor()

    insert_data_sources_query = """
        INSERT OR IGNORE INTO data_sources (
            listing_id,
            source_id
        )
        VALUES (
            (SELECT id FROM listings WHERE post_id = ?),
            (SELECT id FROM sources WHERE source = ?)
            );
    """

    cursor.execute(
        insert_data_sources_query,
        (
            row["post_id"],
            row["source"]
        )
    )

    db.commit()
    cursor.close()


def insert_sources(db: Connection, row: pd.DataFrame) -> None:
    cursor = db.connection().connection.cursor()

    insert_sources_query = """
        INSERT OR IGNORE INTO sources (source)
        VALUES (?);
    """

    cursor.execute(insert_sources_query, (row["source"],))

    db.commit()
    cursor.close()


def insert_images(db: Connection, row: pd.DataFrame) -> None:
    cursor = db.connection().connection.cursor()

    insert_images_query = """
        INSERT OR REPLACE INTO images (
            listing_id,
            image_url,
            image_path
        )
        VALUES (
            (SELECT id FROM listings WHERE post_id = ?),
            ?,
            ?
            );
    """

    try:
        # test this
        if row["image_urls"]:
            for url, path in row["image_urls"], row["image_paths"]:
                cursor.execute(
                    insert_images_query,
                    (
                        row["post_id"],
                        url,
                        path
                    )
                )

    except KeyError:
        cursor.execute(
            insert_images_query,
            (
                row["post_id"],
                row.get("image_url", ""),
                row.get("image_path", "")
            )
        )

    db.commit()
    cursor.close()


def update_listings(db: Connection, row: pd.DataFrame) -> None:
    cursor = db.connection().connection.cursor()
    current_time = get_current_time()

    update_listings_query = """
        UPDATE listings
        SET newly_added = ?,
            last_updated = ?,
            title = ?,
            post_description = ?,
            price = ?,
            location = ?,
            address_info = ?,
            attribute = ?,
            post_timestamp = ?,
            post_url = ?
        WHERE post_id = ?;
    """

    # Convert the Series data to scalar values
    cursor.execute(
        update_listings_query,
        (
            0,
            current_time,
            row["title"].item() if isinstance(row["title"], pd.Series) else row["title"],
            row["post_description"].item() if isinstance(row["post_description"], pd.Series) else row["post_description"],
            row["price"].item() if isinstance(row["price"], pd.Series) else row["price"],
            row["location"].item() if isinstance(row["location"], pd.Series) else row["location"],
            row.get("address_info", "").item() if isinstance(row.get("address_info", ""), pd.Series) else row.get("address_info", ""),
            row.get("attribute", "").item() if isinstance(row.get("attribute", ""), pd.Series) else row.get("attribute", ""),
            row["timestamp"].item() if isinstance(row["timestamp"], pd.Series) else row["timestamp"],
            row["post_url"].item() if isinstance(row["post_url"], pd.Series) else row["post_url"],
            row["post_id"]
        ),
    )

    db.commit()
    cursor.close()



def delete_query(db: Connection) -> None:
    cursor = db.connection().connection.cursor()

    current_time = get_current_datetime()

    time_to_stale = current_time - timedelta(weeks=1)

    # time_to_stale = current_time - timedelta(minutes=5)

    select_old_images = """
        SELECT i.image_path
        FROM images i
        JOIN listings l ON i.listing_id = l.id
        WHERE l.last_updated < ?
        """

    delete_old_listings = """
        DELETE FROM listings
        WHERE last_updated < ?
        """

    cursor.execute(select_old_images, (time_to_stale,))
    old_images = cursor.fetchall()

    if len(old_images) > 0:
        for index, image in enumerate(old_images):
            image_path = image[0].strip()
            print(f'deleteing old images:({index + 1}/{image_path})')
            delete_images(image_path)

    cursor.execute(delete_old_listings, (time_to_stale,))

    db.commit()
    cursor.close()


def query_post_id(db: Connection, df: pd.DataFrame, **kwargs) -> None:
    delete_mode = kwargs.get("delete_mode")

    cursor = db.connection().connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    post_id_query = """
        SELECT * FROM listings
        WHERE post_id = ?;
        """

    for index, row in df.iterrows():
        cursor.execute(post_id_query, (row['post_id'],))
        rows = cursor.fetchall()

        if len(rows) > 0:
            update_listings(db, row)
            insert_sources(db, row)
            insert_data_sources(db, row)
            insert_images(db, row)
        else:
            insert_listings(db, row)
            insert_sources(db, row)
            insert_data_sources(db, row)
            insert_images(db, row)

    if delete_mode is True:
        delete_query(db)

    cursor.close()
    db.close()
