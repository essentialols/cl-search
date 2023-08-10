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
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

file_name = sys.argv[1]
launcher_path = sys.argv[2]
search_query = sys.argv[3]

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
firefox_driver_path = os.path.join(os.getcwd(), 'drivers', 'geckodriver')
firefox_service = Service(firefox_driver_path, log_path=os.path.devnull)
firefox_option = Options()
firefox_option.set_preference('general.useragent.override', user_agent)
driver = webdriver.Firefox(service=firefox_service, options=firefox_option)
driver.implicitly_wait(9)

url = 'https://sanantonio.craigslist.org/'

source_name = os.path.splitext(f'{file_name}')[0]
city_name = re.sub(r'cl_', '', source_name).replace('_', ' ').title()
print(f"Now getting {search_query}s from {city_name} Craigslist...")
driver.get(url)

for_sale = driver.find_element(By.XPATH, '/html/body/div[2]/section/div[3]/div[3]/div[2]/h3/a')
for_sale.click()
time.sleep(8)
search_field = driver.find_element(By.XPATH, '/html/body/div[1]/main/form/div[1]/div/div/input')
search_field.clear()
search_field.send_keys(search_query)
search_field.send_keys(Keys.ENTER)
time.sleep(5)  # If you start getting "ValueError:" "Expected axis has 0 elements" increase time.sleep

posts_html = []
to_stop = False
current_page = 0
total_items = 0

scroll_pause_time = .7  # if current_gallery == prev_gallery before it reaches the end of the page increase this
scroll_offset = 1200
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
    search_results = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[4]/ol')
    soup = BeautifulSoup(search_results.get_attribute('innerHTML'), 'html.parser')
    posts_html.extend(soup.find_all('li', {'class': 'cl-search-result'}))
    page_num = driver.find_element(By.CLASS_NAME, 'cl-page-number').text
    pattern = r'([\d,]+)\s*of\s*([\d,]+)'
    match = re.search(pattern, page_num)
    if match:
        current_page = int(match.group(1).replace(',', ''))
        total_items = int(match.group(2).replace(',', ''))

    try:
        driver.execute_script('window.scrollTo(0, 0)')
        button_next = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[1]/div[2]/button[3]')
        button_next.click()
        time.sleep(1)
        if current_page == total_items:
            to_stop = True
        else:
            to_stop = False
    except ElementNotInteractableException:
        to_stop = True

print('Collected {0} listings'.format(len(posts_html)))

CraigslistPost = namedtuple('CraigslistPost',
                            ['title', 'price', 'post_timestamp', 'location', 'post_url', 'image_url', 'data_pid'])
craigslist_posts = []
image_paths = []
default_image_path = f"{launcher_path}/images/no_image.png"

for posts_html in posts_html:
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

    os.umask(0o002)
    create_dir = f"{launcher_path}/images/cl_images"
    if not (os.path.dirname(create_dir)):
        try:
            original_umask = os.umask(0)
            os.makedirs(os.path.dirname(create_dir, mode=777))
        finally:
            os.umask(original_umask)

    image_url = posts_html.find('img').get('src') if posts_html.find('img') else ''
    image_path = ""

    if image_url:
        image_file_name = image_url.split("/")[-1]
        image_path = os.path.join(create_dir, image_file_name)

        if not os.path.exists(image_path):
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, "wb") as file:
                    file.write(response.content)
                    print(f"Image downloaded: {image_path}")
        else:
            print(f"Image already exists: {image_path}")
    else:
        image_path = f'{default_image_path}'
        print("No image found: using default image")
    image_paths.append(image_path)

    if image_url.strip() == '': # sometimes this errors out if the scroll_pause_time is too low
        image_url = 'No image'

    data_pid = posts_html.get('data-pid')
    craigslist_posts.append(CraigslistPost(title, price, post_timestamp, location, post_url, image_url, data_pid))

df = pd.DataFrame(craigslist_posts)
timezone = pytz.timezone('Asia/Jakarta')
current_time = datetime.datetime.now(timezone).strftime("%m/%d %H:%M:%S")
df.insert(0, 'time_added', current_time)
df.insert(0, 'is_new', "1")
df.insert(0, 'source', f"{source_name}")
df['image_path'] = image_paths
df.dropna(inplace=True)
df.to_csv(f'{launcher_path}/sheets/{source_name}.csv', index=False)
print(f"Created {source_name}.csv")
driver.close()
