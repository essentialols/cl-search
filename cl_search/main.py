from __future__ import annotations

import os
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import pandas as pd
from tqdm import tqdm

from cl_search.args import parse_my_args
from cl_search.craigslist import get_listing_data
from cl_search.craigslist import navigate_to_category
from cl_search.utils import get_current_time
from cl_search.write_dataframes import df_output
from cl_search.write_dataframes import get_default_options
from cl_search.write_dataframes import get_export_formats
from cl_search.write_dataframes import write_frames


def process_link(link: str, queue: Queue, **kwargs):
    driver = navigate_to_category(link, **kwargs)

    try:
        data = get_listing_data(link, driver, **kwargs)
        queue.put(data)

    except TimeoutError as e:
        print(f"Timeout error occurred for URL: {link}. Error: {e}")


def main(**kwargs) -> None:
    data_queue = Queue()
    collected_data = []

    output = kwargs.get("output", "csv")
    location_links = kwargs.get("location_links")
    location = kwargs.get("location", "")
    file_extension = kwargs.get("file_extension", "")
    search_query = kwargs.get("search_query", "")
    path = kwargs.get("output_path")

    # debug issue with multiprocessing webdrivers
    with ThreadPoolExecutor() as executor:
        f = [executor.submit(process_link, link, data_queue, **kwargs) for link in location_links]
        with tqdm(total=len(f), desc=f'Fetching {search_query} from {location.capitalize()} Craigslist') as pbar:
            for future in as_completed(f):
                pbar.update(1)

    while not data_queue.empty():
        collected_data.extend(data_queue.get())

    if output == "clipboard":
        write_frames(collected_data, **kwargs)
        print("Data is ready to paste")

    elif output == "sql":
        write_frames(collected_data, **kwargs)
        print(f"Created craigslist.{file_extension}")

    else:
        output_file = f"{path}/{location}_{search_query}.{file_extension}"
        df = pd.DataFrame([x.as_list() for x in collected_data])
        df.dropna(inplace=True)

        default_options = get_default_options()
        export_formats = get_export_formats(df)

        if output in export_formats:
            function_name, file_extension, file_read = export_formats[output]

        if output in default_options:
            write_options, append_options, read_options = default_options[output]

        if os.path.isfile(output_file):
            current_time = get_current_time()

            existing_data = file_read(output_file, **read_options)
            existing_post_ids = existing_data['post_id'].astype(str).tolist()

            for _, row in df.iterrows():
                if row['post_id'] in existing_post_ids:
                    existing_index = existing_data[existing_data['post_id'] == row['post_id']].index
                    existing_data.loc[existing_index, 'is_new'] = 0
                    existing_data.loc[existing_index, 'last_updated'] = current_time
                    columns_to_update = ["is_new", "last_updated", "title",
                                         "price", "timestamp", "location",
                                         "image_url", "image_path"]

                    for col in columns_to_update:
                        existing_data.loc[existing_index, col] = row[col]

            df_output(existing_data, write_options, **kwargs)

        else:
            write_frames(collected_data, **kwargs)

        if search_query:
            print(f"Created {location}_{search_query}.{file_extension}")

        else:
            print(f"Created {location}.{file_extension}")


def run() -> None:
    args = parse_my_args()
    main(**args)


if __name__ == '__main__':
    run()
