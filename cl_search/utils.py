import datetime
import logging
import os
from urllib.parse import urlparse

import pytz
import requests
import toml
from preferences import tz

logger = logging.getLogger("cl_search")
launcher_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.join(launcher_path, os.pardir)
selectors = toml.load(os.path.join(launcher_path, "selectors.toml"))


def get_current_time():
    timezone = pytz.timezone(tz)
    current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

    return current_time


def parse_url(url):
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


def valid_url(url):
    return url.startswith("http://") or url.startswith("https://")


def get_toml_data(toml, name):
    for data in toml:
        if data.get("name") == name:
            return data

    return None


def download_images(image_url, image_paths, image_counter, total_images):
    image_path = ""
    default_image_path = f"{project_path}/images/no_image.png"
    cl_images_dir = f"{project_path}/images/cl_images"

    if not os.path.exists(cl_images_dir):
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
                        print(
                            f"Image downloaded ({image_counter}/{total_images}): {image_path}"
                        )
                else:
                    print(
                        f"Failed to download image ({image_counter}/{total_images}): {image_url}"
                    )
            else:
                print(f"Invalid url ({image_counter}/{total_images}): {image_url}")
        else:
            print(
                f"Image already exists ({image_counter}/{total_images}): {image_path}"
            )
    else:
        image_path = f"{default_image_path}"
        print(f"No image found ({image_counter}/{total_images}): using default image")

    image_paths.append(image_path)

    return image_paths


def get_links_from_dict(location, hierarchy, links):
    for key, value in hierarchy.items():
        if isinstance(value, str):
            links.append(value)

        elif isinstance(value, dict):
            result = get_links_from_dict(location, value, links)
            if result:
                return set(result)


def get_links(location, hierarchy):
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
