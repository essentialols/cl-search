import logging
import requests
from cl_search.utils import download_images
from cl_search.utils import get_city_name
from cl_search.utils import get_current_time
from cl_search.utils import parse_post_id
from cl_search.utils import split_url_size

# Set up logging to print to the console
logging.basicConfig(level=logging.DEBUG)

class CL_item:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def as_dict(self):
        return self.__dict__

    def as_list(self):
        return list(self.__dict__.values())

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        raise NotImplementedError("This method should be overridden in subclasses")


class List(CL_item):
    kind = "list"

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        logging.debug(f"Using List class for processing posts.")
        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []

        for posts in posts_data:
            # Extract the title
            logging.debug(f"Extracting title.")
            title = getattr(posts.select_one("a span.label"), "text", None)
            logging.debug(f"Title extracted: {title}")
            
            # Extract the price
            logging.debug(f"Extracting price.")
            price_element = posts.find("span", "priceinfo")
            price = price_element.text.strip() if price_element else "Price not given"
            logging.debug(f"Price extracted: {price}")

            # Extract the post URL
            logging.debug(f"Extracting post URL.")
            post_url = posts.find("a", "posting-title").get("href") if posts.find("a", "posting-title") else ""
            logging.debug(f"Post URL extracted: {post_url}")

            # Extract the timestamp
            logging.debug(f"Extracting timestamp.")
            timestamp = getattr(posts.select_one('span[title*="GMT"]'), "text", None)
            logging.debug(f"Timestamp extracted: {timestamp}")

            # Extract location and date information
            logging.debug(f"Extracting location and date.")
            meta = posts.find("span", class_="meta")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    date = meta_info.split(separator.text)[2]
                    if date.endswith("pichide"):
                        date = date[:-7]
                    location = meta_info.split(separator.text)[1]
                    if location.strip() == "":
                        location = f"{city_name} area"
            else:
                date = None
                location = f"{city_name} area"
            logging.debug(f"Location: {location}, Date: {date}")

            # Extract the post ID
            logging.debug(f"Extracting post ID.")
            post_id = parse_post_id(post_url)
            logging.debug(f"Post ID extracted: {post_id}")

            # Extract post description
            logging.debug(f"Extracting post description from the detailed post page.")
            post_description = cls.fetch_post_description(post_url)
            logging.debug(f"Final post description: {post_description}")

            # Extract address info and attributes (if available)
            logging.debug(f"Extracting address info and attributes.")
            address_info = posts.find("div", class_="address-info")
            attribute = posts.find_all("div", "attrib")

            # Placeholder for image URLs and paths (assuming it's required)
            image_urls = []
            image_paths = []

            # Extract images (if available)
            logging.debug(f"Extracting image info.")
            image_url_src = posts.find("img").get("src") if posts.find("img") else ""
            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{kwargs.get("output_path", "./")}/images/no_image.png'
            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if kwargs.get("images_mode") else "No image path"
            logging.debug(f"Image URL: {image_url}, Image Path: {image_path}")

            image_urls.append(image_url)
            image_paths.append(image_path)

            # Append the extracted data to the list
            logging.debug(f"Appending post data to craigslist_posts.")
            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    date=date,
                    post_url=post_url,
                    post_description=post_description,
                    post_id=post_id,
                    image_urls=image_urls,
                    image_paths=image_paths,
                    address_info=address_info,
                    attribute=attribute,
                )
            )
        logging.debug(f"Finished processing posts in List class.")
        return craigslist_posts
    
@staticmethod
def fetch_post_description(post_url):
    if post_url:
        try:
            logging.debug(f"Fetching post details from URL: {post_url}")
            response = requests.get(post_url)
            if response.status_code == 200:
                detailed_soup = BeautifulSoup(response.text, 'html.parser')

                # Extract post description
                logging.debug(f"Extracting post description.")
                post_description = detailed_soup.select_one('#postingbody')

                if post_description:
                    # Limit the logging of raw HTML to avoid large outputs
                    logging.debug(f"Raw post description: {str(post_description)[:100]}...")  # Limit to the first 100 characters
                    post_description = post_description.decode_contents().strip()  # Extract inner HTML
                    logging.debug(f"Post description found: {post_description[:100]}...")  # Print first 100 characters
                else:
                    post_description = "No description provided"
                    logging.debug("No post description found.")


                return post_description

            else:
                logging.debug(f"Failed to retrieve post page. Status code: {response.status_code}")
                return "Failed to retrieve description"
        except Exception as e:
            logging.error(f"Error fetching post description: {e}")
            return "Error fetching description"
    else:
        logging.debug(f"No post URL found, skipping description extraction.")
        return "No description provided"




class Narrow_list(CL_item):
    kind = "narrow list"

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        logging.debug(f"Using Narrow_list class for processing posts.")
        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []

        for posts in posts_data:
            # Extract the title
            logging.debug(f"Extracting title.")
            title = getattr(posts.select_one("a span.label"), "text", None)
            logging.debug(f"Title extracted: {title}")
            
            # Extract the price
            logging.debug(f"Extracting price.")
            price_element = posts.find("span", "priceinfo")
            price = price_element.text.strip() if price_element else "Price not given"
            logging.debug(f"Price extracted: {price}")

            # Extract the post URL
            logging.debug(f"Extracting post URL.")
            post_url = posts.find("a", "posting-title").get("href") if posts.find("a", "posting-title") else ""
            logging.debug(f"Post URL extracted: {post_url}")

            # Extract the timestamp
            logging.debug(f"Extracting timestamp.")
            timestamp = getattr(posts.select_one('span[title*="GMT"]'), "text", None)
            logging.debug(f"Timestamp extracted: {timestamp}")

            # Extract location and date information
            logging.debug(f"Extracting location and date.")
            meta = posts.find("div", class_="supertitle")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    split_meta = meta_info.split(separator.text)
                    date = split_meta[0]
                    location = split_meta[1]
                else:
                    location = meta_info
                    date = timestamp
            else:
                date = None
                location = f"{city_name} area"
            logging.debug(f"Location: {location}, Date: {date}")

            # Extract the post ID
            logging.debug(f"Extracting post ID.")
            post_id = parse_post_id(post_url)
            logging.debug(f"Post ID extracted: {post_id}")

            # Extract post description
            logging.debug(f"Extracting post description.")
            post_description = posts.select_one('#postingbody')
            if post_description:
                post_description = post_description.decode_contents().strip()  # Extract inner HTML
            else:
                post_description = "No description provided"
            logging.debug(f"Final post description: {post_description}")

            # Extract address info and attributes (if available)
            logging.debug(f"Extracting address info and attributes.")
            address_info = posts.find("div", class_="address-info")
            attribute = posts.find_all("div", class_="attrib")

            # Placeholder for image URLs and paths
            logging.debug(f"Extracting image info.")
            image_urls = []
            image_paths = []
            image_url_src = posts.find("img").get("src") if posts.find("img") else ""
            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{kwargs.get("output_path", "./")}/images/no_image.png'
            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if kwargs.get("images_mode") else "No image path"
            logging.debug(f"Image URL: {image_url}, Image Path: {image_path}")

            image_urls.append(image_url)
            image_paths.append(image_path)

            # Append the extracted data to the list
            logging.debug(f"Appending post data to craigslist_posts.")
            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    date=date,
                    post_url=post_url,
                    post_description=post_description,
                    post_id=post_id,
                    image_urls=image_urls,
                    image_paths=image_paths,
                    address_info=address_info,
                    attribute=attribute
                )
            )
        logging.debug(f"Finished processing posts in Narrow_list class.")
        return craigslist_posts



class Thumb(CL_item):
    kind = "thumb"

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        # Get image mode and output path from kwargs
        images_mode = kwargs.get("images_mode", False)
        path = kwargs.get("output_path", "./")

        # Get city name and source info
        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []

        for posts in posts_data:
            # Extract the title
            title = getattr(posts.select_one("a span.label"), "text", None)
            
            # Extract the price
            price_element = posts.find("span", "priceinfo")
            price = price_element.text.strip() if price_element else "Price not given"

            # Extract the post URL
            post_url = posts.find("a", "posting-title").get("href") if posts.find("a", "posting-title") else ""

            # Extract the timestamp
            timestamp = getattr(posts.select_one('span[title*="GMT"]'), "text", None)

            # Extract location and date information
            meta = posts.find("div", class_="supertitle")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    split_meta = meta_info.split(separator.text)
                    date = split_meta[0]
                    location = split_meta[1]
                else:
                    location = meta_info
                    date = timestamp
            else:
                date = None
                location = f"{city_name} area"

            # Extract the post description
            post_description = posts.select_one('#postingbody')
            if post_description:
                post_description = post_description.decode_contents().strip()
            else:
                post_description = "No description provided"

            # Extract the image URL and image path
            image_url_src = posts.find("img").get("src") if posts.find("img") else ""
            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{path}/images/no_image.png'
            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if images_mode else "No image path"

            # Extract the post ID
            post_id = parse_post_id(post_url)

            # Append all data to the list
            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    date=date,
                    image_url=image_url,
                    post_url=post_url,
                    post_id=post_id,
                    image_path=image_path,
                    post_description=post_description  # Add post description
                )
            )

        return craigslist_posts



# unfinished
class Preview(CL_item):
    kind = "preview"

    # finish writing this
    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        images_mode = kwargs.get("images_mode")
        path = kwargs.get("output_path")

        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []
        image_paths = []
        attribute = []

        for posts in posts_data:
            title = getattr(posts.find("div", "posting-title"), "text", None)
            price_element = posts.find("span", "priceinfo")
            price = (
                price_element.text.strip()
                if price_element else "Price not given"
            )
            post_url_element = posts.select_one("div.posting-title a")
            post_url = post_url_element.get("href") if post_url_element else ""

            meta = posts.select_one("div.meta div.location")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    date = meta_info.split(separator.text)[0]
                    location = meta_info.split(separator.text)[1]
                    if location.strip() == "":
                        location = f"{city_name} area"
                else:
                    location = meta_info.split(separator.text)[0]

            timestamp = getattr(posts.find("span", "time-ago"), "text", None)
            post_description = posts.select_one('#postingbody')  # Using the CSS selector
            if post_description:
                post_description = post_description.decode_contents().strip()  # Get inner HTML and strip whitespace
            else:
                post_description = "No description provided"

            address_info = posts.find("div", "address-info")

            if address_info:
                pass

            attribute = posts.find_all("div", "attrib")

            if attribute:
                pass

            # rewrite for preview
            image_urls = []
            image_url_src = posts.find("img").get(
                "src") if posts.find("img") else ""

            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{path}/images/no_image.png'

            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if images_mode else "No image path"

            image_paths.append(image_path)
            post_id = parse_post_id(post_url)

            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    date=date,
                    post_url=post_url,
                    image_urls=image_urls,
                    post_id=post_id,
                    image_paths=image_paths,
                    post_description=post_description,
                    address_info=address_info,
                    attribute=attribute,
                )
            )

        return craigslist_posts



class Grid(CL_item):
    kind = "grid"

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        images_mode = kwargs.get("images_mode", False)
        path = kwargs.get("output_path", "./")

        # Get city name and source info
        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []

        for posts in posts_data:
            # Extract the title
            title = getattr(posts.select_one("a span.label"), "text", None)
            
            # Extract the price
            price_element = posts.find("span", "priceinfo")
            price = price_element.text.strip() if price_element else "Price not given"

            # Extract the post URL
            post_url = posts.find("a", "posting-title").get("href") if posts.find("a", "posting-title") else ""

            # Extract the timestamp and location
            meta = posts.find("div", class_="meta")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    split_meta = meta_info.split(separator.text)
                    timestamp = split_meta[0]
                    location = split_meta[1] if len(split_meta) > 1 else f"{city_name} area"
                else:
                    timestamp = None
                    location = f"{city_name} area"
            else:
                timestamp = None
                location = f"{city_name} area"

            # Extract the post description
            post_description = posts.select_one('#postingbody')
            if post_description:
                post_description = post_description.decode_contents().strip()  # Extract inner HTML
            else:
                post_description = "No description provided"

            # Extract the image URL and image path
            image_url_src = posts.find("img").get("src") if posts.find("img") else ""
            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{path}/images/no_image.png'
            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if images_mode else "No image path"

            # Extract the post ID
            post_id = parse_post_id(post_url)

            # Append all data to the list
            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    post_url=post_url,
                    image_url=image_url,
                    post_id=post_id,
                    image_path=image_path,
                    post_description=post_description  # Add post description
                )
            )

        return craigslist_posts



from cl_search.utils import download_images
from cl_search.utils import get_city_name
from cl_search.utils import get_current_time
from cl_search.utils import parse_post_id
from cl_search.utils import split_url_size

class Gallery(CL_item):
    kind = "gallery"

    @classmethod
    def organize_listing_data(cls, link: str, posts_data: list, **kwargs):
        images_mode = kwargs.get("images_mode", False)
        path = kwargs.get("output_path", "./")

        # Get city name and source info
        city_name = get_city_name(link)
        source_name = f"craigslist_{city_name}"
        current_time = get_current_time()

        craigslist_posts = []

        for posts in posts_data:
            # Extract the title
            title = getattr(posts.find("a", "posting-title"), "text", None)
            
            # Extract the price
            price_element = posts.find("span", "priceinfo")
            price = price_element.text.strip() if price_element else "Price not given"

            # Extract the post URL
            post_url = posts.find("a", "posting-title").get("href") if posts.find("a", "posting-title") else ""

            # Extract the timestamp and location
            meta = posts.find("div", class_="meta")
            if meta:
                meta_info = meta.get_text(strip=True)
                separator = meta.find("span", class_="separator")
                if separator:
                    split_meta = meta_info.split(separator.text)
                    timestamp = split_meta[0]
                    location = split_meta[1] if len(split_meta) > 1 else f"{city_name} area"
                else:
                    timestamp = None
                    location = f"{city_name} area"
            else:
                timestamp = None
                location = f"{city_name} area"

            # Extract the post description
            post_description = posts.select_one('#postingbody')
            if post_description:
                post_description = post_description.decode_contents().strip()  # Extract inner HTML
            else:
                post_description = "No description provided"

            # Extract the image URL and image path
            image_url_src = posts.find("img").get("src") if posts.find("img") else ""
            if image_url_src.strip() == "":
                image_url = "No image"
                image_path = f'{path}/images/no_image.png'
            else:
                base_image_src = split_url_size(image_url_src)
                image_url = str(base_image_src + '_600x450.jpg')
                image_path = download_images(image_url, **kwargs) if images_mode else "No image path"

            # Extract the post ID
            post_id = parse_post_id(post_url)

            # Append all data to the list
            craigslist_posts.append(
                cls(
                    source=source_name,
                    is_new=1,
                    time_added=current_time,
                    last_updated=current_time,
                    title=title,
                    price=price,
                    timestamp=timestamp,
                    location=location,
                    post_url=post_url,
                    image_url=image_url,
                    post_id=post_id,
                    image_path=image_path,
                    post_description=post_description  # Add post description
                )
            )

        return craigslist_posts



def identify_cl_item_type(link: str, posts_data: list, **kwargs):
    for posts in posts_data:
        result_node_wide = posts.parent.find("div", class_="result-node-wide")
        result_node_narrow = posts.parent.find(
            "div", class_="result-node-narrow")
        result_node = posts.parent.find("div", class_="result-node")
        gallery_card = posts.parent.find("div", class_="gallery-card")

        if result_node:
            card_content = posts.find("div", class_="card-content")
            cl_gallery = posts.find("div", class_="cl-gallery")

            if card_content:
                cl_item_data = Preview.organize_listing_data(
                    link, posts_data, **kwargs
                )
                return cl_item_data

            elif cl_gallery:
                cl_item_data = Grid.organize_listing_data(
                    link, posts_data, **kwargs
                )
                return cl_item_data

            else:
                cl_item_data = Thumb.organize_listing_data(
                    link, posts_data, **kwargs
                )
                return cl_item_data

        if result_node_wide:
            cl_item_data = List.organize_listing_data(
                link, posts_data, **kwargs
            )
            return cl_item_data

        if result_node_narrow:
            cl_item_data = Narrow_list.organize_listing_data(
                link, posts_data, **kwargs
            )
            return cl_item_data

        if gallery_card:
            cl_item_data = Gallery.organize_listing_data(
                link, posts_data, **kwargs
            )
            return cl_item_data

    return None
