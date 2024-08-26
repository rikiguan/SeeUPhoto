import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ExifTags

class ImageBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser")
        self.current_index = 0
        self.image_list = []

        # Set a fixed size for the window
        self.root.geometry('1600x800')
        self.root.resizable(False, False)  # Prevent window from being resized

        # Create frames for layout
        self.image_frame = tk.Frame(root, width=1200, height=720)
        self.image_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y, expand=True)
        
        self.info_frame = tk.Frame(root, width=400, height=720)
        self.info_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.info_label = tk.Label(self.info_frame, text='', wraplength=400, justify=tk.LEFT)
        self.info_label.pack()

        self.load_images()
        self.display_image()

        # Key bindings
        self.root.bind('<Left>', self.prev_image)
        self.root.bind('<Right>', self.next_image)
        for i in range(1, 10):
            self.root.bind(str(i), self.move_image)

    def load_images(self):
        """Load all image files in the current directory."""
        self.image_list = [f for f in os.listdir() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not self.image_list:
            print("No images found in the current directory.")
            self.root.quit()

    def display_image(self):
        """Display the current image and its EXIF data."""
        if self.image_list:
            img_path = self.image_list[self.current_index]
            img = Image.open(img_path)
            img.thumbnail((1200, 720))  # Resize to fit the fixed window size
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
            self.root.title(f"Image Browser - {img_path} ({self.current_index + 1}/{len(self.image_list)})")
            
            # Display EXIF data
            exif_data = self.get_exif_data(img)
            exif_text = ''
            for key, value in exif_data.items():
                if 'Date' in key:  # Highlight the date/time information
                    exif_text += f"\n{key}: {value}"
                    self.info_label.config(font=('Arial', 14, 'bold'))  # Increase font size for date/time
                else:
                    exif_text += f"\n{key}: {value}"
            self.info_label.config(text=exif_text)

    def get_exif_data(self, img):
        """Extract EXIF data from the image."""
        exif_data = {}
        if hasattr(img, '_getexif'):
            exif_raw = img._getexif()
            if exif_raw:
                for tag, value in exif_raw.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    exif_data[decoded] = value
        
        # Convert GPS data to a more readable format
        if 'GPSInfo' in exif_data:
            gps_info = exif_data['GPSInfo']
            gps_data = {}
            for key in gps_info.keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gps_data[decode] = gps_info[key]
            exif_data['GPSInfo'] = gps_data
        
        return exif_data

    def prev_image(self, event=None):
        """Display the previous image."""
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.display_image()

    def next_image(self, event=None):
        """Display the next image."""
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.display_image()

    def move_image(self, event):
        """Move the current image to the corresponding folder based on the key pressed."""
        folder_num = event.char
        target_folder = f"Folder_{folder_num}"
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        img_path = self.image_list[self.current_index]
        shutil.move(img_path, os.path.join(target_folder, img_path))
        del self.image_list[self.current_index]
        if self.image_list:
            self.current_index %= len(self.image_list)
            self.display_image()
        else:
            print("No more images to display.")
            self.image_label.config(image='')
            self.info_label.config(text='')
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()
