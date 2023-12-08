import datetime
import pytz
import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import random
from urllib.parse import urlsplit
from dotenv import load_dotenv

launcher_path = sys.argv[2]
search_query = sys.argv[3]

# launcher_path = "/Users/gavinkondrath/projects/cl_search"
# search_query = "record player"

timezone = pytz.timezone('US/Central')
current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

load_dotenv()
proton_user = os.environ['PROTON_USER']
proton_pass = os.environ['PROTON_PASS']

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0'
# driver_path = f'{launcher_path}/drivers/firefox/macos/geckodriver'
driver_path = f'{launcher_path}/drivers/firefox/geckodriver'
driver_service = Service(driver_path, log_output=f'{launcher_path}/temp/log.log')
driver_option = Options()
driver_option.add_argument("-headless")
driver_option.set_preference('general.useragent.override', user_agent)
driver_option.set_preference("permissions.default.desktop-notification", 2)
driver = webdriver.Firefox(options=driver_option, service=driver_service)
driver.install_addon(f'{launcher_path}/drivers/firefox/protonvpn.xpi')

driver.implicitly_wait(9)
window_handles = driver.window_handles
parent_tab = driver.window_handles[0]
child_tab = driver.window_handles[1]
wait = WebDriverWait(driver, 60)

page_load_timeout = 60
url = 'https://www.example.com/'
browser_settings = 'about:addons'
vpn_location = "United States"
random_delay = random.uniform(0.4, 2.7)

print("Setting up VPN")
driver.set_window_size(1400, 1200)
driver.get(browser_settings)
time.sleep(.5)
driver.switch_to.window(child_tab)
extension_id = driver.current_url
parsed_url = urlsplit(extension_id)
extension_id = parsed_url.netloc
print(extension_id)
driver.switch_to.window(parent_tab)
time.sleep(.5)
extensions = driver.find_element(By.XPATH, '/html/body/div/div[1]/categories-box/button[2]')
extensions.click()
proton_options = driver.find_element(By.XPATH, "//*[contains(text(), 'Proton VPN:')]")
proton_options.click()
proton_perms = driver.find_element(By.XPATH, '//*[@id="details-deck-button-permissions"]')
proton_perms.click()
proton_control = driver.find_element(By.ID, "permission-0")
driver.execute_script("arguments[0].click();", proton_control)
proton_access_all = driver.find_element(By.ID, "permission-1")
driver.execute_script("arguments[0].click();", proton_access_all)
proton_access_com = driver.find_element(By.XPATH, '//*[@id="permission-2"]')
proton_access_com.click()
proton_access_me = driver.find_element(By.XPATH, '//*[@id="permission-3"]')
proton_access_me.click()
driver.switch_to.window(child_tab)
proton_sign_in = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/button')
proton_sign_in.click()
time.sleep(.5)
proton_login_tab = driver.window_handles[2]
driver.switch_to.window(proton_login_tab)
proton_email = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
proton_email.click()
proton_email.clear()
for char in proton_user:
    proton_email.send_keys(char)
    delay = random.uniform(0.1, 0.2)
    time.sleep(delay)
proton_password = driver.find_element(By.XPATH, '//*[@id="password"]')
proton_password.click()
proton_password.clear()
for char in proton_pass:
    proton_password.send_keys(char)
    delay = random.uniform(0.1, 0.2)
    time.sleep(delay)
proton_password.send_keys(Keys.ENTER)
extension_url = f'moz-extension://{extension_id}/popup.html'
wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Open the Proton VPN')]")))
try:
    driver.set_page_load_timeout(page_load_timeout)
    driver.get(extension_url)
except TimeoutException as e:
    driver.close()
    raise TimeoutError(f"Selenium timed out waiting for the page to load: {e}")

proton_search = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-input"]')))
time.sleep(1)
proton_search.send_keys(vpn_location)
proton_search.send_keys(Keys.ENTER)
time.sleep(1)

print("Connected to VPN")

try:
    driver.set_page_load_timeout(page_load_timeout)
    driver.get(url)
except TimeoutException as e:
    driver.close()
    raise TimeoutError(f"Selenium timed out waiting for the page to load: {e}")
