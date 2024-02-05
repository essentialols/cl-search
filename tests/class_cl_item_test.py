import pytest
from bs4 import BeautifulSoup

from cl_search.class_cl_item import CL_item
from cl_search.class_cl_item import Gallery
from cl_search.class_cl_item import Grid
from cl_search.class_cl_item import identify_cl_item_type
from cl_search.class_cl_item import List
from cl_search.class_cl_item import Narrow_list
from cl_search.class_cl_item import Preview
from cl_search.class_cl_item import Thumb


@pytest.fixture
def sample_list():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-list" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="result-node-wide"><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only posting-title"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal</span></a><span class="meta"><span class="separator">·</span>LA<span class="separator">·</span><span title="Sun Feb 04 2024 18:23:02 GMT+0800 (Malaysia Time)">5h ago</span><span class="separator">·</span><span class="priceinfo">$250</span><span class="pic-button">pic</span><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></span></div></li>
    """

    return sample_listing


@pytest.fixture
def sample_narrow_list():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-list" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="result-node-narrow"><div class="supertitle">LA</div><div class="title-blob"><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only posting-title"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal</span></a></div><div class="meta"><span title="Sun Feb 04 2024 18:23:02 GMT+0800 (Malaysia Time)">5h ago</span><span class="separator">·</span><span class="priceinfo">$250</span><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></div></div></li>
    """

    return sample_listing


@pytest.fixture
def sample_thumb():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-thumb" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="result-node"><a class="cl-app-anchor text-only result-thumb" tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html"><img class="cl-thumb" loading="lazy" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_50x50c.jpg" alt="Paiste Twenty Masters prototype 21 ride cymbal 1"></a><div class="result-info"><div class="supertitle">LA</div><div class="title-blob"><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only posting-title"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal</span></a></div><div class="meta"><span title="Sun Feb 04 2024 18:23:02 GMT+0800 (Malaysia Time)">5h ago</span><span class="separator">·</span><span class="priceinfo">$250</span><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></div></div></div></li>
    """

    return sample_listing


@pytest.fixture
def sample_preview():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-card previewing" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="result-node"><div class="card-content"><div class="card-image-wrapper "><img class="card-image" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg" alt="Paiste Twenty Masters prototype 21 ride cymbal 1"></div><div class="meta"><div class="location">LA</div><div class="posting-title">Paiste Twenty Masters prototype 21 ride cymbal</div><span class="priceinfo">$250</span><div class="bottom-row"><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></div></div></div></div></li>
    """

    post_preview = """
<div class="posting-viewer" style="inset: 199px 0px 48px 570px; z-index: 5991; position: fixed;"><div class="cl-posting-viewer"><div class="cl-single-posting"><div class="posting-actions"><div class="reply-button open-to-the-right cl-reply-button"><button>reply</button></div><button type="button" tabindex="0" class="bd-button cl-favorite-button" title="add to favorites list"><span class="icon icom-"></span><span class="label">favorite</span></button><button type="button" tabindex="0" class="bd-button cl-banish-button" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button><button type="button" tabindex="0" class="cl-flag-button flag-posting"><span class="icon icom-"></span><span class="label">flag</span></button><div class="share-posting cl-share-button"><div class="container"><a href="https://losangeles.craigslist.org/search/sss#search=1~card~0~0#share"><div class="icom- share-icon"></div><span class="action-label">share</span></a><div class="menu-container"></div></div></div><div class="posted-date cl-posted-time">Posted <span class="time-ago">5h ago</span></div></div><div class="posting-title"><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal - $250</span></a></div><div class="main-layout"><div class="left-col"><div class="posting-gallery cl-gallery click-to-zoom"><div class="gallery-inner" style="width: 565px; height: 423.75px;"><div class="main" href=""><div class="swipe" style="visibility: visible;"><div class="swipe-wrap" style="width: 4520px;"><div style="width: 565px; height: 423.75px; left: 0px; transition-duration: 0ms; transform: translateX(0px);" data-index="0"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal - $250 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_600x450.jpg"></div><div style="width: 565px; height: 423.75px; left: -565px; transition-duration: 0ms; transform: translateX(565px);" data-index="1"></div><div style="width: 565px; height: 423.75px; left: -1130px; transition-duration: 0ms; transform: translateX(565px);" data-cloned="true" data-index="2"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal - $250 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_600x450.jpg"></div><div style="width: 565px; height: 423.75px; left: -1695px; transition-duration: 0ms; transform: translateX(-565px);" data-cloned="true" data-index="3"></div></div></div><div class="slider-back-arrow icom-"></div><div class="slider-forward-arrow icom-"></div></div></div><div class="thumbnails"><img class="thumb-img selected" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_50x50c.jpg"><img class="thumb-img" src="https://images.craigslist.org/00j0j_4EoCuv4GxTu_0re0kq_50x50c.jpg"></div></div><div class="posting-description">Never played. Brand spankin' new.<br>
<br>
21" ride cymbal.<br>
The Twenty series has evolved into the Masters series.<br>
<br>
Being a prototype, you will be the only one to have this unique cymbal sound<br>
<br>
This one is lighter than the regular Twenty series ride if you've ever played that one.<br>
<br>
The Twenty line was one of the best that Paiste made. They used the same Diril formula alloy which is still used on the Meinl Byzance cymbals. That gave the Twenty line that sweet Turkish sound.<br>
</div></div><div class="right-col"><div class="single-posting-map cl-posting-map"><div id="putPostingMapHere" class="leaflet-container leaflet-touch leaflet-retina leaflet-fade-anim leaflet-grab leaflet-touch-drag leaflet-touch-zoom" style="width: 300px; height: 300px; position: relative;" tabindex="0"><div class="leaflet-pane leaflet-map-pane" style="transform: translate3d(0px, 0px, 0px);"><div class="leaflet-pane leaflet-tile-pane"><div class="leaflet-layer " style="z-index: 1; opacity: 1;"><div class="leaflet-tile-container leaflet-zoom-animated" style="z-index: 18; transform: translate3d(0px, 0px, 0px) scale(1);"><img alt="" src="//map5.craigslist.org/t09/12/701/1634.png" class="leaflet-tile leaflet-tile-loaded" style="width: 256px; height: 256px; transform: translate3d(-106px, -75px, 0px); opacity: 1;"><img alt="" src="//map6.craigslist.org/t09/12/702/1634.png" class="leaflet-tile leaflet-tile-loaded" style="width: 256px; height: 256px; transform: translate3d(150px, -75px, 0px); opacity: 1;"><img alt="" src="//map6.craigslist.org/t09/12/701/1635.png" class="leaflet-tile leaflet-tile-loaded" style="width: 256px; height: 256px; transform: translate3d(-106px, 181px, 0px); opacity: 1;"><img alt="" src="//map7.craigslist.org/t09/12/702/1635.png" class="leaflet-tile leaflet-tile-loaded" style="width: 256px; height: 256px; transform: translate3d(150px, 181px, 0px); opacity: 1;"></div></div></div><div class="leaflet-pane leaflet-overlay-pane"></div><div class="leaflet-pane leaflet-shadow-pane"><img src="https://www.craigslist.org/images/map/marker-shadow.png" class="leaflet-marker-shadow leaflet-zoom-animated" alt="" style="margin-left: -12px; margin-top: -41px; width: 41px; height: 41px; transform: translate3d(150px, 150px, 0px);"></div><div class="leaflet-pane leaflet-marker-pane"><img src="https://www.craigslist.org/images/map/marker-icon-2x.png" class="leaflet-marker-icon leaflet-zoom-animated leaflet-interactive" alt="Marker" tabindex="0" role="button" style="margin-left: -12px; margin-top: -41px; width: 25px; height: 41px; transform: translate3d(150px, 150px, 0px); z-index: 150;"></div><div class="leaflet-pane leaflet-tooltip-pane"></div><div class="leaflet-pane leaflet-popup-pane"></div><div class="leaflet-proxy leaflet-zoom-animated" style="transform: translate3d(179712px, 418529px, 0px) scale(2048);"></div></div><div class="leaflet-control-container"><div class="leaflet-top leaflet-left"><div class="leaflet-control-zoom leaflet-bar leaflet-control"><a class="leaflet-control-zoom-in" href="#" title="Zoom in" role="button" aria-label="Zoom in" aria-disabled="false"><span aria-hidden="true">+</span></a><a class="leaflet-control-zoom-out" href="#" title="Zoom out" role="button" aria-label="Zoom out" aria-disabled="false"><span aria-hidden="true">−</span></a></div></div><div class="leaflet-top leaflet-right"></div><div class="leaflet-bottom leaflet-left"></div><div class="leaflet-bottom leaflet-right"><div class="leaflet-control-attribution leaflet-control">© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a></div></div></div></div></div><div class="posting-attribs cl-posting-attributes"><div class="attrib-group"></div></div></div></div><div class="footer-misc cl-footer-misc"><ul class="general-notices"></ul><div class="common"><div>post id: 7711806132</div><div class="cl-posted-time">posted: <span class="time-ago">5h ago</span></div><div class="cl-posted-time">updated: <span class="time-ago">5h ago</span></div><div class="best-of-link"><span class="heart">♥ </span><a class="link" href="">best of</a><sup> [<a href="https://www.craigslist.org/about/best/all">?</a>]</sup></div></div><div class="for-sale-notices"><div><a href="https://www.craigslist.org/about/scams">Avoid scams, deal locally!</a> Beware wiring (e.g. Western Union), cashier checks, money orders, shipping.</div></div></div></div></div></div>
    """

    return sample_listing, post_preview


@pytest.fixture
def sample_grid():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-grid" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="result-node"><div class="cl-gallery"><div class="gallery-inner" style="width: 214px; height: 160.5px;"><a class="main" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html"><div class="swipe" style="visibility: visible;"><div class="swipe-wrap" style="width: 1712px;"><div style="width: 214px; height: 160.5px; left: 0px; transition-duration: 0ms; transform: translateX(0px);" data-index="0"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg"></div><div style="width: 214px; height: 160.5px; left: -214px; transition-duration: 0ms; transform: translateX(214px);" data-index="1"></div><div style="width: 214px; height: 160.5px; left: -428px; transition-duration: 0ms; transform: translateX(214px);" data-cloned="true" data-index="2"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg"></div><div style="width: 214px; height: 160.5px; left: -642px; transition-duration: 0ms; transform: translateX(-214px);" data-cloned="true" data-index="3"></div></div></div><div class="slider-back-arrow icom-"></div><div class="slider-forward-arrow icom-"></div></a></div><div class="dots"><span class="dot selected">•</span><span class="dot">•</span></div></div><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only posting-title"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal</span></a><div class="meta">5h ago<span class="separator">·</span>LA</div><span class="priceinfo">$250</span><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></div></li>
    """

    return sample_listing


@pytest.fixture
def sample_gallery():
    sample_listing = """
<li data-pid="7711806132" class="cl-search-result cl-search-view-mode-gallery" title="Paiste Twenty Masters prototype 21 ride cymbal"><div class="gallery-card"><div class="cl-gallery"><div class="gallery-inner"><a class="main" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html"><div class="swipe" style="visibility: visible;"><div class="swipe-wrap" style="width: 2560px;"><div data-index="0" style="width: 320px; left: 0px; transition-duration: 0ms; transform: translateX(0px);"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg"></div><div data-index="1" style="width: 320px; left: -320px; transition-duration: 0ms; transform: translateX(320px);"></div><div data-cloned="true" data-index="2" style="width: 320px; left: -640px; transition-duration: 0ms; transform: translateX(320px);"><span class="loading icom-"></span><img alt="Paiste Twenty Masters prototype 21 ride cymbal 1" src="https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg"></div><div data-cloned="true" data-index="3" style="width: 320px; left: -960px; transition-duration: 0ms; transform: translateX(-320px);"></div></div></div><div class="slider-back-arrow icom-"></div><div class="slider-forward-arrow icom-"></div></a></div><div class="dots"><span class="dot selected">•</span><span class="dot">•</span></div></div><a tabindex="0" href="https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html" class="cl-app-anchor text-only posting-title"><span class="label">Paiste Twenty Masters prototype 21 ride cymbal</span></a><div class="meta">5h ago<span class="separator">·</span>LA</div><span class="priceinfo">$250</span><button type="button" tabindex="0" class="bd-button cl-favorite-button icon-only" title="add to favorites list"><span class="icon icom-"></span><span class="label"></span></button><button type="button" tabindex="0" class="bd-button cl-banish-button icon-only" title="hide posting"><span class="icon icom-"></span><span class="label">hide</span></button></div></li>
    """

    return sample_listing


@pytest.fixture(
    params=[
        "sample_list",
        "sample_narrow_list",
        "sample_thumb",
        "sample_grid",
        "sample_gallery",
    ]
)
def sample_data(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def process_sample_data(sample_data):
    posts_data = []
    scraped_img_tag_src = set()
    soup = BeautifulSoup(sample_data, "html.parser")
    for div in soup.find_all("li", {"class": "cl-search-result"}):
        img_tag = div.find("img")
        if img_tag:
            img_tag_src = img_tag.get("src")
            if img_tag_src not in scraped_img_tag_src:
                posts_data.extend(div)
                scraped_img_tag_src.add(img_tag_src)
        else:
            post_url = div.find("a", {"class": "posting-title"})
            if post_url:
                img_tag_src = post_url.get("href")
                if img_tag_src not in scraped_img_tag_src:
                    posts_data.extend(div)
                    scraped_img_tag_src.add(img_tag_src)

    return posts_data


def test_list_organize_listing_data(process_sample_data):
    posts_data = process_sample_data
    url = "https://kent.craigslist.org/"
    makes_images = False
    craigslist_posts = identify_cl_item_type(url, posts_data, makes_images)

    assert craigslist_posts[0].title == "Paiste Twenty Masters prototype 21 ride cymbal"
    assert craigslist_posts[0].price == "$250"
    assert craigslist_posts[0].timestamp == "5h ago"
    assert craigslist_posts[0].location == "LA"
    assert (
        craigslist_posts[0].post_url
        == "https://losangeles.craigslist.org/lac/msg/d/los-angeles-paiste-twenty-masters/7711806132.html"
    )
    assert craigslist_posts[0].post_id == "7711806132"

    if isinstance(craigslist_posts[0], (List, Narrow_list, Thumb, Preview)):
        assert craigslist_posts[0].date == "5h ago"

    if isinstance(craigslist_posts[0], (Thumb)):
        assert (
            craigslist_posts[0].image_url
            == "https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_50x50c.jpg"
        )
        assert craigslist_posts[0].image_path == "No image path"

    if isinstance(craigslist_posts[0], (Preview)):
        assert (
            craigslist_posts[0].image_urls
            == "https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_50x50c.jpg"
        )
        assert craigslist_posts[0].image_paths == "No image path"
        assert craigslist_posts[0].post_description == ""
        assert craigslist_posts[0].address_info == ""
        assert craigslist_posts[0].attribute == ""

    if isinstance(craigslist_posts[0], (Grid, Gallery)):
        assert (
            craigslist_posts[0].image_url
            == "https://images.craigslist.org/00000_iNU1yYVig1e_0CI0t2_300x300.jpg"
        )
        assert craigslist_posts[0].image_path == "No image path"


def test_identify_cl_item_type(process_sample_data):
    url = "https://kent.craigslist.org/"
    make_images = False
    cl_item_data = identify_cl_item_type(url, process_sample_data, make_images)

    assert isinstance(cl_item_data[0], CL_item)
