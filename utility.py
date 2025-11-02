import re
import os
import csv
import zipfile
from datetime import datetime

pattern = re.compile('[\W_]+')


def normalize(name):
    return pattern.sub('_', name.strip()).lower().strip()


def file_extracter(zip_path, folder, meta_file, csv_path):

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            # Skip directories
            if member.is_dir():
                continue

            # Get only the filename (remove folder paths inside ZIP)
            filename = os.path.basename(member.filename)
            if not filename:
                # skip empty names
                continue

            # Target file path (flattened)
            target_path = os.path.join(folder, filename)

            # Extract the file
            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

        image_data = []
        current_datetime = datetime.now()
        # formatting date and time
        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H-%M-%S")

        for filename in os.listdir((folder)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(folder, filename)
                size_kb = round(os.path.getsize(path) / 1024, 2)
                image_data.append([
                                    filename,
                                    size_kb,
                                    date,
                                    time,
                                    meta_file,
                                    "Not Processed"])

        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'size', 'date', 'time', 'meta_file', 'status'])
            writer.writerows(image_data)