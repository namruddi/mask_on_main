import os
from tkinter import Tk, filedialog, Button, Label, messagebox, ttk
from PIL import Image, ImageChops, ImageOps

def apply_mask_and_cutout(image_main, image_mask):
    """
    Apply a mask to the main image to cut out areas based on the mask.
    White areas in the mask remain visible, and black areas become transparent.
    """
    image_main = image_main.convert("RGBA")
    image_mask = image_mask.convert("L")  # Convert mask to grayscale (L mode)
    image_main.putalpha(image_mask)
    return image_main

def apply_darken_layer(image_main, image_mask):
    """
    Apply darken blending to combine mask onto the main image with no transparency.
    """
    return ImageChops.darker(image_main, image_mask)

def extract_base_name(filename, marker):
    """Extract the base name of the file by removing the marker ('main' or 'mask') and file extension."""
    base_name = filename.replace(f"_{marker}.png", "")
    return base_name

def process_images(input_dir, output_dir, mode):
    """Find pairs of images and process them based on the selected mode."""
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
            output_path = os.path.join(output_dir, f"{base_name}_{mode}.png")

            print(f"Processing pair: {main_file} + {corresponding_mask} in mode: {mode}")
            try:
                main_image = Image.open(main_path).convert("RGBA")
                mask_image = Image.open(mask_path).convert("RGBA")
                mask_image = mask_image.resize(main_image.size)

                if mode == "cutout":
                    result_image = apply_mask_and_cutout(main_image, mask_image)
                elif mode == "darken":
                    result_image = apply_darken_layer(main_image, mask_image)

                result_image.save(output_path, "PNG")
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

def start_processing(mode):
    """Start processing images in the selected mode."""
    if not input_folder or not output_folder:
        print("Please select both input and output folders.")
        return

    # Show a warning message
    messagebox.showwarning("Processing Warning", "Пожалуйста не трогайте данное окно, пока не завершится процесс, иначе оно залагает.")

    print(f"Processing images in {mode} mode from {input_folder} to {output_folder}...")
    process_images(input_folder, output_folder, mode)
    print(f"{mode.capitalize()} processing complete.")

# Create the GUI
root = Tk()
root.title("Photo Mask Application")
root.geometry("500x350")
root.configure(bg="#2b2b2b")

input_folder = ""
output_folder = ""

# Styling
style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=5)
style.configure("TLabel", font=("Arial", 12), background="#2b2b2b", foreground="#ffffff")

# Widgets
input_label = Label(root, text="Input Folder: Not Selected", anchor="w", width=50, bg="#2b2b2b", fg="#ffffff")
input_label.pack(pady=5, padx=10)
select_input_button = ttk.Button(root, text="Select Input Folder", command=select_input_folder)
select_input_button.pack(pady=5)

output_label = Label(root, text="Output Folder: Not Selected", anchor="w", width=50, bg="#2b2b2b", fg="#ffffff")
output_label.pack(pady=5, padx=10)
select_output_button = ttk.Button(root, text="Select Output Folder", command=select_output_folder)
select_output_button.pack(pady=5)

cutout_button = ttk.Button(root, text="Process with PNG Cutout", command=lambda: start_processing("cutout"))
cutout_button.pack(pady=10)

darken_button = ttk.Button(root, text="Process with Black Screen", command=lambda: start_processing("darken"))
darken_button.pack(pady=10)

root.mainloop()
