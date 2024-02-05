from cl_search.locations import VALID_LOCATIONS
from cl_search.utils import download_images
from cl_search.utils import get_links
from cl_search.utils import parse_url
from cl_search.utils import project_path


def test_write_frames_test():
    assert parse_url("https://kent.craigslist.org/") == "kent"


def test_download_images():
    url = "https://kent.craigslist.org/"
    cl_images_dir = f"{project_path}/images/cl_images/"
    assert download_images(url) == cl_images_dir  # image_path


def test_get_links():
    assert get_links("kent", VALID_LOCATIONS) == {"https://kent.craigslist.org/"}
