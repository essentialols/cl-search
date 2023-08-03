import os
import pandas as pd

def get_image_paths_from_csv(csv_file):
    image_paths = []
    with open(csv_file, 'r') as file:
        csv_reader = pd.read_csv(file)
        if 'image_path' in csv_reader.columns:
            image_paths.extend(csv_reader['image_path'].tolist())
    return image_paths

def get_all_image_files(folder_path):
    image_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append(os.path.join(folder_path, file))
    return image_files

sheets_folder = f"{launcher_path}/sheets"
images_folder = f"{launcher_path}/images/cl_images"

all_image_paths = []

for root, _, files in os.walk(sheets_folder):
    for file in files:
        if file.lower().endswith('.csv'):
            csv_file = os.path.join(root, file)
            print(f"Currently reading {file}")
            all_image_paths.extend(get_image_paths_from_csv(csv_file))

all_images = get_all_image_files(images_folder)

extra_images = list(set(all_images) - set(all_image_paths))

if extra_images:
    for image in extra_images:
        if os.path.exists(image):
            os.remove(image)
            print(f"Removed {image}")
else:
    print("There are no images to remove")