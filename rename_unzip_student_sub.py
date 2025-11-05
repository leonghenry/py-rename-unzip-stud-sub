import csv
import os
import zipfile
import re

def read_name_list(csv_path):
    # Create a dictionary to hold the data from the CSV
    student_dict = {}
    # Open and read the CSV file
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # KEY BY NAME (2nd column). Store student_id, class, team as value.
            student_dict[row['name']] = [row['student_id'], row['class'], row['team']]
    return student_dict

def rename_directory(target_directory, name_dict):
    # Iterate through all the directories in the target directory
    for item in os.listdir(target_directory):
        item_path = os.path.join(target_directory, item)
        if os.path.isdir(item_path):
            # Extract student name between " - " and " SOI"
            m = re.search(r'-\s*(.*?)\s*SOI', item, flags=re.IGNORECASE)
            if not m:
                print(f"Name not found in '{item}'")
                continue

            extracted_name = m.group(1).strip()

            # Look up by NAME in name_dict
            if extracted_name in name_dict:
                student_id, class_, team = name_dict[extracted_name]
                sanitized_name = extracted_name.replace('/', '')
                new_name = f"{team}_{sanitized_name}_{student_id}"
                new_path = os.path.join(target_directory, new_name)
                os.rename(item_path, new_path)
                print(f"Renamed '{item}' to '{new_name}'")

def unzip_files_in_subdirectories(directory):
    # Change the working directory to the specified directory
    os.chdir(directory)
    # Iterate over the items in the directory
    for item in os.listdir():
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            for filename in os.listdir(item_path):
                if filename.endswith('.zip'):
                    zip_path = os.path.join(item_path, filename)
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(item_path)
                        print(f"Unzipped {filename} in {item_path}")
                    except zipfile.BadZipFile:
                        print(f"Failed to unzip {filename} - not a zip file or corrupted.")

if __name__ == "__main__":
    target_directory = input("Enter the dir. containing student submission: ")
    if not os.path.exists(target_directory):
        print("The specified directory does not exist. Please check the path and try again.")
    else:
        csv_path = input("Enter the filename that has student name and group (full path + filename needed): ")
        if not os.path.isfile(csv_path):
            print("The specified CSV file does not exist. Please check the path and try again.")
        else:
            name_dict = read_name_list(csv_path)
            rename_directory(target_directory, name_dict)
            unzip_files_in_subdirectories(target_directory)