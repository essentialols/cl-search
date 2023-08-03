import os
import pandas as pd

def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = [word.strip() for line in file for word in line.split()]
    return words

def filter_csv_by_words(csv_file, words):
    df = pd.read_csv(csv_file)
    df = df[~df['title'].str.lower().str.contains('|'.join(words), na=False)]
    return df

def save_filtered_csv(filtered_df, output_file):
    filtered_df.to_csv(output_file, index=False)

sheets_folder = f"{launcher_path}/sheets"
words_file = "filter_words.txt"
output_folder = f"{launcher_path}/sheets/filtered"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

words_to_filter = read_words_from_file(words_file)

for root, _, files in os.walk(sheets_folder):
    for file in files:
        if file.lower().endswith('.csv'):
            csv_file = os.path.join(root, file)
            print(f"Currently processing {file}")

            filtered_df = filter_csv_by_words(csv_file, words_to_filter)

            output_file = os.path.join(output_folder, file)
            save_filtered_csv(filtered_df, output_file)

print("Filtering Complete!")
