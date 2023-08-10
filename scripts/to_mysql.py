import mysql.connector
import pandas as pd
import os
import time
import sys
from dotenv import load_dotenv

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

folder_path = f"{launcher_path}/filtered"
file_names = os.listdir(folder_path)

print(f"Writing to: {db_database}")

cursor = db.cursor()

for file_name in file_names:
    if file_name.endswith('.csv'):
        source_name = os.path.splitext(file_name)[0]
        df = pd.read_csv(f'{os.path.join(folder_path, file_name)}')
        columns = ", ".join([f"{col} VARCHAR(255)" for col in df.columns])
        drop_query = f"DROP TABLE IF EXISTS {source_name};"
        create_table_query = f"CREATE TABLE IF NOT EXISTS {source_name} ({columns}, id INT AUTO_INCREMENT PRIMARY KEY);"

        cursor.execute(drop_query)
        print(f"dropped old {source_name} table")
        time.sleep(1)

        cursor.execute(create_table_query)
        print(f"Table {source_name} created")

        insert_query = f"INSERT INTO {source_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))})"
        values = [tuple(row) for row in df.values]
        cursor.executemany(insert_query, values)

        db.commit()
        print(f"{len(df)} rows inserted into {source_name}")

db.close()
cursor.close()
