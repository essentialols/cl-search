import os
import mysql.connector
import pandas as pd

# Connecting to MySQL Database
connection = mysql.connector.connect(
    user='root',
    password='football',
    host='localhost',
    database='test',
)
cursor = connection.cursor()

# defining spreadsheet location
folder_path = './sheets'
file_extension = '.xlsx'
file_list = [f for f in os.listdir(folder_path) if f.endswith(file_extension)]

# Loop to read each spreadsheet
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_excel(file_path)
    table_name = file_name[:-len(file_extension)]
    df.to_sql(name=table_name, con=connection, if_exists='replace', index=False)

# Closing MySQL connection
connection.close()
cursor.close()

query = """


"""
cursor.execute(query)

results = []
for i, data in enumerate(cursor):
    results.append(data)
    connection.close()
    cursor.close()
    break
