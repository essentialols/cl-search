import requests
import os
from dotenv import load_dotenv
import mysql.connector
import time
import hashlib
import logging
import sys

launcher_path = sys.argv[2]

load_dotenv()
cloud_url = os.environ['CLOUDINARY_URL']
cloud_api_key = os.environ['CLOUD_API_KEY']
cloud_api_secret = os.environ['CLOUD_API_SECRET']
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

logger = logging.getLogger("to_cloudinary_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/to_cloudinary.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))

db = mysql.connector.connect(
    user=f'{db_user}',
    password=f'{db_pass}',
    host=f'{db_host}',
    port=f'{db_port}',
    database=f'{db_database}'
)

cursor = db.cursor()

query = """
    SELECT l.id, l.image_path, c.data_pid_id, c.cloudinary_link
    FROM listings l
    LEFT JOIN cloudinary c ON l.id = c.data_pid_id
    WHERE c.cloudinary_link IS NULL
"""
cursor.execute(query)
rows = cursor.fetchall()
total_images = len(rows)

if not rows:
    print("No images to upload to Cloudinary!")

else:
    print(f"{total_images} images to upload to Cloudinary.")
    for index, row in enumerate(rows, start=1):
        data_pid_id = row[0]
        image_path = row[1]
        cloudinary_link = row[3]

        timestamp = int(time.time())
        public_id = os.path.splitext(os.path.basename(image_path))[0]
        signature_data = f"public_id={public_id}&timestamp={timestamp}{cloud_api_secret}"
        signature = hashlib.sha1(signature_data.encode()).hexdigest()

        cloudinary_params = {
            "file": (open(image_path, 'rb'))
        }

        data = {
            "public_id": public_id,
            "api_key": cloud_api_key,
            "signature": signature,
            "timestamp": timestamp
        }

        cloudinary_url_with_params = f"{cloud_url}/upload"

        try:
            print(f"Uploading image {index}/{total_images}: {image_path}")
            response = requests.post(cloudinary_url_with_params, files=cloudinary_params, data=data)
            if response.status_code == 200:
                print("Cloudinary image uploaded successfully")
            else:
                print(f"Error uploading Cloudinary image: ({index}/{total_images}). Status code:", response.status_code)
                print("Response content:", response.content)

            cloudinary_response = response.json()
            cloudinary_link = cloudinary_response['public_id']

            update_query = """
                UPDATE cloudinary
                SET cloudinary_link = %s
                WHERE data_pid_id = %s
             """

            cursor.execute(update_query, (cloudinary_link, data_pid_id))
            db.commit()

        except Exception as e:
            print(f"Caught exception when uploading image to Cloudinary: ({index}/{total_images})", str(e))

print("Completed uploading images to Cloudinary server.")

cursor.close()
db.close()
