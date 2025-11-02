import os
import csv
import pandas as pd
from utility import normalize, file_extracter
from image_processor.handler import ImageProcess
from config import UPLOAD_FOLDER, DATA_FOLDER, CSV_PATH, OUTPUT_DIR
from flask import (
                        Flask, render_template, request,
                        redirect, url_for, send_from_directory,
                        flash)


app = Flask(__name__)
# Auto-reload templates without restarting the server
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "erwt67q8w8s"


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    msg = ""

    # checking all arguments existing
    if 'zipfile' not in request.files:
        msg = "No image file"

    if 'csv' not in request.files:
        msg = "No csv file"

    img_file = request.files['zipfile']
    csv_file = request.files['csv']

    # validating request values

    if not img_file.filename.lower().endswith('.zip'):
        msg = "Please upload a .zip file"

    if not csv_file.filename.lower().endswith('.csv'):
        msg = "Please upload a .csv file"

    if msg:
        flash(msg, 'error')
        return redirect(url_for('home'))
    if img_file.filename.lower().endswith('.zip'):
        # A temporary zipfile
        zip_path = os.path.join(UPLOAD_FOLDER, 'uploaded.zip')
        img_file.save(zip_path)

        # unzip and storing file information
        file_extracter(
                            zip_path,
                            UPLOAD_FOLDER,
                            csv_file.filename.lower(),
                            CSV_PATH)

        # removing tempfile
        os.remove(zip_path)

    if csv_file.filename.lower().endswith('.csv'):
        filepath = os.path.join(DATA_FOLDER,  csv_file.filename.lower())
        csv_file.save(filepath)

        try:
            # Read CSV
            df = pd.read_csv(filepath)

            # Normalize column names
            df.columns = df.columns.map(normalize)

            required_columns = {
                                    "filename",
                                    "brightness",
                                    "contrast",
                                    "sharpness"
                                }

            missing = required_columns - set(df.columns)
            # Check for required columns
            if missing:
                flash(f"Missing required columns {list(missing)}", 'error')
                return redirect(url_for('home'))

            missing_files = []
            for _, row in df.iterrows():
                filename = row["filename"]
                img_path = os.path.join(UPLOAD_FOLDER, filename)

                # checking image existing or not
                if not os.path.exists(img_path):
                    missing_files.append(filename)

            if missing_files:
                flash(f"Missing these images from folder : {', '.join(missing_files)}", 'error')
                return redirect(url_for('home'))

            # Save CSV
            df.to_csv(filepath, index=False)

        except Exception as e:
            flash(f"error {str(e)}", 'error')
            return redirect(url_for('home'))

        ip_obj = ImageProcess(filepath, UPLOAD_FOLDER, CSV_PATH)
        ip_obj.process_images()

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


@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/process/<filename>')
def serve_processed_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
