import os

OUTPUT_DIR = os.path.join('storage', 'processed_images')
MASK_DIR = os.path.join('storage', 'masks')
UPLOAD_FOLDER = os.path.join('storage', 'raw_image')
DATA_FOLDER = os.path.join('storage', 'meta_data')
CSV_PATH = os.path.join(DATA_FOLDER, 'upload_details.csv')
OUTPUT_CSV = os.path.join(DATA_FOLDER, "result_metadata.csv")
