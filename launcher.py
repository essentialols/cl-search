import schedule
import time
import os
import subprocess
import logging
import datetime
import pytz

launcher_path = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(launcher_path, 'scripts')
log_file_path = f'{launcher_path}/job_errors.log'
cl_urls = f'{launcher_path}/craigslist_urls.txt'

try:
    os.chmod(log_file_path, 0o600)
    logging.basicConfig(filename=log_file_path, level=logging.ERROR)
except Exception as e:
    print(f"An error occurred: {e}")

max_attempts = 3
search_query = "record player"

timezone = pytz.timezone('Asia/Jakarta')
current_time = datetime.datetime.now(timezone).strftime("%m/%d %H:%M:%S")

job_running = False

def run_script(script_path, file_name, launcher_path, search_query, url, max_retries=max_attempts):
    for retry in range(max_retries + 1):
        try:
            subprocess.run(['python3', script_path, file_name, launcher_path, search_query, url], check=True)
            print(f"Script completed: {script_path}")
            break

        except subprocess.CalledProcessError as e:
            print(f"Error running script {script_path}: {e}")
            logging.error(f"({current_time}) {script_path} failed and is attempting to recover: {e}")
            if retry < max_retries:
                print(f"Retrying script... (attempt {retry + 2}/{max_retries + 1})")
            else:
                print(f"Script {script_path} failed.")
                logging.error(f"({current_time}) Max retries reached for script {script_path}: {e}")

                send_email = os.path.join(scripts_folder, 'send_email.py')
                subprocess.run(['python3', send_email, launcher_path], check=True)
                break


def run_craigslist_scripts(urls):
    url_counter = 0
    for url in urls:
        url_counter += 1
        try:
            file_name = 'craigslist.py'
            script_path = os.path.join(scripts_folder, file_name)
            print(f"Scraping Craiglist ({url_counter}/{len(urls)}): {url}")
            run_script(script_path, file_name, launcher_path, search_query, url, max_retries=max_attempts)
        except Exception as e:
            logging.error(f"({current_time}) Error running Craigslist script: {e}")
            print(f"Error running Craigslist script: {e}")


def job():
    global job_running
    if not job_running:
        job_running = True

        try:
            print("Starting Job...")

            with open(cl_urls, 'r') as file:
                urls = file.read().splitlines()
                run_craigslist_scripts(urls)

            ordered_scripts = [
                'filter_csv.py',
                'remove_extra_images.py',
                'to_mysql_v2.py'
                ]

            url = 'https://www.craigslist.org/'

            script_paths = [os.path.join(scripts_folder, file_name) for file_name in ordered_scripts]

            script_counter = 0

            for script_path in script_paths:
                script_counter += 1
                file_name = os.path.basename(script_path)
                print(f"Running script ({script_counter}/{len(script_paths)}): {script_path}")
                run_script(script_path, file_name, launcher_path, search_query, url, max_retries=max_attempts)

            print("Job Complete!")

        except Exception as e:
            logging.error(f"({current_time}) Error in job: {e}")
            print(f"Error: {e}")
            job()

        finally:
            job_running = False


job()

schedule.every(90).to(120).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
