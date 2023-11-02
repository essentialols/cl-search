import schedule
import time
import os
import subprocess
import logging
import datetime
import pytz
import shutil
from urllib.parse import urlparse

time.sleep(2)  # container delay

###############################################################################

max_attempts = 10
search_query = "iphone"
timezone = pytz.timezone('US/Central')
initialize_mysql_tables = False
delay_job = False
# 10 to 15 minutes
delay_in_minutes = 120
delay_in_minutes_2 = 150
run_it_once = False  # If False job will repeat based on delay_in_minutes.
job_counter_max = 1   # You can customize the amount of times job will run before
#                       breaking while run_it_once is true

# Author: Gavin Kondrath | gav.ink
###############################################################################

utc_now = datetime.datetime.now(tz=pytz.timezone('UTC'))
current_time = utc_now.astimezone(timezone).strftime("(%Y-%m-%d %H:%M)")
time_file = utc_now.astimezone(timezone).strftime("%Y%m%d%H%M%S")

launcher_path = os.path.dirname(os.path.abspath(__file__))
scripts_folder = os.path.join(launcher_path, 'scripts')
log_folder = f'{launcher_path}/logs'
temp_folder = f'{launcher_path}/temp'
job_error_log = f'{log_folder}/job_error.log'
cl_urls = f'{launcher_path}/craigslist_urls.txt'

if not os.path.exists(log_folder):
    os.makedirs(log_folder)

if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

with open(job_error_log, 'w'):
    pass
logging.basicConfig(filename=job_error_log, level=logging.DEBUG)
print("Logging Setup Complete")

job_running = False
job_counter = 0


def clear_temp():
    print("clearing the temp folder")
    temp_items = os.listdir(temp_folder)
    for item in temp_items:
        temp_item_path = os.path.join(temp_folder, item)
        if os.path.isfile(temp_item_path):
            os.remove(temp_item_path)
        elif os.path.isdir(temp_item_path):
            shutil.rmtree(temp_item_path)


def run_script(script_path, file_name, launcher_path, search_query, url, max_retries=max_attempts):
    for retry in range(max_retries + 1):
        try:
            subprocess.run(['python3', script_path, file_name, launcher_path, search_query, url], check=True)
            print(f"Script completed: {script_path}")
            break

        except subprocess.CalledProcessError as e:
            print(f"Error running script {script_path}: {e}")
            logging.error(f"({current_time}) {script_path} failed and is attempting to recover: {e}")

            script_name = file_name[:-3]
            parsed_url = urlparse(url)
            parts_url = parsed_url.netloc.split('.')
            if len(parts_url) > 0:
                city_name = parts_url[0].lower()
            script_name_log = f'{temp_folder}/{script_name}.log'
            script_city_log = f'{temp_folder}/{script_name}_{city_name}.log'

            if os.path.isfile(script_name_log):
                if retry >= 1:
                    new_log_name = f'{temp_folder}/{time_file}_{script_name}_{retry}.log'
                else:
                    new_log_name = f'{temp_folder}/{time_file}_{script_name}.log'
                os.rename(script_name_log, new_log_name)
                shutil.move(new_log_name, f'{log_folder}/')

            elif os.path.isfile(script_city_log):
                if retry >= 1:
                    new_log_name = f'{temp_folder}/{time_file}_{script_name}_{city_name}_{retry}.log'
                else:
                    new_log_name = f'{temp_folder}/{time_file}_{script_name}_{city_name}.log'
                os.rename(script_city_log, new_log_name)
                shutil.move(new_log_name, f'{log_folder}/')

            else:
                print("No log files found for recovery.")

            if retry < max_retries:
                print(f"Retrying script... (attempt {retry + 2}/{max_retries + 1})")

            else:
                print(f"Script {script_path} failed.")
                logging.error(f"({current_time}) Max retries reached for script {script_path}: {e}")

                send_email = os.path.join(scripts_folder, 'send_email.py')
                subprocess.run(['python3', send_email, launcher_path], check=True)
                with open(job_error_log, 'w'):
                    pass
                clear_temp()
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


def job():  # 25.1MiB
    global job_running
    global job_counter
    job_counter += 1
    if not job_running:
        job_running = True
        script_counter = 0

        if initialize_mysql_tables is True:
            print("Initializing MYSQL Tables in DB: webscrapes")
            file_name = 'init_mysql.py'
            url = 'example.com'  # Placeholder to get the script to run
            script_path = os.path.join(scripts_folder, file_name)
            run_script(script_path, file_name, launcher_path, search_query, url, max_retries=max_attempts)

###############################################################################

        try:
            print("Starting Job...")

            with open(cl_urls, 'r') as file:
                urls = file.read().splitlines()
                run_craigslist_scripts(urls)

            ordered_scripts = [
                'filter_csv.py',
                'remove_extra_images.py',
                'to_mysql.py',
                ]

###############################################################################

            script_paths = [os.path.join(scripts_folder, file_name) for file_name in ordered_scripts]
            url = 'https://craigslist.org/'

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
            clear_temp()
            time.sleep(1)
            job_running = False


if delay_job is False:
    job()
    if run_it_once is False:
        schedule.every(delay_in_minutes).to(delay_in_minutes_2).minutes.do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)

if delay_job is True:
    print(f"Waiting for {delay_in_minutes}-{delay_in_minutes_2} minutes before beginning")
    schedule.every(delay_in_minutes).to(delay_in_minutes_2).minutes.do(job)

    while True:
        if run_it_once is True:
            if job_counter == job_counter_max:
                break
        schedule.run_pending()
        time.sleep(1)

