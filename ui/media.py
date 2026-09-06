import tkinter as tk
from PIL import Image, ImageTk

class MediaRenderer:
    def __init__(self, root, label):
        self.root = root
        self.label = label
        self.current_image = None
        self.frames = []
        self.current_frame = 0
        self.animating = False
        self.animation_id = None
        self.delay = 100

    def show_media(self, file_path):
        self.stop_animation()
        try:
            img = Image.open(file_path)
            if getattr(img, "is_animated", False):
                self._load_gif_frames(img)
                self.animating = True
                self._animate()
            else:
                self._show_static_image(img)
        except Exception as e:
            print(f"Error loading media {file_path}: {e}")
            self.label.config(image='', text="Media Error")
            self.current_image = None

    def _show_static_image(self, img):
        max_w = self.root.winfo_screenwidth() - 200
        max_h = self.root.winfo_screenheight() - 200
        if max_w <= 0: max_w = 800
        if max_h <= 0: max_h = 600
        
        # Calculate aspect ratio to fit the screen
        ratio = min(max_w / img.width, max_h / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img)
        self.current_image = photo
        self.label.config(image=photo, text='')

    def _load_gif_frames(self, img):
        self.frames = []
        try:
            self.delay = img.info.get('duration', 100) or 100
            
            max_w = self.root.winfo_screenwidth() - 200
            max_h = self.root.winfo_screenheight() - 200
            if max_w <= 0: max_w = 800
            if max_h <= 0: max_h = 600
            
            # Calculate aspect ratio once based on first frame
            ratio = min(max_w / img.width, max_h / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            for frame_idx in range(img.n_frames):
                img.seek(frame_idx)
                frame_rgba = img.convert("RGBA")
                frame_rgba = frame_rgba.resize(new_size, Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame_rgba))
        except EOFError:
            pass
        self.current_frame = 0

    def _animate(self):
        if not self.animating or not self.frames:
            return
        
        photo = self.frames[self.current_frame]
        self.current_image = photo
        self.label.config(image=photo, text='')
        
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.animation_id = self.root.after(self.delay, self._animate)

    def stop_animation(self):
        self.animating = False
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.current_image = None
        self.frames = []
        self.label.config(image='')
