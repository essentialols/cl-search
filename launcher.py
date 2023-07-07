import schedule
import time

def job():
    try:
        with open('scripts/cl_austin.py', 'r') as file:
            cl_austin = file.read()
            exec(cl_austin)

        with open('scripts/cl_houston.py', 'r') as file:
            cl_houston = file.read()
            exec(cl_houston)

        with open('scripts/to_mysql.py', 'r') as file:
            to_mysql = file.read()
            exec(to_mysql)

    except Exception as e:
        print(f"Error: {e}")
        job()
job()

schedule.every(70).to(90).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
