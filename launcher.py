import schedule
import time as tm
from datetime import time, timedelta, datetime

def job():

    with open('scripts/cl_austin.py', 'r') as file:
        cl_austin = file.read()
        exec(cl_austin)

    with open('scripts/cl_houston.py', 'r') as file:
        cl_houston = file.read()
        exec(cl_houston)

    #  This section is where we run the script to load the spreadsheets into MySQL



job()

schedule.every(45).to(75).minutes.do(job)

while True:
    schedule.run_pending()
    tm.sleep(1)
