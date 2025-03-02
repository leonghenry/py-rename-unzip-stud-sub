import csv
import os
import zipfile

def read_name_list(csv_path):
    # Create a dictionary to hold the data from the CSV
    student_dict = {}
    # Open and read the CSV file
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Store name, class, and team as a list associated with student_id
            student_dict[row['student_id']] = [row['name'], row['class'], row['team']]
    return student_dict

def rename_directory(target_directory, name_dict):
    # Iterate through all the directories in the target directory
    for item in os.listdir(target_directory):
        item_path = os.path.join(target_directory, item)
        if os.path.isdir(item_path):
            input_id = item[:8]  # Take the first 8 characters of the directory name
            if input_id in name_dict:
                name, class_, team = name_dict[input_id]
                sanitized_name = name.replace('/', '')
                new_name = f"{team}_{sanitized_name}_{input_id}"
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