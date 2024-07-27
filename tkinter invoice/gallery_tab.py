import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3
from PIL import Image, ImageTk

class GalleryTab(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.setup_ui()

    def setup_ui(self):
        ttk.Button(self, text="Add Photo", command=self.add_photo).pack(pady=10)
        self.gallery_frame = ttk.Frame(self)
        self.gallery_frame.pack(fill=tk.BOTH, expand=True)
        self.load_gallery()

    def add_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            description = simpledialog.askstring("Photo Description", "Enter a description for the photo:")
            try:
                self.cursor.execute("INSERT INTO gallery (image_path, description) VALUES (?, ?)", (file_path, description))
                self.conn.commit()
                self.load_gallery()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while adding the photo: {e}")

    def load_gallery(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()

        try:
            self.cursor.execute("SELECT * FROM gallery")
            for i, row in enumerate(self.cursor.fetchall()):
                image_path = row[1]
                description = row[2]
                img = Image.open(image_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(self.gallery_frame, image=photo, text=description, compound=tk.BOTTOM)
                label.image = photo
                label.grid(row=i//4, column=i%4, padx=5, pady=5)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading the gallery: {e}")
        except IOError:
            messagebox.showerror("File Error", f"Unable to open image file: {image_path}")

