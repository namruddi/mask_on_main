import os
from tkinter import Tk, filedialog, Button, Label
from PIL import Image, ImageChops

def apply_darken_layer(image_main, image_mask):
    """Apply darken blending to combine mask onto the main image."""
    return ImageChops.darker(image_main, image_mask)

def extract_base_name(filename, marker):
    """
    Extract the base name of the file by removing the marker ('main' or 'mask') and file extension.
    """
    base_name = filename.replace(f"_{marker}.png", "")  # Adjust for file extension and marker
    return base_name

def process_images(input_dir, output_dir):
    """Find pairs of images and apply mask to main with a darken effect."""
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
            output_path = os.path.join(output_dir, f"{base_name}_combined.png")

            print(f"Processing pair: {main_file} + {corresponding_mask}")
            try:
                # Open images
                main_image = Image.open(main_path).convert("RGBA")
                mask_image = Image.open(mask_path).convert("RGBA")

                # Resize mask to match main image
                mask_image = mask_image.resize(main_image.size)

                # Apply darken effect
                combined_image = apply_darken_layer(main_image, mask_image)

                # Save result
                combined_image.save(output_path)
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
