from bs4 import BeautifulSoup
from collections import namedtuple
import datetime
import os
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# installing firefox browser, setting user_agent
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'
firefox_driver_path = os.path.join(os.getcwd(), 'geckodriver')
firefox_service = Service(firefox_driver_path)
firefox_option = Options()
firefox_option.set_preference('general.useragent.override', user_agent)
browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
browser.implicitly_wait(9)  # wait time for the browser to load the webpage

# Url of the website to scrape
url = 'https://austin.craigslist.org/'
browser.get(url)

# search_query (enter on input)
search_query = 'record player'
# search_field will find the "search craigslist" search bar by xpath
search_field = browser.find_element(By.XPATH, '/html/body/div[2]/section/div[2]/div[1]/div/input')
search_field.clear()
search_field.send_keys(search_query)
search_field.send_keys(Keys.ENTER)
time.sleep(10)  # If you start getting "ValueError:" "Expected axis has 0 elements" increase time.sleep

# Collecting the data
posts_html = []
to_stop = False
current_page = 0
total_items = 0

# Action chain setup
scroll_pause_time = .7  # if current_gallery == prev_gallery before it reaches the end of the page increase this
scroll_offset = 1200
actions = ActionChains(browser)

while not to_stop:
    while True:
        prev_url = browser.current_url
        prev_gallery = prev_url.split('#')[1] if '#' in prev_url else None
        actions.scroll_by_amount(0, scroll_offset).perform()
        time.sleep(scroll_pause_time)
        current_url = browser.current_url
        current_gallery = current_url.split('#')[1] if '#' in current_url else None
        if current_gallery == prev_gallery:
            break
    # search_results will find the OL tag using xpath
    search_results = browser.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[4]/ol')
    soup = BeautifulSoup(search_results.get_attribute('innerHTML'), 'html.parser')
    # post_html will contain all search results
    posts_html.extend(soup.find_all('li', {'class': 'cl-search-result'}))
    # page_num will identify the amount of search results in total, and the search results on the current page
    page_num = browser.find_element(By.CLASS_NAME, 'cl-page-number').text
    pattern = r'([\d,]+)\s*of\s*([\d,]+)'
    match = re.search(pattern, page_num)
    if match:
        current_page = int(match.group(1).replace(',', ''))
        total_items = int(match.group(2).replace(',', ''))

    try:
        # scroll to the top
        browser.execute_script('window.scrollTo(0, 0)')
        button_next = browser.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[1]/div[2]/button[3]')
        button_next.click()
        time.sleep(1)
        # Selenium will continue to click the button until the last search result has been reached
        if current_page == total_items:
            to_stop = True
        else:
            to_stop = False
    except ElementNotInteractableException:
        to_stop = True

print('Collected {0} listings'.format(len(posts_html)))

# clean up and organize data
CraigslistPost = namedtuple('CraigslistPost',
                            ['title', 'price', 'post_timestamp', 'location', 'post_url', 'image_url', 'data_pid'])
craigslist_posts = []
# This is where we begin calling all the data we scraped from posts_html
for posts_html in posts_html:
    title = getattr(posts_html.find('a', 'posting-title'), 'text', None)
    price_element = posts_html.find('span', 'priceinfo')
    price = price_element.text.strip() if price_element is not None else 'Price not given'
    # Meta contains both the location and timestamp
    meta_div = posts_html.find('div', class_='meta')
    if meta_div:
        meta_info = meta_div.get_text(strip=True)
        separator = meta_div.find('span', class_='separator')
        if separator:
            post_timestamp = meta_info.split(separator.text)[0]
            location = meta_info.split(separator.text)[1]
            if location.strip() == '':
                location = 'Austin area'  # In case there is no location data it will default to 'Austin area'
    post_url = posts_html.find('a', 'posting-title').get('href') if posts_html.find('a', 'posting-title') else ''
    # We are unable to get the entire list of SRCs, so I will be using requests to download them
    image_url = posts_html.find('img').get('src') if posts_html.find('img') else ''
    if image_url.strip() == '':
        image_url = 'No image'
    data_pid = posts_html.get('data-pid')
    craigslist_posts.append(CraigslistPost(title, price, post_timestamp, location, post_url, image_url, data_pid))

# creating the spreadsheets
df = pd.DataFrame(craigslist_posts)
df.columns = ['Title', 'Price', 'Date Posted', 'Location', 'post_url', 'image_url', 'data-pid']
df.dropna(inplace=True)
current_time = datetime.datetime.now().strftime("%m/%d %H:%M:%S")
df.insert(0, 'Time Added', current_time)
df.insert(0, 'Source', "Austin-cl")  # change value if different craigslist
df['link'] = df.apply(lambda row: f'=HYPERLINK("{row["post_url"]}","Link")', axis=1)
df.to_excel('CL-Austin.xlsx', sheet_name="Austin CL", index=False)
browser.close()
