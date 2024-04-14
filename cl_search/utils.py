import datetime
import logging
import os
import re
from urllib.parse import urlparse

import pytz
import requests
import toml

from cl_search.locations import VALID_LOCATIONS
from cl_search.preferences import tz

logger = logging.getLogger("cl_search")
launcher_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.join(launcher_path, os.pardir)
selectors = toml.load(os.path.join(launcher_path, "selectors.toml"))


def get_current_time() -> datetime.datetime:
    timezone = pytz.timezone(tz)
    current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

    return current_time


# rename this function
def parse_url(url: str) -> str:
    parsed_url = urlparse(url)
    parts_url = parsed_url.netloc.split(".")
    if (
        len(parts_url) >= 2
        and parts_url[0].lower() != "www"
        and parts_url[0].lower() != "craigslist"
    ):
        city_name = parts_url[0]
    else:
        city_name = None

    return city_name


def valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def parse_post_id(post_url: str) -> str:
    post_id_search = re.search(r"/(\d+)\.html$", post_url)
    if post_id_search:
        post_id = post_id_search.group(1)

    return post_id


def download_images(image_url: str) -> str:
    default_image_path = f"{project_path}/images/no_image.png"
    cl_images_dir = f"{project_path}/images/cl_images"

    if not os.path.isdir(cl_images_dir):
        os.makedirs(cl_images_dir)

    if image_url:
        image_file_name = image_url.split("/")[-1]
        image_path = os.path.join(cl_images_dir, image_file_name)

        if not os.path.exists(image_path):
            if valid_url(image_url):
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_path, "wb") as file:
                        file.write(response.content)
                        print(f"Image downloaded: {image_path}")
                else:
                    print(f"Failed to download image: {image_url}")
            else:
                print(f"Invalid url: {image_url}")
        else:
            print(f"Image already exists: {image_path}")
    else:
        image_path = f"{default_image_path}"
        print("No image found: using default image")

    return image_path


def get_links_from_dict(location: str, hierarchy: dict, links) -> str:
    for key, value in hierarchy.items():
        if isinstance(value, str):
            links.append(value)

        elif isinstance(value, dict):
            result = get_links_from_dict(location, value, links)
            if result:
                return set(result)


def get_links(location: str, hierarchy: dict = VALID_LOCATIONS) -> str:
    links = []

    location = location.lower()

    for key, value in hierarchy.items():
        key = key.lower()

        if value is str:
            value.lower()

        if key == location and isinstance(value, str):
            links.append(value)

        elif key == location and isinstance(value, dict):
            results = get_links_from_dict(location, value, links)
            if results:
                return set(results)

        elif value == location and isinstance(value, str):
            links.append(value)

        elif isinstance(value, str) and value.rstrip("/") == location:
            links.append(value)

        elif isinstance(value, dict):
            result = get_links(location, value)
            if result:
                return set(result)

    return links


def delete_images(image_path: str) -> None:
    if os.path.isfile(image_path):
        os.remove(image_path)


def split_url_size(url: str) -> str:
    parts = url.split("_")
    base_url = "_".join(parts[:-1])
    return base_url
