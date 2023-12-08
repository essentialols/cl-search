import mysql.connector
import os
from dotenv import load_dotenv
import sys
import logging
import time

launcher_path = sys.argv[2]

load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']

logger = logging.getLogger("to_mysql_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/init_mysql.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))


def connect_to_database(db_user, db_pass, db_host, db_port):
    global db
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            db = mysql.connector.connect(
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
            )
            return db  # Return the database connection if successful
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            retries += 1
            if retries < max_retries:
                print("Retrying in 5 seconds...")
                time.sleep(10)
            else:
                print("Max retry attempts reached. Unable to connect to the database.")
                raise


def create_tables():
    cursor = db.cursor()

    use_database = "USE webscrapes"

    create_sources_table = """
    CREATE TABLE IF NOT EXISTS sources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(255) UNIQUE
    )
    """

    create_listings_table = """
    CREATE TABLE IF NOT EXISTS listings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        time_added VARCHAR(255),
        title VARCHAR(500),
        price VARCHAR(255),
        post_timestamp VARCHAR(255),
        location VARCHAR(255),
        post_url VARCHAR(255),
        image_url VARCHAR(500),
        data_pid VARCHAR(255) UNIQUE,
        image_path VARCHAR(500),
        is_new TINYINT(1) DEFAULT 1
    )
    """

    create_archived_listings_table = """
    CREATE TABLE IF NOT EXISTS archived_listings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        time_added VARCHAR(255),
        title VARCHAR(500),
        price VARCHAR(255),
        post_timestamp VARCHAR(255),
        location VARCHAR(255),
        post_url VARCHAR(255),
        image_url VARCHAR(500),
        data_pid VARCHAR(255),
        image_path VARCHAR(500),
        is_new TINYINT(1) DEFAULT 1
    )
    """

    create_data_sources_table = """
    CREATE TABLE IF NOT EXISTS data_sources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data_pid_id INT,
        source_id INT,
        FOREIGN KEY (source_id) REFERENCES sources(id),
        FOREIGN KEY (data_pid_id) REFERENCES listings(id) ON DELETE CASCADE,
        UNIQUE (data_pid_id, source_id)
    )
    """

    create_cloudinary_table = """
    CREATE TABLE IF NOT EXISTS cloudinary (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data_pid_id INT UNIQUE,
        cloudinary_link VARCHAR(500),
        FOREIGN KEY (data_pid_id) REFERENCES listings(id) ON DELETE CASCADE
    )
    """

    cursor.execute(use_database)
    cursor.execute(create_sources_table)
    cursor.execute(create_listings_table)
    cursor.execute(create_archived_listings_table)
    cursor.execute(create_data_sources_table)
    cursor.execute(create_cloudinary_table)
    db.commit()


connect_to_database(db_user, db_pass, db_host, db_port)
create_tables()
print("Tables created")
