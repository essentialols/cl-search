import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv
import sys
import requests
import time
import hashlib
import logging

launcher_path = sys.argv[2]

load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']
cloud_name = os.environ['CLOUD_NAME']
cloud_api_key = os.environ['CLOUD_API_KEY']
cloud_api_secret = os.environ['CLOUD_API_SECRET']
cloudinary_url = os.environ['CLOUDINARY_URL']

logger = logging.getLogger("to_mysql_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/to_mysql.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))

db = mysql.connector.connect(
    user=f'{db_user}',
    password=f'{db_pass}',
    host=f'{db_host}',
    port=f'{db_port}',
    database=f'{db_database}'
)

csv_folder = f"{launcher_path}/filtered"

all_rows = []
unique_data_pids = set()

cursor = db.cursor()


def count_and_insert_sources(cursor, csv_folder):
    csv_files = [file for file in os.listdir(csv_folder) if file.endswith('.csv')]

    for csv_file in csv_files:
        source_name = os.path.splitext(csv_file)[0]
        cursor.execute("INSERT INTO sources (source) VALUES (%s) ON DUPLICATE KEY UPDATE source=source", (source_name,))


def request_deletion(public_id, index, total_images):
    cleaned_public_id = public_id[0].strip("'")  # errors if none
    timestamp = int(time.time())
    signature_data = f"public_id={cleaned_public_id}&timestamp={timestamp}{cloud_api_secret}"
    signature = hashlib.sha1(signature_data.encode()).hexdigest()
    cloudinary_url_with_params = f"{cloudinary_url}/destroy"
    cloudinary_request = {
        "public_id": cleaned_public_id,
        "api_key": cloud_api_key,
        "signature": signature,
        "timestamp": timestamp
        }

    if public_id == "no_image.png":
        print(f"Skipping no_image.png ({index}/{total_images})")

    else:
        try:
            response = requests.post(cloudinary_url_with_params, data=cloudinary_request)
            if response.status_code == 200:
                print(f"Cloudinary image successfully deleted ({index}/{total_images}): {public_id}")
            else:
                print(f"Error deleting Cloudinary image ({index}/{total_images}): {public_id}. Status code:", response.status_code)
                print("Error Response:", response.content)
        except Exception as e:
            print(f"Caught exception when deleting images from Cloudinary ({index}/{total_images}): {public_id}", str(e))


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
                post_url=%s,
                image_url=%s,
                image_path=%s,
                is_new = %s
            WHERE data_pid=%s
            """
            cursor.execute(update_query, (
                row['title'], row['price'], row['post_timestamp'], row['location'], row['post_url'], row['image_url'], row['image_path'],
                0,
                data_pid))
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
                %s,
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
                row['time_added'],
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

    cursor.execute(
        'INSERT INTO data_sources (data_pid_id, source_id) VALUES ((SELECT id FROM listings WHERE data_pid=%s),'
        ' (SELECT id FROM sources WHERE source=%s)) ON DUPLICATE KEY UPDATE source_id=source_id',
        (data_pid, row['source']))
    cursor.execute("INSERT IGNORE INTO cloudinary (data_pid_id) SELECT id FROM listings WHERE data_pid=%s", (data_pid,))

    db.commit()

data_pid_values = [row['data_pid'] for row in all_rows]

cursor.execute("""
    SELECT DISTINCT c.cloudinary_link FROM cloudinary c LEFT JOIN listings l ON l.id = c.data_pid_id
    WHERE l.data_pid NOT IN (%s)""" % ",".join(["%s"] * len(data_pid_values)), data_pid_values)

public_ids = cursor.fetchall()
total_images = len(public_ids)

if not public_ids:
    print("There are no images to delete from Cloudinary.")

else:
    print(f"{total_images} images to delete from Cloudinary server.")
    for index, public_id in enumerate(public_ids, start=1):
        try:
            public_id[0].strip("'")

        except AttributeError:
            print(f'Caught none type: {public_id}')
            continue

        request_deletion(public_id, index, total_images)

cursor.execute("""INSERT INTO archived_listings SELECT * FROM listings
    WHERE data_pid NOT IN (%s)""" % ",".join(["%s"] * len(data_pid_values)), data_pid_values)

cursor.execute("DELETE FROM listings WHERE data_pid NOT IN (%s)" % ",".join(
    ["%s"] * len(data_pid_values)), data_pid_values)

db.commit()

cloudinary_image_update = """
   SELECT l.id, l.image_path, c.data_pid_id, c.cloudinary_link
   FROM listings l
   LEFT JOIN cloudinary c ON l.id = c.data_pid_id
 """
cursor.execute(cloudinary_image_update)
cloudinary_links = cursor.fetchall()
total_images = len(cloudinary_links)

print("Checking if there are images to update")
for index, row in enumerate(cloudinary_links, start=1):
    image_path = row[1]
    data_pid_id = row[2]
    public_id = row[3]

    if public_id is None:
        continue

    elif os.path.splitext(os.path.basename(image_path))[0] != public_id:
        print(f"Updating image {public_id}")
        request_deletion(public_id, index, total_images)

        update_images = """
            UPDATE cloudinary
            SET cloudinary_link = NULL
            WHERE data_pid_id = %s
        """

        cursor.execute(update_images, (data_pid_id,))
        print(f"Updated data_pid_id in Cloudinary:{data_pid_id}")
        db.commit()

    else:
        continue

cursor.close()
db.close()
