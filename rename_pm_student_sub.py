import csv
import os
import time
import zipfile
import shutil
from datetime import datetime

# Reads student metadata from a CSV file and returns a dictionary
# where the key is the cleaned, normalized name (uppercase, no commas, single spacing),
# and the value is a list [student_id, class, team]
def read_name_list(csv_path):
    student_dict = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            clean_name = ' '.join(row['name'].strip().upper().replace(',', '').split())
            student_dict[clean_name] = [row['student_id'], row['class'], row['team']]
    return student_dict

# Extracts the student name from the folder name string.
# Assumes the format: "<some id> - <name> SOI..."
# Returns a cleaned, normalized name string.
def extract_name_from_folder(folder_name):
    try:
        start = folder_name.index(' - ') + 3
        end = folder_name.index(' SOI')
        name_part = folder_name[start:end].strip()
        name_part = name_part.replace(',', '')          # remove commas
        name_part = ' '.join(name_part.split())         # normalize spacing
        return name_part
    except ValueError:
        return ""

# Recursively merges the contents of one folder into another.
# Handles both files and subdirectories.
# If a filename already exists in the destination, appends _1, _2, etc.
def merge_folder_contents(src_folder, dst_folder, log_file):
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dst_path = os.path.join(dst_folder, item)

        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                log_file.write(f"  Recursively merging folder: {src_path} → {dst_path}\n")
                merge_folder_contents(src_path, dst_path, log_file)
            else:
                shutil.move(src_path, dst_path)
                log_file.write(f"  Moved folder: {src_path} → {dst_path}\n")
        else:
            base, ext = os.path.splitext(item)
            counter = 1
            while os.path.exists(dst_path):
                dst_path = os.path.join(dst_folder, f"{base}_{counter}{ext}")
                counter += 1
            shutil.move(src_path, dst_path)
            log_file.write(f"  Moved file: {src_path} → {dst_path}\n")

# Renames student folders using team_name + cleaned_name + student_id.
# If the target folder already exists, merges content into it.
# Logs all actions to a log file.
def rename_directory(target_directory, name_dict, log_path):
    with open(log_path, 'w', encoding='utf-8') as log_file:
        for item in os.listdir(target_directory):
            item_path = os.path.join(target_directory, item)
            if os.path.isdir(item_path):
                extracted_name = extract_name_from_folder(item)
                name_key = extracted_name.strip().upper()
                if name_key in name_dict:
                    student_id, class_, team = name_dict[name_key]
                    sanitized_name = extracted_name.replace('/', '')
                    new_name = f"{team}_{sanitized_name}_{student_id}"
                    new_path = os.path.join(target_directory, new_name)

                    if os.path.exists(new_path):
                        log_file.write(f"\nMERGE: '{item}' → existing '{new_name}'\n")
                        merge_folder_contents(item_path, new_path, log_file)
                        os.rmdir(item_path)
                        print(f"Merged and removed folder '{item}'")
                    else:
                        os.rename(item_path, new_path)
                        print(f"Renamed '{item}' to '{new_name}'")
                else:
                    print(f"[SKIPPED] Name '{extracted_name}' not found in CSV.")
                    log_file.write(f"\nSKIPPED: '{item}' → No match for extracted name '{extracted_name}'\n")

# Recursively unzips all ZIP files in a given directory (and subdirectories),
# restoring the original timestamps.
def unzip_all_zip_files(directory):
    while True:
        found_zip = False
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.zip'):
                    zip_path = os.path.join(root, filename)
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            for zip_info in zip_ref.infolist():
                                extracted_path = zip_ref.extract(zip_info, path=root)
                                date_time = time.mktime(zip_info.date_time + (0, 0, -1))
                                os.utime(extracted_path, (date_time, date_time))
                        print(f"Unzipped {filename} in {root}")
                        os.remove(zip_path)  # Optional: delete zip after extraction
                        found_zip = True
                    except zipfile.BadZipFile:
                        print(f"Failed to unzip {filename} - not a zip file or corrupted.")
        if not found_zip:
            break


# Creates a hierarchical text report of all student submission folders.
# Each directory is listed with its internal files and subfolders, indented by level.
def write_submission_report(directory, report_filename="submission_report.txt"):
    report_path = os.path.join(directory, report_filename)
    top_items = sorted(os.listdir(directory))  # Sort once at the top

    with open(report_path, 'w', encoding='utf-8') as rpt:
        for folder in top_items:
            folder_path = os.path.join(directory, folder)
            if os.path.isdir(folder_path):
                rpt.write(f"{folder}\n")
                for root, dirs, files in os.walk(folder_path):
                    level = root.replace(folder_path, '').count(os.sep) + 1
                    indent = '  ' * level

                    for d in sorted(dirs):
                        rpt.write(f"{indent}{d}/\n")

                    for f in sorted(files):
                        f_path = os.path.join(root, f)
                        mtime = os.path.getmtime(f_path)
                        timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                        rpt.write(f"{indent}{f} ({timestamp})\n")
                rpt.write("\n")
        rpt.write("End of Report\n")
    print(f"📄 Submission report saved to: {report_path}")


# Main execution block
if __name__ == "__main__":
    target_directory = input("Enter Full Path of the Directory containing students submission: ").strip()
    if not os.path.exists(target_directory):
        print("The specified directory does not exist. Please check the path and try again.")
    else:
        csv_path = input("Enter Full Path + CSV Filename that has (student_id + name + class + team): ").strip()
        if not os.path.isfile(csv_path):
            print("The specified CSV file does not exist. Please check the path and try again.")
        else:
            unzip_all_zip_files(target_directory)

            name_dict = read_name_list(csv_path)
            log_file_path = os.path.join(target_directory, 'merge_log.txt')
            rename_directory(target_directory, name_dict, log_file_path)

            write_submission_report(target_directory)

            print(f"\n✅ Merge log saved to: {log_file_path}")

