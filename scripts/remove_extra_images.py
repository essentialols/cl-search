import os
import pandas as pd
import requests
import sys

launcher_path = sys.argv[2]

csv_sheets_fold = f"{launcher_path}/filtered"
cl_images_fold = f"{launcher_path}/images/cl_images"

def get_image_paths_from_csv(csv_file):
    image_paths = set()
    with open(csv_file, 'r') as file:
        csv_reader = pd.read_csv(file)
        if 'image_path' in csv_reader.columns:
            valid_paths = csv_reader[csv_reader['image_path'].str.startswith(f'{cl_images_fold}')]
            image_paths.update(valid_paths['image_path'].tolist())
    return list(image_paths)

def get_all_image_files(folder_path):
    image_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append(os.path.join(folder_path, file))
    return image_files

def main():
    all_image_paths = []

    for root, _, files in os.walk(csv_sheets_fold):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_file = os.path.join(root, file)
                print(f"Currently reading {file}")
                all_image_paths.extend(get_image_paths_from_csv(csv_file))

    all_images = get_all_image_files(csv_sheets_fold)

    extra_images = list(set(all_images) - set(all_image_paths))

    if extra_images:
        for image in extra_images:
            if os.path.exists(image):
                os.remove(image)
                print(f"Removed {image}")
    else:
        print("There are no images to remove")

    reloaded_image_paths = []

    for root, _, files in os.walk(csv_sheets_fold):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_file = os.path.join(root, file)
                reloaded_image_paths.extend(get_image_paths_from_csv(csv_file))

    missing_images = list(set(reloaded_image_paths) - set(all_images))

    if missing_images:
        missing_image_urls = {}

        for missing_image_path in missing_images:
            for root, _, files in os.walk(csv_sheets_fold):
                for file in files:
                    if file.lower().endswith('.csv'):
                        csv_file = os.path.join(root, file)
                        with open(csv_file, 'r') as file:
                            csv_reader = pd.read_csv(file)
                            if 'image_path' in csv_reader.columns and 'image_url' in csv_reader.columns:
                                matching_row = csv_reader[csv_reader['image_path'] == missing_image_path]
                                if not matching_row.empty:
                                    missing_image_urls[missing_image_path] = matching_row['image_url'].iloc[0]
                                    break

        for missing_image_path, image_url in missing_image_urls.items():
            image_filename = image_url.split('/')[-1]
            image_path = os.path.join(cl_images_fold, image_filename)

            if not os.path.exists(image_path):
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_path, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"Downloaded missing image: {image_path}")
                else:
                    print(f"Failed to download image from URL: {image_url}")
            else:
                print(f"Image already exists: {image_path}")

    else:
        print("Verification complete: No missing images found.")

if __name__ == "__main__":
    main()
