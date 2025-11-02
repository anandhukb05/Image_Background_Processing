# Image_Background_Processing

Requirements
-   Detecting the product area.
    
-   Generating a white background.
    
-   Applying brightness/contrast/sharpness adjustments.
    
-   Maintaining a 60% fill ratio (product should occupy ~60% of the 1:1 frame).
    
-   Producing and saving the corresponding product mask.
    
-   Handling CSV input/output for metadata before and after processing.

  ### Detailed Requirements

1.  Input:
    
    -   Folder containing raw product images (Will attach the raw images in this mail).
        
    -   A CSV file (e.g., `input_metadata.csv`) containing:
        
        -   Image filename
            
        -   Brightness
            
        -   Contrast
            
        -   Sharpness
            
        -   Any other preprocessing parameters you need
            
2.  Processing Steps:
    
    -   Detect the product region (use segmentation/mask generation — you may use libraries like OpenCV, Pillow, NumPy, or PyTorch/TensorFlow if preferred).
        
    -   Create a clean white background (RGB: 255,255,255).
        
    -   Ensure the product fills approximately 60% of the total frame area (1:1 aspect ratio).
        
    -   Crop and resize the image to a 1:1 ratio centered on the product.
        
    -   Generate and save the binary mask (product = 1, background = 0).
        
3.  Output:
    
    -   Folder containing:
        
        -   Processed 1:1 images with white background.
            
        -   Corresponding mask images.
            
    -   A CSV file containing:
        
        -   Image filename
            
        -   Adjusted brightness, contrast, and sharpness
            
        -   Fill ratio achieved
            
        -   Mask path
            
4.  File Naming Convention:
    
    -   Use the original filename with a suffix, e.g.:
        
        -   `original_name_processed.jpg`
            
        -   `original_name_mask.png`
            


# setup instructions

python -m venv venv_name

#activate venv then install dependencies

pip install -r requirements.txt


then run main.py

the flask server is started
     

<img width="1870" height="906" alt="image" src="https://github.com/user-attachments/assets/a4eb98ea-00b0-47d6-afec-e8e3540e65cb" />



upload the images zip folder and input meta data.

input metadata sample

<img width="529" height="397" alt="image" src="https://github.com/user-attachments/assets/7ffd0800-b649-49cd-b27c-bfe1c5bd5d47" />

# csv coloumns

1. Filename
   It is the filename of image
   
2. Brightness
   
    Meaning: How light or dark the overall image is.
    In mathematical terms, it shifts pixel intensities up or down.

    Example
        If a pixel value is 100 (on a 0–255 scale):
        Brightness = 1.0 → no change (100)
        Brightness = 1.2 → 20% brighter (≈120)
        Brightness = 0.8 → 20% darker (≈80)

4. Contrast
   
      Meaning: How much difference there is between dark and light areas.
      Increasing contrast makes shadows darker and highlights brighter.
      Decreasing contrast makes the image look “flat” or “washed out”.
    
    Example
      If average intensity is 128:
      High contrast (1.5) → dark pixels (50 → 30), light pixels (200 → 230)
      Low contrast (0.5) → dark pixels (50 → 90), light pixels (200 → 160)

5. Sharpness

    Meaning: How strong the edges and fine details appear.
    Increasing sharpness increases local contrast around edges — it makes objects and textures look crisper.
    Decreasing sharpness makes them blurrier or softer.

    Example
      If you increase sharpness:
      The difference between adjacent pixels becomes larger — edges look more defined.
      If you decrease sharpness:
      Edges get smoothed out.
    
    In Pillow (ImageEnhance.Sharpness):
            1.0 = original sharpness
            < 1.0 = more blurred
            > 1.0 = sharper edges
            0.0 = completely blurred image

then click on process button.


after processing we can see that the result


<img width="1840" height="831" alt="image" src="https://github.com/user-attachments/assets/071a32e8-1dd3-48f5-9fab-adb3302ac8ad" />


inside the storage folder we can see the results files


<img width="819" height="525" alt="image" src="https://github.com/user-attachments/assets/fd036688-563b-42c3-8237-6fc5b83a263f" />



<img width="691" height="305" alt="image" src="https://github.com/user-attachments/assets/e02f3bfc-37db-44a7-9b08-ec7e29844c85" />



# Storage folder
masks folder contain mask images

meta_data folder contains the csv files.

result_csv file containing Image filename, Adjusted brightness, contrast, and sharpness, Fill ratio achieved and Mask path

processed_images folder that contains the images processed. filename like original_name_processed.jpg

raw_image folder contains original images
