import mysql.connector
import pandas as pd
from PIL import Image
import io
import time

db = mysql.connector.connect(
    user='mysql_user',
    password='mysql_password',
    host='localhost',
    database='mysql_database'
)

source_name = 'cl_austin'
df = pd.read_excel(f'sheets/{source_name}.xlsx')

cursor = db.cursor()

columns = ", ".join([f"{col} VARCHAR(255)" for col in df.columns])
create_table_query = f"CREATE TABLE IF NOT EXISTS {source_name} ({columns}, id INT AUTO_INCREMENT PRIMARY KEY);"
cursor.execute(create_table_query)
print(f"Table {source_name} created")

insert_query = f"INSERT INTO {source_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))})"
values = [tuple(row) for row in df.values]
cursor.executemany(insert_query, values)
db.commit()

print(f"{len(df)} rows inserted into {source_name}")

db.close()
cursor.close()
