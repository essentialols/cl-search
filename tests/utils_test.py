from cl_search.locations import VALID_LOCATIONS
from cl_search.utils import download_images
from cl_search.utils import get_links
from cl_search.utils import parse_post_id
from cl_search.utils import parse_url
from cl_search.utils import project_path
from cl_search.utils import split_url_size
from cl_search.utils import valid_url


def test_parse_url():
    assert parse_url("https://kent.craigslist.org/") == "kent"


def test_valid_url():
    url = "https://kent.craigslist.org/"
    assert valid_url(url) is True


def test_parse_post_id():
    post = "https://austin.craigslist.org/tag/d/austin-vintage-fisher-price-record/7728830431.html"
    assert parse_post_id(post) == "7728830431"


def test_download_images():
    url = "https://kent.craigslist.org/"
    cl_images_dir = f"{project_path}/images/cl_images/"
    assert download_images(url) == cl_images_dir  # image_path


def test_get_links():
    assert get_links("kent", VALID_LOCATIONS) == {"https://kent.craigslist.org/"}


def test_split_url_size():
    img_src = "https://images.craigslist.org/00606_jaaEH1DHWrT_0pm0t2_600x450.jpg"

    assert split_url_size(img_src) == "https://images.craigslist.org/00606_jaaEH1DHWrT_0pm0t2"
