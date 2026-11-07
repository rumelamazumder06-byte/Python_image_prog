import tkinter as tk
from tkinter import filedialog, messagebox
def get_rgb(photo, x, y):
   
    pixel = photo.get(x, y)
    if isinstance(pixel, (tuple, list)):
        return tuple(int(channel) for channel in pixel[:3])
    if isinstance(pixel, str) and pixel.startswith("#"):
        value = pixel.lstrip("#")
        if len(value) == 3:
            value = "".join(channel * 2 for channel in value)
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
    return tuple(int(channel) for channel in str(pixel).split()[:3])


def make_photo(width, height, pixels):
    
    photo = tk.PhotoImage(width=width, height=height)
    for y, row in enumerate(pixels):
        colors = " ".join(
            "#{:02x}{:02x}{:02x}".format(red, green, blue)
            for red, green, blue in row
        )
        photo.put("{" + colors + "}", to=(0, y))
    return photo


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Image Viewer")
        self.root.geometry("900x650")

        self.image = None
        self.image_item = None

        toolbar = tk.Frame(root, padx=6, pady=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        actions = (
            ("Open", self.open_image),
            ("Grayscale", self.to_grayscale),
            ("Enhance grayscale", self.enhance_grayscale),
            ("Rotate 90°", self.rotate_90),
            ("Flip horizontal", self.flip_horizontal),
            ("Flip vertical", self.flip_vertical),
            ("Save as", self.save_image),
        )
        for label, command in actions:
            tk.Button(toolbar, text=label, command=command).pack(
                side=tk.LEFT, padx=2
            )

        viewer = tk.Frame(root)
        viewer.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(viewer, background="#333333")
        vertical = tk.Scrollbar(
            viewer, orient=tk.VERTICAL, command=self.canvas.yview
        )
        horizontal = tk.Scrollbar(
            viewer, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.canvas.configure(
            xscrollcommand=horizontal.set, yscrollcommand=vertical.set
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        viewer.rowconfigure(0, weight=1)
        viewer.columnconfigure(0, weight=1)

        self.status = tk.StringVar(value="Open an image to get started.")
        tk.Label(root, textvariable=self.status, anchor=tk.W, padx=6).pack(
            side=tk.BOTTOM, fill=tk.X
        )

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Open image",
            filetypes=[
                ("Tk-supported images", "*.png *.gif *.pgm *.ppm *.pbm"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            image = tk.PhotoImage(file=path)
        except tk.TclError as error:
            messagebox.showerror("Could not open image", str(error))
            return
        self.image = image
        self.display_image()
        self.status.set(
            "{} × {} pixels — {}".format(image.width(), image.height(), path)
        )

    def display_image(self):
        if self.image is None:
            return
        self.canvas.delete("all")
        self.image_item = self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.image
        )
        self.canvas.configure(
            scrollregion=(0, 0, self.image.width(), self.image.height())
        )

    def read_pixels(self):
        width, height = self.image.width(), self.image.height()
        return [
            [get_rgb(self.image, x, y) for x in range(width)]
            for y in range(height)
        ]

    def apply_pixels(self, pixels):
        height = len(pixels)
        width = len(pixels[0])
        self.image = make_photo(width, height, pixels)
        self.display_image()
        self.status.set("{} × {} pixels".format(width, height))

    def to_grayscale(self):
        if self.image is None:
            return
        pixels = self.read_pixels()
        gray_pixels = []
        for row in pixels:
            gray_row = []
            for red, green, blue in row:
                gray = (299 * red + 587 * green + 114 * blue) // 1000
                gray_row.append((gray, gray, gray))
            gray_pixels.append(gray_row)
        self.apply_pixels(gray_pixels)

    def enhance_grayscale(self):
        if self.image is None:
            return
        pixels = self.read_pixels()
        grayscale = [
            [(299 * red + 587 * green + 114 * blue) // 1000
             for red, green, blue in row]
            for row in pixels
        ]
        low = min(min(row) for row in grayscale)
        high = max(max(row) for row in grayscale)
        if low == high:
            messagebox.showinfo(
                "Enhance grayscale",
                "This image has no intensity range to stretch.",
            )
            return
        scale = 255 / (high - low)
        enhanced = [
            [
                (value, value, value)
                for value in (max(0, min(255, round((pixel - low) * scale)))
                              for pixel in row)
            ]
            for row in grayscale
        ]
        self.apply_pixels(enhanced)

    def rotate_90(self):
        if self.image is None:
            return
        pixels = self.read_pixels()
        height, width = len(pixels), len(pixels[0])
        rotated = [
            [pixels[height - 1 - x][y] for x in range(height)]
            for y in range(width)
        ]
        self.apply_pixels(rotated)

    def flip_horizontal(self):
        if self.image is None:
            return
        self.apply_pixels([list(reversed(row)) for row in self.read_pixels()])

    def flip_vertical(self):
        if self.image is None:
            return
        self.apply_pixels(list(reversed(self.read_pixels())))

    def save_image(self):
        if self.image is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("GIF image", "*.gif"),
                ("PPM image", "*.ppm"),
            ],
        )
        if not path:
            return
        image_format = path.rsplit(".", 1)[-1].lower()
        try:
            self.image.write(path, format=image_format)
        except tk.TclError as error:
            messagebox.showerror("Could not save image", str(error))
            return
        self.status.set("Saved {}".format(path))


if __name__ == "__main__":
    root = tk.Tk()
    ImageViewer(root)
    root.mainloop()
