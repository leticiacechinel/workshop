# src/data_ingestion.py

import os
import gdown  # Use gdown instead of requests for Google Drive files
from zipfile import ZipFile
import pandas as pd
import chardet  # Library for detecting file encoding

def download_and_unzip(url, extract_to):
    """
    Downloads a ZIP file from a Google Drive URL and extracts its contents to a specified directory.

    Parameters:
    - url (str): The Google Drive URL to download the ZIP file from.
    - extract_to (str): The directory to extract the files to.

    Returns:
    - extracted_csv_path (str): The path to the extracted CSV file.
    """
    local_zip_path = os.path.join(extract_to, 'data.zip')
    os.makedirs(extract_to, exist_ok=True)

    # Download the ZIP file with gdown
    try:
        print(f"Downloading data from {url}...")
        gdown.download(url, local_zip_path, quiet=False)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading the file: {e}")
        raise

    # Extract the ZIP file with exception handling
    try:
        with ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Files extracted to {extract_to}")
    except Exception as e:
        print(f"Error extracting the ZIP file: {e}")
        raise

    # Dynamically locate the extracted CSV file
    extracted_files = os.listdir(extract_to)
    csv_files = [file for file in extracted_files if file.lower().endswith('.csv')]

    if not csv_files:
        raise FileNotFoundError("No CSV file found in the extracted data.")

    # Use the first CSV file found
    extracted_csv_path = os.path.join(extract_to, csv_files[0])
    print(f"CSV file found: {csv_files[0]}")

    # Optional: Remove the ZIP file after extraction to save space
    os.remove(local_zip_path)

    return extracted_csv_path

def detect_encoding(file_path):
    """
    Detects the encoding of a text file.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - encoding (str): The detected encoding.
    """
    with open(file_path, 'rb') as f:
        # Read the first 100KB to detect encoding
        result = chardet.detect(f.read(100000))
    return result['encoding']

def save_data_to_csv(data, save_path, file_name):
    """
    Saves a DataFrame to a CSV file.

    Parameters:
    - data (pd.DataFrame): The DataFrame to save.
    - save_path (str): The directory to save the file in.
    - file_name (str): The name of the CSV file.
    """
    final_path = os.path.join(save_path, file_name)
    os.makedirs(save_path, exist_ok=True)
    data.to_csv(final_path, index=False)
    print(f"Data saved in {final_path}")

if __name__ == "__main__":
    # Mapping of years to their corresponding Google Drive file IDs
    year_file_id_mapping = {
        2021: "12xH8LX9aN2gObR766YN3cMcuycwyCJDz",
        2022: "1PRQjuV5gOn_nn6UNvaJyVURDIfbSAK4-",
        2023: "1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq",
        2024: "14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO"
    }

    # Directory to extract the files to
    extract_base_dir = '../data/raw'

    # Initialize an empty list to hold DataFrames
    data_frames = []

    for year, file_id in year_file_id_mapping.items():
        print(f"\nProcessing data for the year {year}...")
        # Create a unique extraction directory for each year
        extract_to = os.path.join(extract_base_dir, f'year_{year}')
        # Desired output CSV file name
        output_filename = f'datatran{year}.csv'

        # Construct the direct download URL
        url = f"https://drive.google.com/uc?export=download&id={file_id}"

        # Download and extract the data
        extracted_csv_path = download_and_unzip(url, extract_to)

        # Detect the encoding of the extracted CSV file
        encoding = detect_encoding(extracted_csv_path)
        print(f"Detected file encoding: {encoding}")

        # Read the CSV file with the detected encoding
        try:
            data = pd.read_csv(extracted_csv_path, sep=';', encoding=encoding)
            print("CSV file read successfully.")
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
            raise

        # Optional: Save individual year's data
        # save_data_to_csv(data, '../data/raw', output_filename)

        # Append the DataFrame to the list
        data_frames.append(data)

        # Optional: Clean up the extracted files to save space
        os.remove(extracted_csv_path)
        os.rmdir(extract_to)

    # Concatenate all DataFrames
    all_data = pd.concat(data_frames, ignore_index=True)
    print("\nAll data concatenated successfully.")

    # Save the combined data
    save_data_to_csv(all_data, '../data/raw', 'datatran_all_years.csv')
