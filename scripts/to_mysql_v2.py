import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv
import sys

launcher_path = sys.argv[2]

load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

db = mysql.connector.connect(
    user=f'{db_user}',
    password=f'{db_pass}',
    host=f'{db_host}',
    port=f'{db_port}',
    database=f'{db_database}'
)

def create_tables():
    cursor = db.cursor()

    create_sources_table = """
    CREATE TABLE IF NOT EXISTS sources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(255) UNIQUE
    )
    """

    create_listings_table = """
    CREATE TABLE IF NOT EXISTS listings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        time_added TIMESTAMP,
        title VARCHAR(255),
        price VARCHAR(255),
        post_timestamp VARCHAR(255),
        location VARCHAR(255),
        post_url VARCHAR(255),
        image_url VARCHAR(255),
        data_pid VARCHAR(255) UNIQUE,
        image_path VARCHAR(255),
        is_new TINYINT(1) DEFAULT 1
    )
    """

    create_archived_listings_table = """
    CREATE TABLE IF NOT EXISTS archived_listings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        time_added TIMESTAMP,
        title VARCHAR(255),
        price VARCHAR(255),
        post_timestamp VARCHAR(255),
        location VARCHAR(255),
        post_url VARCHAR(255),
        image_url VARCHAR(255),
        data_pid VARCHAR(255),
        image_path VARCHAR(255),
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

    cursor.execute(create_sources_table)
    cursor.execute(create_listings_table)
    cursor.execute(create_archived_listings_table)
    cursor.execute(create_data_sources_table)
    db.commit()

csv_folder = f"{launcher_path}/filtered"

all_rows = []
unique_data_pids = set()

create_tables()

cursor = db.cursor()

def count_and_insert_sources(cursor, csv_folder):
    csv_files = [file for file in os.listdir(csv_folder) if file.endswith('.csv')]

    for csv_file in csv_files:
        source_name = os.path.splitext(csv_file)[0]
        cursor.execute("INSERT INTO sources (source) VALUES (%s) ON DUPLICATE KEY UPDATE source=source", (source_name,))

count_and_insert_sources(cursor, csv_folder)

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        csv_path = os.path.join(csv_folder, filename)

        df = pd.read_csv(csv_path)

        unique_data_pids.update(df['data_pid'])
        all_rows.extend(df.to_dict(orient='records'))

for data_pid in unique_data_pids:
    cursor.execute("SELECT * FROM listings WHERE data_pid = %s", (data_pid,))
    existing_data = cursor.fetchone()

    row = next((r for r in all_rows if r['data_pid'] == data_pid), None)
    if row:
        is_new = row['is_new']

        if existing_data:
            update_query = """
            UPDATE listings
            SET title=%s,
                price=%s,
                post_timestamp=%s,
                location=%s,
                image_url=%s,
                image_path=%s,
                is_new = %s
            WHERE data_pid=%s
            """
            cursor.execute(update_query, (row['title'], row['price'], row['post_timestamp'], row['location'], row['image_url'], row['image_path'], 0, data_pid))
        else:
            insert_query = """
            INSERT INTO listings (
                time_added,
                title,
                price,
                post_timestamp,
                location,
                post_url,
                image_url,
                data_pid,
                image_path,
                is_new
            )
            VALUES (
                NOW(),
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """

            cursor.execute(insert_query, (
                row['title'],
                row['price'],
                row['post_timestamp'],
                row['location'],
                row['post_url'],
                row['image_url'],
                data_pid,
                row['image_path'],
                is_new
            ))

        db.commit()

for row in all_rows:
    data_pid = row['data_pid']

    cursor.execute("INSERT INTO data_sources (data_pid_id, source_id) VALUES ((SELECT id FROM listings WHERE data_pid=%s), (SELECT id FROM sources WHERE source=%s)) ON DUPLICATE KEY UPDATE source_id=source_id", (data_pid, row['source']))

    db.commit()

data_pid_values = [row['data_pid'] for row in all_rows]
cursor.execute("INSERT INTO archived_listings SELECT * FROM listings WHERE data_pid NOT IN (%s)" % ",".join(["%s"] * len(data_pid_values)), data_pid_values)
cursor.execute("DELETE FROM listings WHERE data_pid NOT IN (%s)" % ",".join(["%s"] * len(data_pid_values)), data_pid_values)
db.commit()

cursor.close()
db.close()
