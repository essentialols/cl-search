import os
import pandas as pd
import sys
import logging

launcher_path = sys.argv[2]

logger = logging.getLogger("filter_csv_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/filter_csv.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))


def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = [word.strip().lower() for word in file]
    return words


def filter_csv_by_words_and_image(csv_file, phrases_to_filter, protected_phrases):
    df = pd.read_csv(csv_file)

    if phrases_to_filter:
        for index, row in df.iterrows():
            title = row['title'].lower()
            for phrase in phrases_to_filter:
                if phrase in title and not any(protected in title for protected in protected_phrases):
                    df = df.drop(index)
                    break

    df = df.drop_duplicates(subset=['title', 'image_path'], keep='first')
    return df


def save_filtered_csv(filtered_df, output_file):
    filtered_df.to_csv(output_file, index=False)


sheets_folder = f"{launcher_path}/sheets"
filter_words = f"{launcher_path}/filter_words.txt"
protected_words = f"{launcher_path}/protected_words.txt"
output_folder = f"{launcher_path}/filtered"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

phrases_to_filter = read_words_from_file(filter_words)
protected_phrases = read_words_from_file(protected_words)

for root, _, files in os.walk(sheets_folder):
    for file in files:
        if file.lower().endswith('.csv'):
            csv_file = os.path.join(root, file)
            print(f"Currently processing {file}")

            filtered_df = filter_csv_by_words_and_image(csv_file, phrases_to_filter, protected_phrases)

            output_file = os.path.join(output_folder, file)
            save_filtered_csv(filtered_df, output_file)

print("Filtering Complete!")
