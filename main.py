import os
import zipfile
import csv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import re

pattern = re.compile('[\W_]+')
def normalize(name):
    return pattern.sub('_', name.strip()).lower().strip()

app = Flask(__name__)
#Auto-reload templates without restarting the server
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# folders
UPLOAD_FOLDER = 'storage'
DATA_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

CSV_PATH = os.path.join(DATA_FOLDER, 'images.csv')


@app.route('/upload', methods=['POST'])
def upload():

    #checking all arguments existing
    if 'zipfile' not in request.files:
        msg= "No image file"

    if 'csv' not in request.files:
        msg= "No csv file"

    img_file = request.files['zipfile']
    csv_file = request.files['csv']

    # validating request values

    if not img_file.filename.lower().endswith('.zip'):
        msg = "Please upload a .zip file"

    if not csv_file.filename.lower().endswith('.csv'):
        msg = "Please upload a .csv file"

    folder = normalize(img_file.filename.split(".")[0])


    if img_file.filename.lower().endswith('.zip'):
        zip_path = os.path.join(UPLOAD_FOLDER, 'uploaded.zip')
        img_file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Skip directories
                if member.is_dir():
                    continue
                
                # Get only the filename (remove folder paths inside ZIP)
                filename = os.path.basename(member.filename)
                if not filename:
                    continue  # skip empty names
                
                # Target file path (flattened)
                target_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Extract the file
                with zip_ref.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())
        # Collect image details
        image_data = []
        for filename in os.listdir((UPLOAD_FOLDER)):
            print("--- filename ---", filename)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                path = os.path.join(UPLOAD_FOLDER, filename)
                size_kb = round(os.path.getsize(path) / 1024, 2)
                print("---- info ---", [filename, size_kb, ""])
                image_data.append([filename, size_kb, ""])  # last column for user notes

        # Write to CSV
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Size (KB)', 'Notes'])
            writer.writerows(image_data)

    return redirect(url_for('show_images'))


@app.route('/images')
def show_images():
    # Read from CSV
    images = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            images = list(reader)
    return render_template('images.html', images=images)


@app.route('/update', methods=['POST'])
def update_csv():
    data = request.form
    rows = []
    # Read existing CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'] == data['name']:
                row['Notes'] = data['notes']
            rows.append(row)

    # Rewrite CSV
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Size (KB)', 'Notes'])
        writer.writeheader()
        writer.writerows(rows)

    return redirect(url_for('show_images'))


@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)




if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)