import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ExifTags

class ImageBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("图片浏览器")
        self.current_index = 0
        self.image_list = []
        self.image_cache = {}  # 缓存图像
        self.image_cache_small = {}  # 缓存图像
        self.exif_cache = {}   # 缓存 EXIF 数据

        # 设置窗口大小
        self.root.geometry('1600x900')
        self.root.resizable(False, False)  # 禁止窗口调整大小

        # 创建主框架
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 图像和 EXIF 信息的框架
        self.image_frame = tk.Frame(self.main_frame, width=1200, height=700)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_frame = tk.Frame(self.main_frame, width=400, height=700)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # EXIF 信息的 Canvas 和滚动条
        self.info_canvas = tk.Canvas(self.info_frame)
        self.info_scrollbar = tk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_canvas.yview)
        self.info_frame_content = tk.Frame(self.info_canvas)

        self.info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_canvas.create_window((0, 0), window=self.info_frame_content, anchor='nw')
        self.info_canvas.config(yscrollcommand=self.info_scrollbar.set)

        # EXIF 信息标签
        self.info_label = tk.Label(self.info_frame_content, text='', justify=tk.LEFT, anchor='nw', wraplength=400)
        self.info_label.pack(fill=tk.BOTH, expand=True)

        # 缩略图框架和滚动条
        self.thumbnail_frame = tk.Frame(root, height=150)
        self.thumbnail_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.thumbnail_canvas = tk.Canvas(self.thumbnail_frame)
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.thumbnail_scrollbar = tk.Scrollbar(self.thumbnail_frame, orient=tk.HORIZONTAL, command=self.thumbnail_canvas.xview)
        self.thumbnail_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.thumbnail_canvas.config(xscrollcommand=self.thumbnail_scrollbar.set)

        self.thumbnail_frame_content = tk.Frame(self.thumbnail_canvas)
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_frame_content, anchor='nw')

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 加载图像和 EXIF 数据
        self.load_images()
        self.preload_images()

        # 键盘绑定
        self.root.bind('<Left>', self.prev_image)
        self.root.bind('<Right>', self.next_image)
        for i in range(0, 10):
            self.root.bind(str(i), self.move_image)

    def load_images(self):
        """加载当前目录中的所有图像文件。"""
        self.image_list = [f for f in os.listdir() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not self.image_list:
            print("当前目录中没有找到图像文件。")
            self.root.quit()

    def preload_images(self):
        """预加载图像到缓存中。"""
        def load_images_in_background():
            for img_path in self.image_list:
                img = Image.open(img_path)
                img.thumbnail((1200, 700))
                self.image_cache[img_path] = ImageTk.PhotoImage(img)
                img.thumbnail((100, 100))
                self.image_cache_small[img_path] = ImageTk.PhotoImage(img)
                exif_data = self.get_exif_data(img)
                self.exif_cache[img_path] = exif_data
            self.display_image()

        # 启动后台线程
        threading.Thread(target=load_images_in_background, daemon=True).start()


    def display_image(self):
        """显示当前图像及其 EXIF 数据。"""
        if self.image_list:
            img_path = self.image_list[self.current_index]
            img_tk = self.image_cache.get(img_path)
            if img_tk:
                self.image_label.config(image=img_tk)
                self.image_label.image = img_tk
                self.root.title(f"图片浏览器 - {img_path} ({self.current_index + 1}/{len(self.image_list)})")

                # 显示 EXIF 数据
                exif_data = self.exif_cache.get(img_path, {})
                exif_text = ''
                for key, value in exif_data.items():
                    if 'Date' in key:  # 高亮显示日期/时间信息
                        exif_text += f"\n{key}: {value}"
                    else:
                        exif_text += f"\n{key}: {value}"
                
                self.info_label.config(text=exif_text)

                # 更新缩略图
                self.update_thumbnails()

                # 更新 Canvas 滚动区域
                self.info_frame_content.update_idletasks()
                self.info_canvas.config(scrollregion=self.info_canvas.bbox("all"))

    def get_exif_data(self, img):
        """从图像中提取 EXIF 数据。"""
        exif_data = {}
        if hasattr(img, '_getexif'):
            exif_raw = img._getexif()
            if exif_raw:
                for tag, value in exif_raw.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    exif_data[decoded] = value
        
        # 将 GPS 数据转换为更可读的格式
        if 'GPSInfo' in exif_data:
            gps_info = exif_data['GPSInfo']
            gps_data = {}
            for key in gps_info.keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gps_data[decode] = gps_info[key]
            exif_data['GPSInfo'] = gps_data
        
        return exif_data

    def prev_image(self, event=None):
        """显示上一张图像。"""
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.display_image()

    def next_image(self, event=None):
        """显示下一张图像。"""
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.display_image()

    def move_image(self, event):
        """根据按键将当前图像移动到对应的文件夹中。"""
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
            print("没有更多图像显示。")
            self.image_label.config(image='')
            self.info_label.config(text='')
            self.root.quit()

    def update_thumbnails(self):
        """更新底部的缩略图显示。"""
        # 清除现有缩略图
        for widget in self.thumbnail_frame_content.winfo_children():
            widget.destroy()
        
        # 创建新的缩略图
        for i in range(max(self.current_index - 1, 0), min(self.current_index + 14, len(self.image_list))):
            img_path = self.image_list[i]
            img_tk = self.image_cache_small.get(img_path)
            if img_tk:
                thumbnail_label = tk.Label(self.thumbnail_frame_content, image=img_tk, borderwidth=2, relief='solid')
                if i == self.current_index:
                    thumbnail_label.config(borderwidth=3, relief='solid', highlightbackground='red', highlightcolor='red', highlightthickness=3)
                thumbnail_label.image = img_tk
                thumbnail_label.grid(row=0, column=i - max(self.current_index - 7, 0), padx=5, pady=5)

        # 更新 Canvas 滚动区域
        self.thumbnail_frame_content.update_idletasks()
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()
