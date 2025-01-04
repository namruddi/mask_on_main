import os
from tkinter import Tk, filedialog, Button, Label
from PIL import Image

def apply_mask_and_cutout(image_main, image_mask):
    """
    Apply a mask to the main image to cut out areas based on the mask.
    White areas in the mask remain visible, and black areas become transparent.
    """
    # Ensure both images are in RGBA modea
    image_main = image_main.convert("RGBA")
    image_mask = image_mask.convert("L")  # Convert mask to grayscale (L mode)

    # Use the mask as the alpha channel
    image_main.putalpha(image_mask)

    return image_main

def extract_base_name(filename, marker):
    """Extract the base name of the file by removing the marker ('main' or 'mask') and file extension."""
    base_name = filename.replace(f"_{marker}.png", "")  # Adjust for file extension and marker
    return base_name

def process_images(input_dir, output_dir):
    """Find pairs of images and apply mask to cut out areas."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(input_dir)
    main_files = [f for f in files if f.endswith("_main.png")]
    mask_files = [f for f in files if f.endswith("_mask.png")]

    if not main_files or not mask_files:
        print(f"No 'main' or 'mask' files found in {input_dir}.")
        return

    for main_file in main_files:
        base_name = extract_base_name(main_file, "main")
        corresponding_mask = next(
            (m for m in mask_files if extract_base_name(m, "mask") == base_name), None
        )

        if corresponding_mask:
            main_path = os.path.join(input_dir, main_file)
            mask_path = os.path.join(input_dir, corresponding_mask)
            output_path = os.path.join(output_dir, f"{base_name}_cutout.png")

            print(f"Processing pair: {main_file} + {corresponding_mask}")
            try:
                # Open images
                main_image = Image.open(main_path)
                mask_image = Image.open(mask_path)

                # Apply mask and cut out
                cutout_image = apply_mask_and_cutout(main_image, mask_image)

                # Save result
                cutout_image.save(output_path, "PNG")
                print(f"Saved: {output_path}")
            except Exception as e:
                print(f"Error processing {main_file} and {corresponding_mask}: {e}")
        else:
            print(f"No matching mask found for {main_file}")

def select_input_folder():
    """Prompt user to select the input folder."""
    folder_selected = filedialog.askdirectory(title="Select Input Folder")
    if folder_selected:
        input_label.config(text=f"Input Folder: {folder_selected}")
        global input_folder
        input_folder = folder_selected

def select_output_folder():
    """Prompt user to select the output folder."""
    folder_selected = filedialog.askdirectory(title="Select Output Folder")
    if folder_selected:
        output_label.config(text=f"Output Folder: {folder_selected}")
        global output_folder
        output_folder = folder_selected

def start_processing():
    """Start processing the images."""
    if not input_folder or not output_folder:
        print("Please select both input and output folders.")
        return
    print(f"Processing images from {input_folder} to {output_folder}...")
    process_images(input_folder, output_folder)
    print("Processing complete.")

import os
import cv2
from PIL import Image

def split_objects_by_mask(image_path, mask_path, output_dir):
    """
    Разделяет объекты из основного изображения по маске и сохраняет их отдельно.
    """
    # Убедитесь, что выходная папка существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Загрузите основное изображение и маску
    image_main = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Загружается с каналом RGBA
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)  # Загружается в оттенках серого

    # Найти контуры объектов на маске
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Найдено {len(contours)} объектов.")
    for idx, contour in enumerate(contours):
        # Определить ограничивающую рамку контура
        x, y, w, h = cv2.boundingRect(contour)

        # Вырезать объект из основного изображения и маски
        cropped_main = image_main[y:y+h, x:x+w]
        cropped_mask = mask[y:y+h, x:x+w]

        # Преобразовать обрезанный объект в RGBA с прозрачностью
        cropped_pil = Image.fromarray(cropped_main).convert("RGBA")
        mask_pil = Image.fromarray(cropped_mask).convert("L")
        cropped_pil.putalpha(mask_pil)

        # Сохранить обрезанный объект
        output_path = os.path.join(output_dir, f"object_{idx + 1}.png")
        cropped_pil.save(output_path, "PNG")
        print(f"Сохранено: {output_path}")

# Пример использования
image_path = "path/to/your/image_main.png"  # Основное изображение
mask_path = "path/to/your/image_mask.png"  # Маска
output_dir = "path/to/output/directory"    # Папка для сохранения объектов

split_objects_by_mask(image_path, mask_path, output_dir)



# Create the GUI
root = Tk()
root.title("Photo Mask Application")

input_folder = ""
output_folder = ""

input_label = Label(root, text="Input Folder: Not Selected", width=50, anchor="w")
input_label.pack(pady=5)
select_input_button = Button(root, text="Select Input Folder", command=select_input_folder)
select_input_button.pack(pady=5)

output_label = Label(root, text="Output Folder: Not Selected", width=50, anchor="w")
output_label.pack(pady=5)
select_output_button = Button(root, text="Select Output Folder", command=select_output_folder)
select_output_button.pack(pady=5)

process_button = Button(root, text="Start Processing", command=start_processing)
process_button.pack(pady=20)

root.mainloop()
