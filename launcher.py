import schedule
import time

def job():
    try:
        file_names = ['cl_austin.py',
                      'cl_houston.py',
                      'to_mysql.py']

        for file_name in file_names:
            print(f"Processing file: {file_name}")
            with open(f'scripts/{file_name}', 'r') as file:
                script = file.read()
                exec(script)

    except Exception as e:
        print(f"Error: {e}")
        job()
job()

schedule.every(70).to(90).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
