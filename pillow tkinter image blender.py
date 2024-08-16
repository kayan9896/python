
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def select_image(image_var, image_label):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if file_path:
        image_var.set(file_path)
        image = Image.open(file_path)
        image.thumbnail((32, 32))  # Set thumbnail size to 32x32

        # Convert the image to RGB mode if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Create a PhotoImage object from the PIL image
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo

def blend_images():
    image1_path = image1_var.get()
    image2_path = image2_var.get()
    if image1_path and image2_path:
        try:
            image1 = Image.open(image1_path)
            image2 = Image.open(image2_path)

            # Convert images to RGB mode if necessary
            if image1.mode != "RGB":
                image1 = image1.convert("RGB")
            if image2.mode != "RGB":
                image2 = image2.convert("RGB")

            # Resize images to match the size of the first image
            if image1.size != image2.size:
                image2 = image2.resize(image1.size)

            blended_image = Image.blend(image1, image2, alpha=0.5)
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if save_path:
                blended_image.save(save_path)
                messagebox.showinfo("Success", "Blended image saved successfully.")

                # Display the blended image in the preview label
                blended_image.thumbnail((32, 32))  # Set thumbnail size to 32x32
                photo = ImageTk.PhotoImage(blended_image)
                blended_label.config(image=photo)
                blended_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "Please select both images before processing.")

# Create the main window
window = tk.Tk()
window.title("Image Blender")
window.geometry("600x500")  # Adjusted window size
window.resizable(False, False)  # Disable window resizing

# Create variables to store the selected image paths
image1_var = tk.StringVar()
image2_var = tk.StringVar()

# Create a frame for the image selection section
select_frame = tk.Frame(window)
select_frame.pack(pady=20)

# Create labels and buttons for selecting images
tk.Label(select_frame, text="Image 1:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
image1_label = tk.Label(select_frame, width=4, height=2, relief=tk.SUNKEN, bd=2)  # Adjusted label size
image1_label.grid(row=1, column=0, padx=10, pady=10)
tk.Button(select_frame, text="Select", command=lambda: select_image(image1_var, image1_label)).grid(row=2, column=0, padx=10, pady=10)

tk.Label(select_frame, text="Image 2:").grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
image2_label = tk.Label(select_frame, width=4, height=2, relief=tk.SUNKEN, bd=2)  # Adjusted label size
image2_label.grid(row=1, column=1, padx=10, pady=10)
tk.Button(select_frame, text="Select", command=lambda: select_image(image2_var, image2_label)).grid(row=2, column=1, padx=10, pady=10)

# Create a label to display the blended image preview
blended_label = tk.Label(window, width=8, height=2, relief=tk.SUNKEN, bd=2)  # Adjusted label size
blended_label.pack(pady=20)

# Create a button to process the images
tk.Button(window, text="Process", command=blend_images).pack(pady=10)

# Start the main event loop
window.mainloop()
