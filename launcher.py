import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

launcher_path = os.path.dirname(os.path.abspath(__file__))

def job():
    try:
        print("Starting Job...")

        file_names = ['cl_austin.py',
                      'cl_dallas.py',
                      'cl_houston.py',
                      'cl_san_antonio.py',
                      'to_mysql.py']

        for file_name in file_names:
            print(f"Processing: {file_name}")
            file_path = os.path.join(launcher_path, 'scripts', file_name)
            with open(file_path, 'r') as file:
                script = file.read()
                exec(script)

        print("Job Complete!")

    except Exception as e:
        print(f"Error: {e}")
        job()
job()

schedule.every(70).to(90).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
