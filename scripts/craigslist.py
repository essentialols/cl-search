from bs4 import BeautifulSoup
from collections import namedtuple
import datetime
import pytz
import os
import pandas as pd
import re
import requests
import time
import sys
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

file_name = sys.argv[1]
launcher_path = sys.argv[2]
search_query = sys.argv[3]
url = sys.argv[4]

parsed_url = urlparse(url)
parts_url = parsed_url.netloc.split('.')
if len(parts_url) > 0:
    city_name = parts_url[0].capitalize()
source_name = f'craigslist_{parts_url[0]}'

timezone = pytz.timezone('Asia/Jakarta')
current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

page_load_timeout = 60

logger = logging.getLogger(f"cl_{city_name}_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/{source_name}.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s Selenium -> %(message)s", "%Y-%m-%d %H:%M:%S"))

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0'
driver_service = Service(log_output=f'{launcher_path}/temp/{source_name}.log')
driver_option = Options()
driver_option.add_argument("--headless=new")
driver_option.add_argument(f'--user-agent={user_agent}')
driver_option.add_argument("--disable-notifications")
driver_option.add_argument('--disable-dev-shm-usage')
driver_option.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=driver_option, service=driver_service)

driver.implicitly_wait(9)
driver.set_window_size(1280, 1000)
window_handles = driver.window_handles
wait = WebDriverWait(driver, 30)

print(f"Fetching {search_query}s from {city_name} Craigslist...")

try:
    driver.set_page_load_timeout(page_load_timeout)
    driver.get(url)
except TimeoutException as e:
    driver.close()
    raise TimeoutError(f"Selenium timed out waiting for the page to load: {e}")

for_sale = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@href="/search/sss"]')))
for_sale.click()
search_field = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="search for sale"]')))
search_field.clear()
search_field.send_keys(search_query)
search_field.send_keys(Keys.ENTER)
wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[5]/ol')))
time.sleep(1)

posts_data = []
scraped_img_tag_src = set()
to_stop = False
current_page = 0
total_items = 0

scroll_pause_time = .8  # if current_gallery == prev_gallery before it reaches the end of the page increase this
scroll_offset = 1000
actions = ActionChains(driver)

while not to_stop:
    while True:
        prev_url = driver.current_url
        prev_gallery = prev_url.split('#')[1] if '#' in prev_url else None
        actions.scroll_by_amount(0, scroll_offset).perform()
        time.sleep(scroll_pause_time)
        current_url = driver.current_url
        current_gallery = current_url.split('#')[1] if '#' in current_url else None
        if current_gallery == prev_gallery:
            break
    search_results = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[5]/ol')
    soup = BeautifulSoup(search_results.get_attribute('innerHTML'), 'html.parser')
    for div in soup.find_all('li', {'class': 'cl-search-result'}):
        img_tag = div.find('img')
        if img_tag:
            img_tag_src = img_tag.get('src')
            if img_tag_src not in scraped_img_tag_src:
                posts_data.extend(div)
                scraped_img_tag_src.add(img_tag_src)

    page_num = driver.find_element(By.CLASS_NAME, 'cl-page-number').text
    pattern = r'([\d,]+)\s*of\s*([\d,]+)'
    match = re.search(pattern, page_num)
    if match:
        current_page = int(match.group(1).replace(',', ''))
        total_items = int(match.group(2).replace(',', ''))
    if posts_data == []:
        driver.close()
        raise NoSuchElementException("No listings found on the page. Check if the page loaded properly.")

    try:
        driver.execute_script('window.scrollTo(0, 0)')
        button_next = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[8]/div[1]/button[3]')
        button_next.click()
        time.sleep(1)
        if current_page == total_items:
            to_stop = True
        else:
            to_stop = False

    except ElementNotInteractableException:
        to_stop = True

    except NoSuchElementException as e:
        print(f"Error: {e}")
        break

#with open(f'{launcher_path}/temp/{source_name}_posts_html.txt', 'w', encoding='utf-8') as file:
#    for div in posts_data:
#        file.write(str(div) + '\n')

print('Collected {0} listings'.format(len(posts_data)))

CL_item = namedtuple('CL_item',
                            ['title', 'price', 'post_timestamp', 'location', 'post_url', 'image_url'])
craigslist_posts = []
image_paths = []
image_counter = 0
total_images = len(posts_data)
default_image_path = f"{launcher_path}/images/no_image.png"

for posts_html in posts_data:
    title = getattr(posts_html.find('a', 'posting-title'), 'text', None)
    price_element = posts_html.find('span', 'priceinfo')
    price = price_element.text.strip() if price_element is not None else 'Price not given'
    post_url = posts_html.find('a', 'posting-title').get('href') if posts_html.find('a', 'posting-title') else ''

    meta_div = posts_html.find('div', class_='meta')
    if meta_div:
        meta_info = meta_div.get_text(strip=True)
        separator = meta_div.find('span', class_='separator')
        if separator:
            post_timestamp = meta_info.split(separator.text)[0]
            location = meta_info.split(separator.text)[1]
            if location.strip() == '':
                location = f'{city_name} area'

    create_dir = f"{launcher_path}/images/cl_images"
    if not os.path.exists(create_dir):
        os.makedirs(create_dir)

    image_url = posts_html.find('img').get('src') if posts_html.find('img') else ''
    image_path = ""
    image_counter += 1

    if image_url:
        image_file_name = image_url.split("/")[-1]
        image_path = os.path.join(create_dir, image_file_name)

        if not os.path.exists(image_path):
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, "wb") as file:
                    file.write(response.content)
                    print(f"Image downloaded ({image_counter}/{total_images}): {image_path}")
        else:
            print(f"Image already exists ({image_counter}/{total_images}): {image_path}")
    else:
        image_path = f'{default_image_path}'
        print(f"No image found ({image_counter}/{total_images}): using default image")
    image_paths.append(image_path)

    if image_url.strip() == '':  # sometimes this errors out if the scroll_pause_time is too low
        image_url = 'No image'

    craigslist_posts.append(CL_item(title, price, post_timestamp, location, post_url, image_url))

df = pd.DataFrame(craigslist_posts)
df.insert(0, 'time_added', current_time)
df.insert(0, 'is_new', "1")
df.insert(0, 'source', f"{source_name}")
df['data_pid'] = df['post_url'].str.extract(r'/(\d+)\.html$')
df['image_path'] = image_paths
df.dropna(inplace=True)
df.to_csv(f'{launcher_path}/sheets/{source_name}.csv', index=False)
print(f"Created {source_name}.csv")
driver.close()
driver.quit()

