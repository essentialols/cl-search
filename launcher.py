import schedule
import time
import os
import subprocess
import logging
import datetime
import pytz

logging.basicConfig(filename='job_errors.log', level=logging.ERROR)

launcher_path = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(launcher_path, 'scripts')

max_attempts = 3
search_query = "record player"

timezone = pytz.timezone('Asia/Jakarta')
current_time = datetime.datetime.now(timezone).strftime("%m/%d %H:%M:%S")


def run_script(script_path, file_name, launcher_path, search_query, max_retries=max_attempts):

    for retry in range(max_retries + 1):
        try:
            print(f"Running script: {script_path}")
            subprocess.run(['bin/python', script_path, file_name, launcher_path, search_query], check=True)
            print(f"Script completed: {script_path}")
            break

        except subprocess.CalledProcessError as e:
            print(f"Error running script {script_path}: {e}")
            logging.error(f"({current_time}) {script_path} failed and is attempting to recover: {e}")
            if retry < max_retries:
                print(f"Retrying... (attempt {retry + 2}/{max_retries + 1})")
            else:
                print(f"Script {script_path} failed.")
                logging.error(f"({current_time}) Max retries reached for script {script_path}: {e}")

                send_email = os.path.join(scripts_folder, 'send_email.py')
                subprocess.run(['bin/python', send_email, launcher_path], check=True)

                break


def job():
    try:
        print("Starting Job...")

        cl_scripts = [file_name for file_name in os.listdir(scripts_folder) if file_name.startswith('cl_')]

        ordered_scripts = [
            'filter_csv.py',
            'remove_extra_images.py',
            'to_mysql_v2.py'
            ]

        all_scripts = cl_scripts + ordered_scripts

        script_paths = [os.path.join(scripts_folder, file_name) for file_name in all_scripts]

        for script_path in script_paths:
            file_name = os.path.basename(script_path)
            run_script(script_path, file_name, launcher_path, search_query, max_retries=max_attempts)

        print("Job Complete!")

    except Exception as e:
        logging.error(f"({current_time}) Error in job: {e}")
        print(f"Error: {e}")

        job()


job()

schedule.every(70).to(90).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
