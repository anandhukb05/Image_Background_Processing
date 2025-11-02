import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance
from rembg import remove
from config import MASK_DIR, OUTPUT_DIR, OUTPUT_CSV


class ImageProcess():

    def __init__(self, image_meta_path, image_folder_path, meta_file_path):
        self.image_meta_path = image_meta_path
        self.image_folder_path = image_folder_path
        # file_meta path of transaction metafile of upload (this file for internal purpose)
        self.file_meta = meta_file_path

    def process_images(self):

        image_meta_df = pd.read_csv(self.image_meta_path)
        meta_df = pd.read_csv(self.file_meta)

        results_list = []

        for _, row in image_meta_df.iterrows():
            filename = row["filename"]
            brightness = row.get("brightness", 1.0)
            contrast = row.get("contrast", 1.0)
            sharpness = row.get("sharpness", 1.0)

            img_path = os.path.join(self.image_folder_path, self.filename)

            # checking image existing or not
            if not os.path.exists(img_path):
                meta_df.loc[self.meta_df['filename'] == self.filename, ['status']] = ["file is missing"]
                meta_df.to_csv("data.csv", index=False)
                continue

            img = cv2.imread(img_path)
            if img is None:
                meta_df.loc[meta_df['filename'] == filename, ['status']] = ["Unable to read"]
                meta_df.to_csv("data.csv", index=False)
                continue

            # Removing background
            result_img, mask_img = self.remove_background(self.img)

            # Center and resizing the image
            processed_img, mask_img = self.center_and_resize_with_fill_ratio(result_img, mask_img)
            if processed_img is None:
                meta_df.loc[meta_df['filename'] == filename, ['status']] = ["Object not detected"]
                meta_df.to_csv("data.csv", index=False)
                continue

            # Enhancing the image with input metadata
            processed_pil = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
            processed_pil = self.apply_adjustments(processed_pil, brightness, contrast, sharpness)
            processed_img = cv2.cvtColor(np.array(processed_pil), cv2.COLOR_RGB2BGR)

            # --- Saving results

            os.makedirs(OUTPUT_DIR, exist_ok=True)
            os.makedirs(MASK_DIR, exist_ok=True)
            base_name = os.path.splitext(filename)[0]
            processed_path = os.path.join(OUTPUT_DIR, f"{base_name}_processed.jpg")
            mask_path = os.path.join(MASK_DIR, f"{base_name}_mask.png")

            cv2.imwrite(processed_path, processed_img)
            cv2.imwrite(mask_path, mask_img)

            # saving changes details of image
            fill_ratio_achieved = np.sum(mask_img > 0) / (mask_img.shape[0] * mask_img.shape[1])
            results_list.append({
                "Image filename": filename,
                "Brightness": brightness,
                "Contrast": contrast,
                "Sharpness": sharpness,
                "Fill ratio achieved": round(fill_ratio_achieved, 3),
                "Mask path": mask_path
            })

            meta_df.loc[meta_df['filename'] == filename, ['status']] = ["Processed"]
            meta_df.to_csv("data.csv", index=False)

            pd.DataFrame(results_list).to_csv(OUTPUT_CSV, index=False)
            print("\n🎯 Processing complete! Results saved to", OUTPUT_CSV)

    def remove_background(self, input_image):
        """
        Remove background using rembg and replace with white background.
        Works for both file paths and cv2 images.
        Returns: (result_image_BGR, mask_image)
        """
        # Convert OpenCV image (BGR) to RGB bytes for rembg
        if isinstance(input_image, np.ndarray):
            rgb_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
            input_pil = Image.fromarray(rgb_image)
        else:
            input_pil = Image.open(input_image)

        # Run background removal
        output_pil = remove(input_pil)

        # Convert to RGBA
        output_pil = output_pil.convert("RGBA")
        np_img = np.array(output_pil)

        # Separate alpha mask
        alpha = np_img[:, :, 3] / 255.0

        # Create white background
        white_bg = np.ones_like(np_img[:, :, :3], dtype=np.uint8) * 255
        white_bg = (white_bg * (1 - alpha[..., None]) + np_img[:, :, :3] * alpha[..., None]).astype(np.uint8)

        # Mask image (binary)
        mask_img = (alpha > 0.1).astype(np.uint8) * 255

        # Convert to BGR for OpenCV compatibility
        result_bgr = cv2.cvtColor(white_bg, cv2.COLOR_RGB2BGR)

        return result_bgr, mask_img

    def center_and_resize_with_fill_ratio(self, img, mask, fill_ratio=0.6, final_size=1024):
        """Center object in white 1:1 square ensuring ~60% fill ratio."""

        y_indices, x_indices = np.where(mask > 0)
        if len(x_indices) == 0 or len(y_indices) == 0:
            return None, None

        x1, x2 = x_indices.min(), x_indices.max()
        y1, y2 = y_indices.min(), y_indices.max()
        product = img[y1:y2, x1:x2]
        product_mask = mask[y1:y2, x1:x2]

        obj_h, obj_w = product.shape[:2]
        obj_area = obj_h * obj_w
        desired_area = fill_ratio * (final_size ** 2)
        scale = np.sqrt(desired_area / obj_area)
        new_w, new_h = int(obj_w * scale), int(obj_h * scale)

        product_resized = cv2.resize(product, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        mask_resized = cv2.resize(product_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

        background = np.ones((final_size, final_size, 3), dtype=np.uint8) * 255
        mask_bg = np.zeros((final_size, final_size), dtype=np.uint8)

        x_offset = max((final_size - new_w) // 2, 0)
        y_offset = max((final_size - new_h) // 2, 0)
        y_end = min(y_offset + new_h, final_size)
        x_end = min(x_offset + new_w, final_size)
        crop_h = y_end - y_offset
        crop_w = x_end - x_offset

        background[y_offset:y_end, x_offset:x_end] = product_resized[:crop_h, :crop_w]
        mask_bg[y_offset:y_end, x_offset:x_end] = mask_resized[:crop_h, :crop_w]

        return background, mask_bg

    def apply_adjustments(self, img_pil, brightness, contrast, sharpness):
        """Apply brightness, contrast, and sharpness adjustments."""
        img_pil = ImageEnhance.Brightness(img_pil).enhance(brightness)
        img_pil = ImageEnhance.Contrast(img_pil).enhance(contrast)
        img_pil = ImageEnhance.Sharpness(img_pil).enhance(sharpness)
        return img_pil
