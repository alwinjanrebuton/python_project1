# frontend.py
# All the screens of the Iligan City Fire Station System.
# Part 1: the FIRE THEME (one place for all the colors) and the GLASS tools.
# Part 2: the ADMIN screens (Dashboard, Workers, Attendance, Duty, Leave, Reports, Incidents).
# Part 3: the WORKER screens (Login, Register, Menu, and the forms) - not built yet.
# This file only draws screens. All the saving and reading of data is done by backend.py.
# Pictures used: logo.png and background.png (in the same folder as this file).

import os                           # for folders (the reports folder)
import csv                          # lets us save a report as a file Excel can open
import tkinter as tk
import tkinter
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageTk
from datetime import datetime, timedelta    # for dates and times (timedelta is for "this week")
from functools import partial       # lets a button remember which row it belongs to
from tkinter import filedialog, messagebox
import backend                      # our backend.py file (all the data)

# =====================================================
# THE FIRE COLORS (change a color here and the whole system changes)
# =====================================================
WHITE = "#FFFFFF"            # pure white text
BG_DARK = "#1A0F0D"          # window background (smoky black-brown)
BG_PANEL = "#2A1512"         # boxes and cards (dark ember)
BG_PANEL_LIGHT = "#3A1B16"   # a slightly lighter box
BORDER = "#7F2A1D"           # thin lines around boxes

RED = "#C62828"              # main buttons
RED_DARK = "#8E1B1B"         # button when the mouse is over it
RED_DEEP = "#6E1414"         # deep red bars (headers)
ORANGE = "#E65100"           # second buttons and highlights
ORANGE_DARK = "#BF360C"      # orange when the mouse is over it
AMBER = "#FFB300"            # warm yellow (warnings, "Under Review")
EMBER_GRAY = "#5D4037"       # quiet buttons like BACK and CANCEL

TEXT = "#FFE9D6"             # main text (warm cream, not pure white)
TEXT_MUTED = "#FFFFFF"       # small notes (was "#C9A38F")

GREEN_BTN = "#2E7D32"        # green buttons (Approve, Reactivate)
GREEN_BTN_HOVER = "#1B5E20"  # green when the mouse is over it

# Colors for messages (they are easy to read on the dark background)
OK_GREEN = "#66BB6A"         # success
WARN_ORANGE = "#FFA726"      # "already done" and warnings
BAD_RED = "#FF5252"          # errors


class FireOptionMenu(ctk.CTkOptionMenu):
    """Fire themed selector using CustomTkinter's native dropdown behavior."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("fg_color", "#38201B")
        kwargs.setdefault("button_color", "#713323")
        kwargs.setdefault("button_hover_color", "#A94A2B")
        kwargs.setdefault("text_color", TEXT)
        kwargs.setdefault("dropdown_fg_color", "#241512")
        kwargs.setdefault("dropdown_hover_color", "#7F2A1D")
        kwargs.setdefault("dropdown_text_color", TEXT)
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("dynamic_resizing", False)
        super().__init__(*args, **kwargs)


# Keep selector styling and dropdown behavior consistent across the entire app.
ctk.CTkOptionMenu = FireOptionMenu


def set_colors(widget_name, **colors):
    """Changes the default colors of one kind of widget (like CTkButton).
    We write each color twice because CustomTkinter keeps one color for
    light mode and one for dark mode. We use the same color for both."""
    settings = ctk.ThemeManager.theme.get(widget_name)
    if settings is None:
        return                                  # that widget kind does not exist: skip it

    for key, value in colors.items():
        settings[key] = [value, value]


def apply_theme():
    """Turns the whole system into fire colors.
    Call this ONE time, before any window or widget is created."""
    ctk.set_appearance_mode("dark")

    set_colors("CTk", fg_color=BG_DARK)
    set_colors("CTkToplevel", fg_color=BG_DARK)

    set_colors("CTkFrame", fg_color=BG_PANEL, top_fg_color=BG_PANEL_LIGHT, border_color=BORDER)

    set_colors("CTkLabel", text_color=TEXT)

    set_colors("CTkButton", fg_color=RED, hover_color=RED_DARK, border_color=BORDER,
               text_color=TEXT, text_color_disabled=TEXT_MUTED)

    set_colors("CTkEntry", fg_color=BG_PANEL, border_color=BORDER, text_color=TEXT,
               placeholder_text_color=TEXT_MUTED)

    set_colors("CTkTextbox", fg_color=BG_PANEL, border_color=BORDER, text_color=TEXT,
               scrollbar_button_color=BORDER, scrollbar_button_hover_color=ORANGE)

    set_colors("CTkOptionMenu", fg_color=RED, button_color=RED_DARK,
               button_hover_color=RED_DEEP, text_color=TEXT, text_color_disabled=TEXT_MUTED)

    set_colors("CTkComboBox", fg_color=BG_PANEL, border_color=BORDER, button_color=RED,
               button_hover_color=RED_DARK, text_color=TEXT, text_color_disabled=TEXT_MUTED)

    # The list that opens when you click a dropdown
    set_colors("DropdownMenu", fg_color=BG_PANEL, hover_color=RED, text_color=TEXT)

    set_colors("CTkRadioButton", fg_color=ORANGE, border_color=BORDER, hover_color=ORANGE_DARK,
               text_color=TEXT, text_color_disabled=TEXT_MUTED)

    set_colors("CTkCheckBox", fg_color=ORANGE, border_color=BORDER, hover_color=ORANGE_DARK,
               checkmark_color=TEXT, text_color=TEXT, text_color_disabled=TEXT_MUTED)

    set_colors("CTkScrollbar", button_color=BORDER, button_hover_color=ORANGE)

    set_colors("CTkScrollableFrame", label_fg_color=BG_PANEL_LIGHT)


# =====================================================
# THE LOGO (uses logo.png - used by the Admin sidebar and the welcome screen)
# =====================================================
def load_logo():
    """Loads the Bureau of Fire Protection logo used as the main system logo."""
    path = os.path.join(backend.BASE_FOLDER, "fire_logo.png")
    if not os.path.exists(path):
        return None
    logo = Image.open(path).convert("RGBA")
    for corner in [(0, 0), (logo.width - 1, 0), (0, logo.height - 1), (logo.width - 1, logo.height - 1)]:
        ImageDraw.floodfill(logo, corner, (255, 255, 255, 0), thresh=60)
    return logo


def load_smc_logo():
    """Loads the St. Michael's College logo for school branding and credits."""
    path = os.path.join(backend.BASE_FOLDER, "smc_logo.png")
    if not os.path.exists(path):
        return None
    logo = Image.open(path).convert("RGBA")
    for corner in [(0, 0), (logo.width - 1, 0), (0, logo.height - 1), (logo.width - 1, logo.height - 1)]:
        ImageDraw.floodfill(logo, corner, (255, 255, 255, 0), thresh=60)
    return logo


# =====================================================
# GLASS TOOLS (the same idea as the welcome screen in main.py)
# =====================================================
GLASS_TINT = (25, 8, 8)           # dark smoky glass


def hex_to_rgb(color):
    """Turns a color like '#FFB300' into (255, 179, 0)."""
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def make_glass(background, box, radius, tint, alpha, outline=(255, 190, 120, 150)):
    """Makes a see-through 'glass' picture for the area `box` of the background."""
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    piece = background.crop(box).filter(ImageFilter.GaussianBlur(8)).convert("RGBA")
    piece = Image.alpha_composite(piece, Image.new("RGBA", (w, h), tuple(tint) + (alpha,)))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    piece.putalpha(mask)
    ImageDraw.Draw(piece).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius,
                                            outline=outline, width=2)
    return piece


# The blurred, darkened background.png is made ONCE and shared by every glass canvas
background_cache = {"original": None, "size": None, "full": None}


def get_background_piece(widget, screen):
    """Gives the part of background.png that sits behind this widget.
    The sidebar and the Dashboard get matching pieces, so they look like one picture."""
    if background_cache["original"] is None:
        path = os.path.join(backend.BASE_FOLDER, "background.png")
        if os.path.exists(path):
            image = Image.open(path).convert("RGB")
        else:
            image = Image.new("RGB", (1000, 650), (40, 12, 10))     # no file: plain dark
        image.thumbnail((1920, 1080))
        image = image.filter(ImageFilter.GaussianBlur(4))
        dark = Image.new("RGB", image.size, (20, 6, 6))
        background_cache["original"] = Image.blend(image, dark, 0.45)   # make it darker

    screen_size = (max(screen.winfo_width(), 100), max(screen.winfo_height(), 100))
    if background_cache["size"] != screen_size:
        background_cache["full"] = ImageOps.fit(background_cache["original"], screen_size)
        background_cache["size"] = screen_size

    x = widget.winfo_rootx() - screen.winfo_rootx()
    y = widget.winfo_rooty() - screen.winfo_rooty()
    return background_cache["full"].crop((x, y, x + widget.winfo_width(), y + widget.winfo_height()))


class CanvasText:
    """A small stand-in for a label. It has .configure(text=..., text_color=...) like a label,
    but it writes the text on a glass canvas."""

    def __init__(self, text=""):
        self.text = text
        self.color = None              # set by configure(text_color=...)
        self.canvas = None
        self.item = None

    def attach(self, canvas, x, y, **options):
        self.canvas = canvas
        if self.color is not None:
            options["fill"] = self.color
        self.item = canvas.create_text(x, y, text=self.text, **options)

    def configure(self, text=None, text_color=None, **ignored):
        if text is not None:
            self.text = text
        if text_color is not None:
            self.color = text_color
        if self.canvas is not None and self.item is not None:
            if text is not None:
                self.canvas.itemconfig(self.item, text=text)
            if text_color is not None:
                self.canvas.itemconfig(self.item, fill=text_color)


class GlassCanvas(tk.Canvas):
    """A canvas with the background picture, where we can draw glass panels and glass buttons.
    It redraws itself every time its size changes."""

    def __init__(self, parent, screen, draw, **options):
        super().__init__(parent, highlightthickness=0, bd=0, bg="#120A0A", **options)
        self.screen = screen
        self.draw = draw              # draw(canvas, width, height) is called to paint the content
        self.keep = []                # keeps the pictures alive
        self.count = 0
        self.piece = None
        self.last_size = (0, 0)
        self.timer = None
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if (event.width, event.height) == self.last_size:
            return
        self.last_size = (event.width, event.height)
        if self.timer is not None:
            self.after_cancel(self.timer)
        self.timer = self.after(80, self.redraw)

    def redraw(self):
        W, H = self.winfo_width(), self.winfo_height()
        if W < 50 or H < 50:
            return
        self.delete("all")
        self.keep = []
        self.count = 0

        piece = get_background_piece(self, self.screen)
        self.show_picture(0, 0, piece)
        self.piece = piece.convert("RGB")        # glass panels are stacked on this copy
        self.draw(self, W, H)

    def show_picture(self, x, y, pil_image):
        photo = ImageTk.PhotoImage(pil_image)
        self.keep.append(photo)
        return self.create_image(x, y, image=photo, anchor="nw")

    def glass(self, box, radius, alpha, tint=GLASS_TINT, outline=(255, 190, 120, 150)):
        """Draws one glass panel. Later panels are drawn on top of it."""
        x1, y1, x2, y2 = box
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(self.piece.width, x2), min(self.piece.height, y2)
        if x2 - x1 < 4 or y2 - y1 < 4:
            return
        image = make_glass(self.piece, (x1, y1, x2, y2), radius, tint, alpha, outline)
        self.show_picture(x1, y1, image)
        self.piece.paste(image, (x1, y1), image)

    def glass_button(self, box, text, tint, hover_tint, command, font, left=False):
        """A glass button. It gets brighter when the mouse is over it."""
        x1, y1, x2, y2 = box
        radius = min(12, (y2 - y1) // 2)
        normal = ImageTk.PhotoImage(make_glass(self.piece, box, radius, tint, 150))
        hover = ImageTk.PhotoImage(make_glass(self.piece, box, radius, hover_tint, 225))
        self.keep += [normal, hover]

        self.count += 1
        tag = "button" + str(self.count)
        picture = self.create_image(x1, y1, image=normal, anchor="nw", tags=tag)
        if left:
            self.create_text(x1 + 20, (y1 + y2) // 2, text=text, fill=WHITE,
                             font=font, anchor="w", tags=tag)
        else:
            self.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text, fill=WHITE,
                             font=font, tags=tag)

        def on_enter(event):
            self.itemconfig(picture, image=hover)
            self.config(cursor="hand2")

        def on_leave(event):
            self.itemconfig(picture, image=normal)
            self.config(cursor="")

        self.tag_bind(tag, "<Enter>", on_enter)
        self.tag_bind(tag, "<Leave>", on_leave)
        self.tag_bind(tag, "<Button-1>", lambda event: command())


# =====================================================
# GLASS BUTTONS (rectangle, see-through look, used by EVERY button in the Admin)
# =====================================================
glass_button_cache = {}


def mix_colors(color_a, color_b, amount):
    """Mixes two (r, g, b) colors. amount=0 gives color_a, amount=1 gives color_b."""
    return tuple(int(color_a[i] * (1 - amount) + color_b[i] * amount) for i in range(3))


def find_background_color(widget):
    """Walks up the widgets to find the solid color that sits behind a button."""
    while widget is not None:
        for option in ("fg_color", "bg"):
            try:
                color = widget.cget(option)
            except Exception:
                continue
            if isinstance(color, (tuple, list)):
                color = color[-1]
            if isinstance(color, str) and color.startswith("#") and len(color) == 7:
                return color
        widget = getattr(widget, "master", None)
    return BG_DARK


def render_glass_button(width, height, tint_hex, back_hex, hover, disabled):
    """Draws one glass button picture: a tinted see-through rectangle with a soft shine
    on top and a thin light border. The result is saved, so the same button is only drawn once."""
    key = (width, height, tint_hex, back_hex, hover, disabled)
    if key in glass_button_cache:
        return glass_button_cache[key]

    back = hex_to_rgb(back_hex)
    tint = hex_to_rgb(tint_hex)
    if disabled:
        tint = (90, 80, 78)
        strength = 0.30
    elif hover:
        strength = 0.85
    else:
        strength = 0.55

    scale = 3                                            # draw big, then shrink = smooth corners
    w, h = width * scale, height * scale
    radius = min(10, height // 2) * scale

    # 1. the glass color (the tint over the page color)
    body = mix_colors(back, tint, strength)
    image = Image.new("RGBA", (w, h), body + (255,))

    # 2. the soft shine on the top half
    shine = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shine_draw = ImageDraw.Draw(shine)
    half = h // 2
    peak = 95 if hover else 70
    for y in range(half):
        shine_draw.line((0, y, w, y), fill=(255, 225, 190, int(peak * (1 - y / half))))
    image = Image.alpha_composite(image, shine)

    # 3. the thin light border
    border = mix_colors(body, (255, 205, 160), 0.85 if hover else 0.60)
    ImageDraw.Draw(image).rounded_rectangle(
        (0, 0, w - 1, h - 1), radius=radius, outline=border + (255,), width=2 * scale
    )

    # 4. round the corners and shrink
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    image.putalpha(mask)
    image = image.resize((width, height), Image.LANCZOS)

    glass_button_cache[key] = image
    return image


class GlassButton(tk.Canvas):
    """A glass rectangle button. It works like a normal button:
    GlassButton(parent, text="SAVE", width=100, height=34, command=do_it, fg_color=ORANGE)
    and later:  button.configure(text="...", fg_color=..., state="disabled")
    fg_color is the TINT of the glass."""

    def __init__(self, master, text="", width=140, height=28, command=None,
                 font=("Arial", 13, "bold"), fg_color=RED, state="normal", **ignored):
        self.back_hex = find_background_color(master)
        super().__init__(master, width=width, height=height, bg=self.back_hex,
                         highlightthickness=0, bd=0)
        self.text = text
        self.command = command
        self.font = font
        self.tint = fg_color
        self.state = state
        self.hover = False
        self.photo = None

        self.bind("<Configure>", lambda event: self.draw())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.draw()

    def draw(self):
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 4 or height < 4:                      # not shown yet: use the asked size
            width = int(float(tk.Canvas.cget(self, "width")))
            height = int(float(tk.Canvas.cget(self, "height")))

        disabled = self.state == "disabled"
        picture = render_glass_button(width, height, self.tint, self.back_hex,
                                      self.hover and not disabled, disabled)
        self.photo = ImageTk.PhotoImage(picture)
        self.delete("all")
        self.create_image(0, 0, image=self.photo, anchor="nw")
        if disabled:
            text_color = "#9A8A86"
        else:
            text_color = WHITE
        self.create_text(width // 2, height // 2, text=self.text, fill=text_color, font=self.font)

    def on_enter(self, event):
        self.hover = True
        if self.state != "disabled":
            tk.Canvas.configure(self, cursor="hand2")
        self.draw()

    def on_leave(self, event):
        self.hover = False
        tk.Canvas.configure(self, cursor="")
        self.draw()

    def on_click(self, event):
        if self.state != "disabled" and self.command is not None:
            self.command()

    def configure(self, **options):
        """Works like CTkButton.configure for the things we use."""
        if "text" in options:
            self.text = options.pop("text")
        if "fg_color" in options:
            self.tint = options.pop("fg_color")
        if "state" in options:
            self.state = options.pop("state")
        if "command" in options:
            self.command = options.pop("command")
        if "font" in options:
            self.font = options.pop("font")
        for ignored_option in ("hover_color", "text_color", "text_color_disabled",
                               "border_color", "corner_radius"):
            options.pop(ignored_option, None)
        if options:
            tk.Canvas.configure(self, **options)
        self.draw()

    config = configure



# =====================================================
# GLASS TABLE PAGE (a whole page drawn on glass: title, filters, and a table)
# =====================================================
class GlassTablePage(GlassCanvas):
    """A page that shows the blurred background through its table, like the Dashboard.
    The title, the table, the rows and the buttons are drawn on the canvas.
    The search boxes and dropdowns are real widgets placed on top of the glass.

    controls = the rows of tools above the table. Each row looks like this:
        {"height": 38, "items": [("widget", search_box, None),      # None = takes the extra space
                                 ("button", "SEARCH", 100, RED, command),
                                 ("text", "Date:", 50)]}
        {"height": 22, "items": [("info", count_label, TEXT_MUTED)]}   # a line of text
    The rows of the table are lists of cells. A cell is one of these:
        "plain text"
        ("text", "value", color, is_bold)
        ("button", "VIEW", tint_color, command)
        ("menu", "Present", color, ["Present", "Late"], command_with_new_value)"""

    def __init__(self, parent, screen, page_title, columns, row_height=46):
        super().__init__(parent, screen, lambda canvas, W, H: self.paint(canvas, W, H))
        self.page_title = page_title
        self.table_columns = columns          # list of (heading, width) - width None = extra space
        self.controls = []
        self.table_rows = []
        self.empty_text = ""
        self.first_row = 0                    # the first row that is on the screen now
        self.row_height = row_height
        self.area_top = None                  # None = the page was not painted yet
        self.page_rows = 10
        self.row_photos = []
        self.col_x = []
        self.col_w = []
        self.bind("<MouseWheel>", self.on_wheel)

    # ---------------- painting ----------------
    def paint(self, canvas, W, H):
        canvas.create_text(30, 34, text=self.page_title, anchor="w",
                           fill=WHITE, font=("Arial", 26, "bold"))

        y = 66
        for row in self.controls:
            y = self.place_row(canvas, row, y, W)

        # ----- the glass panel for the table -----
        top = y
        bottom = H - 24
        self.glass((24, top, W - 24, bottom), 16, 140)

        inner_left = 24 + 18
        inner_right = W - 24 - 22
        fixed = 0
        for heading, width in self.table_columns:
            if width is not None:
                fixed = fixed + width
        stretch = max(120, (inner_right - inner_left) - fixed)

        self.col_x = []
        self.col_w = []
        x = inner_left
        for heading, width in self.table_columns:
            if width is None:
                width = stretch
            self.col_x.append(x)
            self.col_w.append(width)
            canvas.create_text(x, top + 26, text=heading, anchor="w",
                               fill=AMBER, font=("Arial", 13, "bold"))
            x = x + width

        canvas.create_line(inner_left, top + 46, inner_right, top + 46, fill="#8A4A33")

        self.area_top = top + 52
        self.area_left = inner_left
        self.area_right = inner_right
        self.scroll_x = W - 24 - 14
        area_height = bottom - 10 - self.area_top
        self.page_rows = max(1, area_height // self.row_height)
        self.draw_rows()

    def item_width(self, item):
        return item[2]

    def place_row(self, canvas, row, y, W):
        """Places one row of tools above the table. Gives back the y where the next row starts."""
        items = row["items"]
        height = row["height"]
        gap = 10
        left = 30
        total = W - 60

        # a line of text
        if items[0][0] == "info":
            label = items[0][1]
            color = items[0][2]
            label.attach(canvas, left, y + height // 2, anchor="w", fill=color,
                         font=("Arial", 13), width=total, justify="left")
            return y + height + 4

        # work out the width of the item that takes the extra space
        fixed = gap * (len(items) - 1)
        stretch_count = 0
        for item in items:
            if self.item_width(item) is None:
                stretch_count = stretch_count + 1
            else:
                fixed = fixed + self.item_width(item)
        stretch = max(150, (total - fixed) // max(1, stretch_count))

        x = left
        for item in items:
            kind = item[0]
            width = self.item_width(item)
            if width is None:
                width = stretch

            if kind == "text":
                canvas.create_text(x, y + height // 2, text=item[1], anchor="w",
                                   fill=WHITE, font=("Arial", 14, "bold"))
            elif kind == "widget":
                widget = item[1]
                try:
                    widget.configure(width=width)
                    box_height = int(widget.cget("height"))
                except Exception:
                    box_height = height
                canvas.create_window(x, y + (height - box_height) // 2, window=widget, anchor="nw")
            elif kind == "button":
                self.put_button(x, y, width, height, item[1], item[3], item[4], "chrome", self.keep)

            x = x + width + gap

        return y + height + 10

    def put_button(self, x, y, w, h, text, tint, command, tag, store):
        """Draws one glass button on the canvas. It gets brighter when the mouse is over it."""
        normal = ImageTk.PhotoImage(render_glass_button(w, h, tint, "#2A1512", False, False))
        hover = ImageTk.PhotoImage(render_glass_button(w, h, tint, "#2A1512", True, False))
        store.append(normal)
        store.append(hover)

        self.count += 1
        unique = "gb" + str(self.count)
        tags = (tag, unique)
        picture = self.create_image(x, y, image=normal, anchor="nw", tags=tags)
        self.create_text(x + w // 2, y + h // 2, text=text, fill=WHITE,
                         font=("Arial", 12, "bold"), tags=tags)

        def on_enter(event):
            self.itemconfig(picture, image=hover)
            self.config(cursor="hand2")

        def on_leave(event):
            self.itemconfig(picture, image=normal)
            self.config(cursor="")

        self.tag_bind(unique, "<Enter>", on_enter)
        self.tag_bind(unique, "<Leave>", on_leave)
        self.tag_bind(unique, "<Button-1>", lambda event: command())

    # ---------------- the table rows ----------------
    def set_rows(self, rows, keep_scroll=False):
        """Gives the table its new rows and shows them."""
        self.table_rows = rows
        if not keep_scroll:
            self.first_row = 0
        self.draw_rows()

    def draw_rows(self):
        """Draws only the rows that fit on the screen. The mouse wheel moves through the rest."""
        if self.area_top is None:
            return                                   # the page was not painted yet

        self.delete("rows")
        self.config(cursor="")
        self.row_photos = []

        total = len(self.table_rows)
        max_first = max(0, total - self.page_rows)
        self.first_row = max(0, min(self.first_row, max_first))

        if total == 0:
            self.create_text(self.col_x[0], self.area_top + 26, text=self.empty_text,
                             anchor="w", fill=TEXT_MUTED, font=("Arial", 14), tags="rows")
            return

        for position in range(self.page_rows):
            index = self.first_row + position
            if index >= total:
                break
            row_y = self.area_top + position * self.row_height
            middle = row_y + self.row_height // 2

            for column in range(len(self.table_rows[index])):
                self.draw_cell(self.table_rows[index][column], self.col_x[column],
                               self.col_w[column], row_y, middle)

            line_y = row_y + self.row_height - 1
            self.create_line(self.area_left, line_y, self.area_right, line_y,
                             fill="#5A3026", tags="rows")

        # a small bar on the right that shows where we are in the list
        if total > self.page_rows:
            track = self.page_rows * self.row_height
            thumb = max(30, int(track * self.page_rows / total))
            thumb_y = self.area_top + int((track - thumb) * self.first_row / max_first)
            self.create_rectangle(self.scroll_x, thumb_y, self.scroll_x + 6, thumb_y + thumb,
                                  fill=ORANGE, outline="", tags="rows")

    def draw_cell(self, cell, x, width, row_y, middle):
        """Draws one cell of a row."""
        if isinstance(cell, str):
            cell = ("text", cell, WHITE, False)

        kind = cell[0]

        if kind == "text":
            if cell[3]:
                font = ("Arial", 14, "bold")
            else:
                font = ("Arial", 13)
            self.create_text(x, middle, text=cell[1], anchor="w", fill=cell[2],
                             font=font, width=width - 10, tags="rows")

        elif kind == "button":
            button_w = min(width - 10, 90)
            self.put_button(x, middle - 15, button_w, 30, cell[1], cell[2], cell[3],
                            "rows", self.row_photos)

        elif kind == "menu":
            # shows the value with a small arrow. Clicking it opens a list of choices.
            self.count += 1
            unique = "mn" + str(self.count)
            self.create_text(x, middle, text=cell[1] + "   \u25BE", anchor="w", fill=cell[2],
                             font=("Arial", 14, "bold"), tags=("rows", unique))
            self.tag_bind(unique, "<Button-1>", partial(self.open_menu, cell[3], cell[4]))
            self.tag_bind(unique, "<Enter>", lambda event: self.config(cursor="hand2"))
            self.tag_bind(unique, "<Leave>", lambda event: self.config(cursor=""))

    def open_menu(self, choices, callback, event):
        """Opens a small list of choices where the mouse is."""
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=WHITE, activebackground=RED,
                       activeforeground=WHITE, bd=0, font=("Arial", 12))
        for choice in choices:
            menu.add_command(label=choice, command=partial(callback, choice))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_wheel(self, event):
        """The mouse wheel moves the table up and down (2 rows at a time)."""
        if event.delta > 0:
            self.first_row = self.first_row - 2
        else:
            self.first_row = self.first_row + 2
        self.draw_rows()


# =====================================================
# PART 2: THE ADMIN SCREENS
# =====================================================

# ---------- Lists used by the Admin dropdowns ----------
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

DAYS = []
for day in range(1, 32):           # 1 up to 31
    DAYS.append(str(day))

# To keep the pages fast, a table shows at most this many rows at once
MAX_ROWS = 100


# ---------- Small helper functions (used by several pages) ----------
def show_or_dash(value):
    """Gives a dash for an empty value, so empty things look tidy."""
    if value == "":
        return "-"
    return value


def join_or_none(lines, none_text):
    """Puts each line on its own row, or gives a message if there are no lines."""
    if len(lines) == 0:
        return none_text
    return "\n".join(lines)


def build_admin_screen(parent, go_back):
    """Builds the whole Admin screen (sidebar menu and all the pages).
    parent  = the main window
    go_back = the function that returns to the welcome screen (the EXIT button uses it)
    It gives back two things: the screen, and a function that opens it on the Dashboard.
    Admin authentication is handled by the centered login flow in main.py.
    Everything below is indented 4 spaces because it is all inside this function."""

    screen = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=0)

    # ---------- Body: the sidebar on the left, the pages on the right ----------
    body = ctk.CTkFrame(screen, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # The glass sidebar (it is painted by draw_sidebar, further down)
    sidebar = GlassCanvas(body, screen, lambda canvas, W, H: draw_sidebar(canvas, W, H), width=300)
    sidebar.pack(side="left", fill="y")

    content = ctk.CTkFrame(body, fg_color="transparent")
    content.pack(side="left", fill="both", expand=True)

    # ---------- Page handling ----------
    # Only ONE page is shown at a time. We keep every page in this list.
    all_pages = []

    def show_page(page):
        """Hides all pages, then shows the one we want."""
        for each_page in all_pages:
            each_page.pack_forget()
        if isinstance(page, GlassCanvas):
            page.pack(fill="both", expand=True)                  # glass pages: no gap
        else:
            page.pack(fill="both", expand=True, padx=20, pady=15)

    def make_placeholder_page(title_text, note_text):
        """Makes a simple page that says it will be built later."""
        page = ctk.CTkFrame(content, fg_color="transparent")

        title = ctk.CTkLabel(page, text=title_text, font=("Arial", 28, "bold"))
        title.pack(pady=(80, 10))

        note = ctk.CTkLabel(page, text=note_text, font=("Arial", 16), text_color=TEXT_MUTED)
        note.pack()

        all_pages.append(page)
        return page

    # =====================================================
    # PAGE 1: DASHBOARD (glass)
    # =====================================================
    dashboard_page = GlassCanvas(content, screen, lambda canvas, W, H: draw_dashboard(canvas, W, H))
    all_pages.append(dashboard_page)

    # These work like labels: refresh_dashboard() uses .configure(text=...) on them
    date_label = CanvasText()
    clock_label = CanvasText()
    shift_label = CanvasText()
    total_workers_label = CanvasText("0")
    present_label = CanvasText("0")
    absent_label = CanvasText("0")
    on_leave_label = CanvasText("0")
    on_duty_label = CanvasText("0")
    pending_leave_label = CanvasText("0")
    recent_label = CanvasText("")

    # (caption, color, the number) for each of the 6 cards
    stat_cards = [
        ("Total Workers", WHITE, total_workers_label),
        ("Present Today", OK_GREEN, present_label),
        ("Absent Today", BAD_RED, absent_label),
        ("On Leave Today", AMBER, on_leave_label),
        ("Currently On Duty", ORANGE, on_duty_label),
        ("Pending Leave Requests", AMBER, pending_leave_label),
    ]

    def draw_dashboard(canvas, W, H):
        """Paints the Dashboard. Panel sizes follow the font sizes."""
        m = px(30)
        title_y = fpx(26) // 2 + px(14)
        canvas.create_text(px(36), title_y, text="FIRE STATION ADMIN DASHBOARD", anchor="w",
                           fill=WHITE, font=("Arial", 26, "bold"))
        y = title_y * 2 + px(6)

        # ----- Glass clock panel (wide enough for its longest line) -----
        pad = px(30)
        clock_w = max(text_width("Wednesday, September 30, 2026", 16, False),
                      text_width("00:00:00 PM", 34),
                      text_width("Current shift: Afternoon (2:00 PM - 10:00 PM)", 14, False)) + pad * 2
        h1, h2, h3 = fpx(16), fpx(34), fpx(14)
        clock_h = h1 + h2 + h3 + px(64)
        canvas.glass((m, y, m + clock_w, y + clock_h), 24, 150)
        line_y = y + px(20)
        date_label.attach(canvas, m + pad, line_y + h1 // 2, anchor="w", fill=WHITE, font=("Arial", 16))
        line_y = line_y + h1 + px(10)
        clock_label.attach(canvas, m + pad, line_y + h2 // 2, anchor="w", fill=AMBER, font=("Arial", 34, "bold"))
        line_y = line_y + h2 + px(10)
        shift_label.attach(canvas, m + pad, line_y + h3 // 2, anchor="w", fill=TEXT_MUTED, font=("Arial", 14))

        # ----- The 6 glass cards (3 columns, 2 rows) -----
        gap = px(20)
        card_w = (W - 2 * m - 2 * gap) // 3
        big, small = fpx(36), fpx(13)
        card_h = big + small + px(60)
        cards_top = y + clock_h + px(20)
        for index in range(len(stat_cards)):
            caption, color, value_label = stat_cards[index]
            column = index % 3
            row = index // 3
            x1 = m + column * (card_w + gap)
            y1 = cards_top + row * (card_h + gap)

            canvas.glass((x1, y1, x1 + card_w, y1 + card_h), 22, 130,
                         outline=hex_to_rgb(color) + (210,))
            middle = x1 + card_w // 2
            value_label.attach(canvas, middle, y1 + px(20) + big // 2, fill=color,
                               font=("Arial", 36, "bold"))
            canvas.create_text(middle, y1 + card_h - px(20) - small // 2, text=caption,
                               fill=WHITE, font=("Arial", 13))

        # ----- Glass panel for the recent incident reports -----
        recent_top = cards_top + 2 * card_h + gap + px(20)
        canvas.glass((m, recent_top, W - m, H - m), 22, 130)
        canvas.create_text(m + px(24), recent_top + px(24) + fpx(16) // 2,
                           text="Recent Incident Reports", anchor="w",
                           fill=AMBER, font=("Arial", 16, "bold"))
        recent_label.attach(canvas, m + px(24), recent_top + px(34) + fpx(16), anchor="nw",
                            fill=WHITE, font=("Arial", 13), width=W - 2 * m - px(48),
                            justify="left")

    def show_time():
        """Puts the date and the time on the screen."""
        now = datetime.now()
        date_label.configure(text=now.strftime("%A, %B %d, %Y"))
        clock_label.configure(text=now.strftime("%I:%M:%S %p"))

    def update_clock():
        """Updates the clock. It runs again every 1 second (1000 milliseconds).
        It only does the work when the Admin screen is really on the screen."""
        if screen.winfo_ismapped():
            show_time()
        screen.after(1000, update_clock)      # "after" runs this function again later

    def refresh_dashboard():
        """Reads the data and updates the numbers and the incident list."""
        now = datetime.now()
        today_text = now.strftime("%m/%d/%Y")        # like 10/09/2026

        total_workers_label.configure(text=str(backend.count_workers()))
        present_label.configure(text=str(backend.count_present(today_text)))
        absent_label.configure(text=str(backend.count_absent(today_text)))
        on_leave_label.configure(text=str(backend.count_on_leave(now.date())))
        on_duty_label.configure(text=str(backend.count_on_duty_now(now)))
        pending_leave_label.configure(text=str(backend.count_pending_leaves()))

        # Show which shift is happening right now
        shift_name, duty_date_text = backend.get_current_shift(now)
        start_time = backend.SHIFT_TIMES[shift_name][0]
        end_time = backend.SHIFT_TIMES[shift_name][1]
        shift_label.configure(text=f"Current shift: {shift_name} ({start_time} - {end_time})")

        # Show the 5 newest incident reports
        rows = backend.get_recent_incidents(5)

        if len(rows) == 0:
            recent_label.configure(text="No incident reports yet.")
        else:
            lines = []
            for row in rows:
                # row = (incident_id, incident_type, date_time, worker_uid, status)
                incident_number = f"INC-{row[0]:04d}"      # 1 becomes INC-0001
                lines.append(f"{incident_number}   {row[1]}   -   {row[2]}   -   reported by {row[3]}   -   {row[4]}")
            recent_label.configure(text="\n".join(lines))

    def auto_refresh():
        """Refreshes the dashboard, then does it again in 5 seconds."""
        if screen.winfo_ismapped():
            refresh_dashboard()
        settings = backend.load_settings()
        try:
            delay = int(settings.get("refresh_seconds", "5")) * 1000
        except ValueError:
            delay = 5000
        if settings.get("auto_refresh", "on") != "on":
            delay = 5000
        screen.after(delay, auto_refresh)

    # =====================================================
    # PAGE 2: WORKER LIST (glass table)
    # =====================================================
    workers_page = GlassTablePage(
        content, screen, "Worker Management",
        [("Worker ID", 130), ("Name", None), ("Sex", 100), ("Phone", 150),
         ("Status", 110), ("", 100)]
    )
    all_pages.append(workers_page)

    detail_state = {"uid": "", "confirming": False}     # remembers which worker is open

    worker_count_label = CanvasText()

    def load_worker_list():
        """Reads the search box, finds the workers, and shows them in the table."""
        search_text = search_entry.get().strip()
        total_workers = len(backend.get_all_workers())

        if search_text == "":
            records = backend.get_all_workers()
        else:
            records = backend.search_workers(search_text)

        worker_count_label.configure(text=f"Showing {len(records)} of {total_workers} worker(s)")

        rows = []
        for record in records:
            if record["status"] == "Active":
                status_color = OK_GREEN
            else:
                status_color = BAD_RED

            # partial(...) makes the button remember WHICH worker it belongs to
            rows.append([
                ("text", record["worker_uid"], WHITE, True),
                backend.make_name(record),
                record["sex"],
                record["phone_number"],
                ("text", record["status"], status_color, True),
                ("button", "VIEW", RED, partial(show_worker_detail, record["worker_uid"])),
            ])

        workers_page.empty_text = "No workers found."
        workers_page.set_rows(rows)

    def show_all_workers():
        """Empties the search box and shows every worker."""
        search_entry.delete(0, "end")
        load_worker_list()

    def on_enter_key(event):
        """Lets the Admin press the Enter key to search."""
        load_worker_list()

    search_entry = ctk.CTkEntry(
        workers_page, placeholder_text="Search by name, Worker ID, or phone number", height=38
    )
    search_entry.bind("<Return>", on_enter_key)          # pressing Enter also searches

    workers_page.controls = [
        {"height": 38, "items": [
            ("widget", search_entry, None),
            ("button", "SEARCH", 100, RED, load_worker_list),
            ("button", "SHOW ALL", 100, EMBER_GRAY, show_all_workers),
        ]},
        {"height": 22, "items": [("info", worker_count_label, TEXT_MUTED)]},
    ]

    # =====================================================
    # PAGE 3: WORKER DETAILS
    # =====================================================
    worker_detail_page = ctk.CTkScrollableFrame(content, fg_color="transparent")
    all_pages.append(worker_detail_page)

    def make_history_section(section_parent, title_text):
        """Makes a title and an empty text label for one history list.
        It gives back the text label so we can fill it in later."""
        title = ctk.CTkLabel(section_parent, text=title_text, font=("Arial", 15, "bold"), anchor="w")
        title.pack(fill="x", padx=10, pady=(15, 0))

        text_label = ctk.CTkLabel(section_parent, text="", font=("Arial", 13), justify="left", anchor="w")
        text_label.pack(fill="x", padx=10, pady=(3, 0))
        return text_label

    def fill_worker_history(uid):
        """Fills the activity history part of the Worker Details page."""
        history = backend.get_worker_history(uid)

        history_summary_label.configure(
            text=f"Attendance records: {len(history['attendance'])}      "
                 f"Absence reports: {len(history['absences'])}      "
                 f"Leave requests: {len(history['leaves'])}      "
                 f"Incident reports: {len(history['incidents'])}      "
                 f"Duties assigned: {len(history['duties'])}"
        )

        lines = []
        for record in history["attendance"][:5]:
            lines.append(
                f"{record['date']}   In: {record['time_in']}   "
                f"Out: {show_or_dash(record['time_out'])}   {record['status']}"
            )
        history_attendance_label.configure(text=join_or_none(lines, "No attendance records yet."))

        lines = []
        for record in history["absences"][:5]:
            lines.append(f"{record['absence_date']}   {record['reason']}")
        history_absence_label.configure(text=join_or_none(lines, "No absence reports yet."))

        lines = []
        for record in history["leaves"][:5]:
            lines.append(
                f"{record['leave_type']}:  {record['start_date']} to {record['end_date']}   -   {record['status']}"
            )
        history_leave_label.configure(text=join_or_none(lines, "No leave requests yet."))

        lines = []
        for record in history["incidents"][:5]:
            lines.append(
                f"INC-{int(record['incident_id']):04d}   {record['incident_type']}   -   "
                f"{record['date_time']}   -   {record['status']}"
            )
        history_incident_label.configure(text=join_or_none(lines, "No incident reports yet."))

        lines = []
        for record in history["duties"][:5]:
            lines.append(
                f"{record['duty_date']}   {record['shift']} ({record['start_time']} - {record['end_time']})   -   {record['assignment']}"
            )
        history_duty_label.configure(text=join_or_none(lines, "No duties assigned yet."))

    def fill_worker_detail():
        """Fills the Worker Details page with the open worker's information."""
        uid = detail_state["uid"]
        record = backend.get_full_worker(uid)

        detail_uid_label.configure(text=uid)

        if record["status"] == "Active":
            detail_status_label.configure(text="Status: ACTIVE", text_color=OK_GREEN)
            detail_status_button.configure(
                text="DEACTIVATE WORKER", fg_color=RED, hover_color=RED_DARK
            )
        else:
            detail_status_label.configure(text="Status: INACTIVE", text_color=BAD_RED)
            detail_status_button.configure(
                text="REACTIVATE WORKER", fg_color=GREEN_BTN, hover_color=GREEN_BTN_HOVER
            )

        detail_state["confirming"] = False

        detail_info_label.configure(
            text=f"Full Name:  {backend.make_name(record)}\n\n"
                 f"Sex:  {record['sex']}\n\n"
                 f"Birthday:  {record['birthday']}\n\n"
                 f"Phone Number:  {record['phone_number']}\n\n"
                 f"Address:  {record['address']}\n\n"
                 f"Registration Date:  {record['registration_date']}"
        )

        fill_worker_history(uid)

    def show_worker_detail(uid):
        """Opens the Worker Details page for one worker."""
        record = backend.get_full_worker(uid)
        if record is None:
            return

        detail_state["uid"] = uid
        detail_message_label.configure(text="")
        fill_worker_detail()
        show_page(worker_detail_page)

    def go_back_to_list():
        """Goes back to the worker list (with the newest data)."""
        load_worker_list()
        show_page(workers_page)

    def toggle_worker_status():
        """Deactivates an Active worker (after a second click to confirm) or reactivates an Inactive one."""
        uid = detail_state["uid"]
        record = backend.get_full_worker(uid)

        if record["status"] == "Active":
            # First click: ask the Admin to click again. No popup is used.
            if not detail_state["confirming"]:
                detail_state["confirming"] = True
                detail_status_button.configure(text="CLICK AGAIN TO CONFIRM")
                detail_message_label.configure(
                    text="This worker will no longer be able to log in. All records are kept.",
                    text_color=WARN_ORANGE
                )
                return

            backend.set_worker_status(uid, "Inactive")
            fill_worker_detail()
            detail_message_label.configure(text="Worker deactivated.", text_color=BAD_RED)
        else:
            backend.set_worker_status(uid, "Active")
            fill_worker_detail()
            detail_message_label.configure(text="Worker reactivated.", text_color=OK_GREEN)

    detail_back_button = GlassButton(
        worker_detail_page, text="< BACK TO LIST", width=140, height=32, command=go_back_to_list
    )
    detail_back_button.pack(anchor="w", padx=10, pady=(5, 0))

    detail_title = ctk.CTkLabel(
        worker_detail_page, text="Worker Details", font=("Arial", 26, "bold"), anchor="w"
    )
    detail_title.pack(fill="x", padx=10, pady=(10, 0))

    detail_uid_label = ctk.CTkLabel(
        worker_detail_page, text="", font=("Arial", 34, "bold"), text_color=ORANGE, anchor="w"
    )
    detail_uid_label.pack(fill="x", padx=10)

    detail_status_label = ctk.CTkLabel(
        worker_detail_page, text="", font=("Arial", 16, "bold"), anchor="w"
    )
    detail_status_label.pack(fill="x", padx=10, pady=(0, 10))

    detail_card = ctk.CTkFrame(worker_detail_page, border_width=2, corner_radius=10)
    detail_card.pack(fill="x", padx=10)

    detail_info_label = ctk.CTkLabel(
        detail_card, text="", font=("Arial", 15), justify="left", anchor="w"
    )
    detail_info_label.pack(fill="x", padx=20, pady=20)

    detail_buttons_row = ctk.CTkFrame(worker_detail_page, fg_color="transparent")
    detail_buttons_row.pack(fill="x", padx=10, pady=(15, 0))

    detail_edit_button = GlassButton(
        detail_buttons_row, text="EDIT INFORMATION", width=200, height=40,
        font=("Arial", 14, "bold"), fg_color=ORANGE, hover_color=ORANGE_DARK,
        command=lambda: start_edit_worker()
    )
    detail_edit_button.pack(side="left", padx=(0, 10))

    detail_status_button = GlassButton(
        detail_buttons_row, text="", width=220, height=40,
        font=("Arial", 14, "bold"), command=toggle_worker_status
    )
    detail_status_button.pack(side="left")

    detail_message_label = ctk.CTkLabel(
        worker_detail_page, text="", font=("Arial", 14, "bold"), anchor="w"
    )
    detail_message_label.pack(fill="x", padx=10, pady=(10, 0))

    history_title = ctk.CTkLabel(
        worker_detail_page, text="Worker Activity / History", font=("Arial", 20, "bold"), anchor="w"
    )
    history_title.pack(fill="x", padx=10, pady=(25, 0))

    history_summary_label = ctk.CTkLabel(
        worker_detail_page, text="", font=("Arial", 13), text_color=TEXT_MUTED, anchor="w"
    )
    history_summary_label.pack(fill="x", padx=10, pady=(3, 0))

    history_attendance_label = make_history_section(worker_detail_page, "Recent Attendance")
    history_absence_label = make_history_section(worker_detail_page, "Recent Absence Reports")
    history_leave_label = make_history_section(worker_detail_page, "Recent Leave Requests")
    history_incident_label = make_history_section(worker_detail_page, "Recent Incident Reports")
    history_duty_label = make_history_section(worker_detail_page, "Recent Duties")

    bottom_space = ctk.CTkLabel(worker_detail_page, text="")
    bottom_space.pack(pady=10)

    # =====================================================
    # PAGE 4: EDIT WORKER
    # =====================================================
    worker_edit_page = ctk.CTkScrollableFrame(content, fg_color="transparent")
    all_pages.append(worker_edit_page)

    # ----- Lists for the Birthday dropdowns (workers are 16 to 80 years old) -----
    current_year = datetime.now().year
    birthday_years = []
    for year in range(current_year - 16, current_year - 81, -1):    # newest year first
        birthday_years.append(str(year))

    def set_entry_text(entry, text):
        """Puts text in a text box (it empties the box first)."""
        entry.delete(0, "end")
        entry.insert(0, text)

    def make_edit_field(field_parent, label_text, placeholder):
        """Makes one label + one text box. It gives back the text box."""
        label = ctk.CTkLabel(field_parent, text=label_text, font=("Arial", 14, "bold"), anchor="w")
        label.pack(fill="x", padx=40, pady=(10, 0))

        entry = ctk.CTkEntry(field_parent, placeholder_text=placeholder, height=35)
        entry.pack(fill="x", padx=40, pady=(2, 0))
        return entry

    def start_edit_worker():
        """Opens the Edit page and fills it with the worker's current information."""
        uid = detail_state["uid"]
        record = backend.get_full_worker(uid)

        edit_uid_label.configure(text=f"Worker ID:  {uid}   (cannot be changed)")

        set_entry_text(edit_first_name_entry, record["first_name"])
        set_entry_text(edit_middle_name_entry, record["middle_name"])
        set_entry_text(edit_surname_entry, record["surname"])
        set_entry_text(edit_suffix_entry, record["suffix"])
        set_entry_text(edit_address_entry, record["address"])
        set_entry_text(edit_phone_entry, record["phone_number"])
        edit_sex_variable.set(record["sex"])

        # Turn the saved birthday text into the three dropdowns
        try:
            birthday = datetime.strptime(record["birthday"], "%m/%d/%Y")
            edit_month_menu.set(MONTHS[birthday.month - 1])
            edit_day_menu.set(str(birthday.day))
            edit_year_menu.set(str(birthday.year))
        except ValueError:
            edit_month_menu.set("Month")
            edit_day_menu.set("Day")
            edit_year_menu.set("Year")

        edit_message_label.configure(text="")
        show_page(worker_edit_page)

    def cancel_edit():
        """Goes back to the Worker Details page without saving."""
        show_page(worker_detail_page)

    def save_worker_changes():
        """Checks the Edit form, then saves the changes."""
        uid = detail_state["uid"]

        first_name = edit_first_name_entry.get().strip()
        middle_name = edit_middle_name_entry.get().strip()
        surname = edit_surname_entry.get().strip()
        suffix = edit_suffix_entry.get().strip()
        address = edit_address_entry.get().strip()
        phone = edit_phone_entry.get().strip()
        sex = edit_sex_variable.get()

        month_text = edit_month_menu.get()
        day_text = edit_day_menu.get()
        year_text = edit_year_menu.get()

        # Check 1: required text fields cannot be empty (suffix is not required)
        if (first_name == "" or middle_name == "" or surname == "" or
                address == "" or phone == ""):
            edit_message_label.configure(text="Please complete all required fields.")
            return

        # Check 2: the Admin must choose a Month, a Day, and a Year
        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            edit_message_label.configure(text="Please select the complete birthday (Month, Day, and Year).")
            return

        # Check 3: the date must really exist (for example, February 30 does not)
        month_number = MONTHS.index(month_text) + 1
        try:
            birthday = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            edit_message_label.configure(text="That birthday date does not exist. Please check the day.")
            return

        birthday_text = birthday.strftime("%m/%d/%Y")      # like 05/20/2000

        # Check 4: sex must be selected
        if sex == "":
            edit_message_label.configure(text="Please select Male or Female.")
            return

        # Check 5: phone must be 11 digits and start with 09
        if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
            edit_message_label.configure(text="Please enter a valid phone number like 09123456789.")
            return

        backend.update_worker(
            uid, first_name, middle_name, surname, suffix,
            address, birthday_text, sex, phone
        )

        show_worker_detail(uid)
        detail_message_label.configure(
            text="Worker information updated successfully.", text_color=OK_GREEN
        )

    edit_title = ctk.CTkLabel(
        worker_edit_page, text="Edit Worker Information", font=("Arial", 26, "bold")
    )
    edit_title.pack(pady=(10, 0))

    edit_uid_label = ctk.CTkLabel(
        worker_edit_page, text="", font=("Arial", 16, "bold"), text_color=ORANGE
    )
    edit_uid_label.pack(pady=(0, 5))

    edit_first_name_entry = make_edit_field(worker_edit_page, "First Name", "Enter first name")
    edit_middle_name_entry = make_edit_field(worker_edit_page, "Middle Name", "Enter middle name")
    edit_surname_entry = make_edit_field(worker_edit_page, "Surname", "Enter surname")
    edit_suffix_entry = make_edit_field(worker_edit_page, "Suffix (optional)", "Jr., Sr., III")
    edit_address_entry = make_edit_field(worker_edit_page, "Address", "Street, City, Province")

    # ----- Birthday: three dropdowns -----
    edit_birthday_title = ctk.CTkLabel(
        worker_edit_page, text="Birthday", font=("Arial", 14, "bold"), anchor="w"
    )
    edit_birthday_title.pack(fill="x", padx=40, pady=(10, 0))

    edit_birthday_row = ctk.CTkFrame(worker_edit_page, fg_color="transparent")
    edit_birthday_row.pack(fill="x", padx=40, pady=(2, 0))

    edit_month_menu = ctk.CTkOptionMenu(edit_birthday_row, values=MONTHS, width=200, height=35)
    edit_month_menu.set("Month")
    edit_month_menu.pack(side="left", padx=(0, 10))

    edit_day_menu = ctk.CTkOptionMenu(edit_birthday_row, values=DAYS, width=120, height=35)
    edit_day_menu.set("Day")
    edit_day_menu.pack(side="left", padx=(0, 10))

    edit_year_menu = ctk.CTkOptionMenu(edit_birthday_row, values=birthday_years, width=140, height=35)
    edit_year_menu.set("Year")
    edit_year_menu.pack(side="left")

    # ----- Sex: two radio buttons -----
    edit_sex_title = ctk.CTkLabel(
        worker_edit_page, text="Sex", font=("Arial", 14, "bold"), anchor="w"
    )
    edit_sex_title.pack(fill="x", padx=40, pady=(10, 0))

    edit_sex_variable = ctk.StringVar(value="")

    edit_sex_row = ctk.CTkFrame(worker_edit_page, fg_color="transparent")
    edit_sex_row.pack(fill="x", padx=40, pady=(2, 0))

    edit_male_button = ctk.CTkRadioButton(
        edit_sex_row, text="Male", variable=edit_sex_variable, value="Male"
    )
    edit_male_button.pack(side="left", padx=(0, 30))

    edit_female_button = ctk.CTkRadioButton(
        edit_sex_row, text="Female", variable=edit_sex_variable, value="Female"
    )
    edit_female_button.pack(side="left")

    edit_phone_entry = make_edit_field(worker_edit_page, "Phone Number", "09XXXXXXXXX")

    edit_message_label = ctk.CTkLabel(
        worker_edit_page, text="", font=("Arial", 14, "bold"), text_color=BAD_RED
    )
    edit_message_label.pack(pady=(15, 0))

    edit_save_button = GlassButton(
        worker_edit_page, text="SAVE CHANGES", height=42,
        font=("Arial", 15, "bold"), command=save_worker_changes
    )
    edit_save_button.pack(fill="x", padx=40, pady=(10, 0))

    edit_cancel_button = GlassButton(
        worker_edit_page, text="CANCEL", height=36, fg_color=EMBER_GRAY, command=cancel_edit
    )
    edit_cancel_button.pack(fill="x", padx=40, pady=(10, 30))

    # ---------- GLASS Worker Details + Edit pages (they replace the old plain ones above) ----------
    import worker_detail_glass

    def go_back_to_list_glass():
        load_worker_list()
        show_page(workers_page)

    show_worker_detail = worker_detail_glass.create_worker_detail_pages(
        content, all_pages, screen, show_page, go_back_to_list_glass
    )


    # =====================================================
    # THE OTHER PAGES
    # Each of these pages is built by its own function (further down in this file).
    # =====================================================
    attendance_page, load_attendance_page = create_attendance_page(content, all_pages, screen)
    duty_page, load_duty_page = create_duty_page(content, all_pages)
    leave_page, load_leave_page = create_leave_page(content, all_pages)

    # The Reports page and the Incident Report pages work together as ONE section.
    def open_incident_management():
        load_incident_page()         # show the newest incident reports
        show_page(incident_page)

    def back_to_reports():
        load_reports_page()          # show the newest report
        show_page(reports_page)

    incident_page, load_incident_page = create_incident_page(
        content, all_pages, show_page, back_to_reports
    )
    reports_page, load_reports_page = create_reports_page(
        content, all_pages, open_incident_management
    )

    # =====================================================
    # PAGE: SETTINGS
    # =====================================================
    settings_page = ctk.CTkFrame(content, fg_color=BG_DARK)
    all_pages.append(settings_page)

    settings_title = ctk.CTkLabel(
        settings_page, text="System Settings", font=("Arial", 28, "bold"), text_color=TEXT
    )
    settings_title.pack(pady=(35, 5))

    settings_note = ctk.CTkLabel(
        settings_page,
        text="Important controls for the fire station system. Settings are saved in a text file.",
        font=("Arial", 13), text_color=TEXT_MUTED
    )
    settings_note.pack(pady=(0, 22))

    settings_card = ctk.CTkFrame(
        settings_page, fg_color=BG_PANEL, corner_radius=18, border_width=1, border_color=BORDER
    )
    settings_card.pack(fill="x", padx=45, pady=5)

    auto_refresh_var = ctk.StringVar(value=backend.get_setting("auto_refresh", "on"))
    notifications_var = ctk.StringVar(value=backend.get_setting("notifications", "on"))
    refresh_seconds_var = ctk.StringVar(value=backend.get_setting("refresh_seconds", "5"))
    settings_status = ctk.CTkLabel(settings_page, text="", font=("Arial", 13, "bold"), text_color=OK_GREEN)

    def add_setting_row(row, title_text, note_text, widget):
        ctk.CTkLabel(settings_card, text=title_text, font=("Arial", 16, "bold"), text_color=TEXT, anchor="w").grid(
            row=row, column=0, padx=25, pady=(16, 2), sticky="w"
        )
        ctk.CTkLabel(settings_card, text=note_text, font=("Arial", 11), text_color=TEXT_MUTED, anchor="w", justify="left").grid(
            row=row + 1, column=0, padx=25, pady=(0, 12), sticky="w"
        )
        widget.grid(row=row, column=1, rowspan=2, padx=25, pady=15, sticky="e")

    refresh_menu = FireOptionMenu(settings_card, values=["5", "10", "30", "60"], variable=refresh_seconds_var, width=120)
    auto_menu = FireOptionMenu(settings_card, values=["on", "off"], variable=auto_refresh_var, width=120)
    notice_menu = FireOptionMenu(settings_card, values=["on", "off"], variable=notifications_var, width=120)

    add_setting_row(0, "Dashboard Auto Refresh", "Automatically refresh dashboard information while the Admin screen is open.", auto_menu)
    add_setting_row(2, "Refresh Interval", "Choose how often the dashboard checks for updated records.", refresh_menu)
    add_setting_row(4, "Save Notifications", "Play the system bell after important records are saved.", notice_menu)

    settings_card.grid_columnconfigure(0, weight=1)

    def save_current_settings():
        try:
            seconds = int(refresh_seconds_var.get())
            if seconds not in (5, 10, 30, 60):
                raise ValueError
        except ValueError:
            settings_status.configure(text="Choose a valid refresh interval.", text_color=BAD_RED)
            return
        backend.save_settings({
            "auto_refresh": auto_refresh_var.get(),
            "refresh_seconds": seconds,
            "notifications": notifications_var.get(),
        })
        settings_status.configure(text="Settings saved successfully.", text_color=OK_GREEN)

    def open_data_folder():
        os.makedirs(backend.DATA_FOLDER, exist_ok=True)
        try:
            os.startfile(backend.DATA_FOLDER)
        except AttributeError:
            import subprocess, sys
            command = ["open", backend.DATA_FOLDER] if sys.platform == "darwin" else ["xdg-open", backend.DATA_FOLDER]
            subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror("Open Data Folder", str(exc))

    def make_backup():
        try:
            target = backend.backup_data()
            settings_status.configure(text="Backup created: " + os.path.basename(target), text_color=OK_GREEN)
        except OSError as exc:
            settings_status.configure(text="Backup failed: " + str(exc), text_color=BAD_RED)

    def export_all_tables():
        try:
            target, _ = backend.export_all_csv()
            settings_status.configure(text="CSV export created: " + os.path.basename(target), text_color=OK_GREEN)
        except OSError as exc:
            settings_status.configure(text="CSV export failed: " + str(exc), text_color=BAD_RED)

    button_row = ctk.CTkFrame(settings_page, fg_color="transparent")
    button_row.pack(fill="x", padx=45, pady=(20, 8))
    for column in range(4):
        button_row.grid_columnconfigure(column, weight=1)

    GlassButton(button_row, text="SAVE SETTINGS", height=42, command=save_current_settings).grid(row=0, column=0, padx=5, sticky="ew")
    GlassButton(button_row, text="OPEN DATA FOLDER", height=42, fg_color=EMBER_GRAY, command=open_data_folder).grid(row=0, column=1, padx=5, sticky="ew")
    GlassButton(button_row, text="BACKUP DATA", height=42, fg_color=ORANGE, command=make_backup).grid(row=0, column=2, padx=5, sticky="ew")
    GlassButton(button_row, text="EXPORT ALL CSV", height=42, fg_color=GREEN_BTN, command=export_all_tables).grid(row=0, column=3, padx=5, sticky="ew")

    settings_status.pack(pady=(5, 10))

    def refresh_settings_page():
        saved = backend.load_settings()
        auto_refresh_var.set(saved.get("auto_refresh", "on"))
        refresh_seconds_var.set(saved.get("refresh_seconds", "5"))
        notifications_var.set(saved.get("notifications", "on"))
        settings_status.configure(text="")


    # =====================================================
    # SIDEBAR BUTTONS
    # =====================================================
    def go_dashboard():
        refresh_dashboard()          # show the newest numbers when we come back
        show_page(dashboard_page)

    def go_workers():
        load_worker_list()
        show_page(workers_page)

    def go_attendance():
        load_attendance_page()
        show_page(attendance_page)

    def go_duty():
        load_duty_page()
        show_page(duty_page)

    def go_leave():
        load_leave_page()
        show_page(leave_page)

    def go_reports():
        load_reports_page()
        show_page(reports_page)

    def go_settings():
        refresh_settings_page()
        show_page(settings_page)

    # ----- The glass sidebar -----
    sidebar_items = [
        ("Dashboard", go_dashboard),
        ("Workers", go_workers),
        ("Attendance", go_attendance),
        ("Duty / Shifts", go_duty),
        ("Leave / Absence", go_leave),
        ("Reports", go_reports),
        ("Settings", go_settings),
    ]
    logo_picture = load_logo()

    def draw_sidebar(canvas, W, H):
        """Paints the sidebar (bigger text, smaller glass spacing)."""
        canvas.glass((px(14), px(14), W - px(14), H - px(14)), 18, 150)

        top = px(30)
        if logo_picture is not None:
            logo = logo_picture.copy()
            logo.thumbnail((px(125), px(125)))
            canvas.show_picture((W - logo.width) // 2, top, logo)
            top = top + logo.height + px(4)

        title_h = fpx(15) * 2
        canvas.create_text(W // 2, top + px(16) + title_h // 2, text="Iligan City Fire System Admin",
                           fill=AMBER, font=("Arial", 15, "bold"), width=W - px(60), justify="center")
        top = top + px(16) + title_h + px(20)

        exit_h = fpx(15) + px(40)
        button_h = fpx(15) + px(40)
        step = button_h + px(14)
        available = (H - px(30) - exit_h - px(20)) - top
        if step * len(sidebar_items) > available:
            step = max(40, available // len(sidebar_items))
            button_h = step - px(10)

        y = top
        for text, command in sidebar_items:
            canvas.glass_button((px(30), y, W - px(30), y + button_h), text, (90, 30, 20),
                                (210, 60, 20), command, ("Arial", 15, "bold"), left=True)
            y = y + step

        canvas.glass_button((px(30), H - px(30) - exit_h, W - px(30), H - px(30)), "EXIT ADMIN",
                            (140, 20, 20), (220, 40, 30), go_back, ("Arial", 15, "bold"))
    
    # ---------- Start the clock and the auto refresh ----------
    update_clock()          # starts the clock
    auto_refresh()          # refreshes the numbers every 5 seconds

    def open_admin():
        """Called by main.py every time the Admin button is clicked."""
        show_time()
        go_dashboard()

    return screen, open_admin


# =====================================================
# ADMIN PAGE: ATTENDANCE
# =====================================================
ATTENDANCE_STATUS_CHOICES = ["Present", "Late", "Absent", "On Leave", "Official Duty"]
ATTENDANCE_DATE_MODES = ["Today", "This Week", "This Month", "All Dates", "Specific Date"]
ATTENDANCE_STATUS_FILTERS = ["All Statuses"] + ATTENDANCE_STATUS_CHOICES


def create_attendance_page(content, all_pages, screen):
    """Builds the Attendance page (a glass table) inside the "content" area of the Admin screen.
    It gives back two things: the page, and a function that reloads the table."""

    page = GlassTablePage(
        content, screen, "Attendance Records",
        [("Worker ID", 130), ("Name", None), ("Date", 130), ("Time In", 120),
         ("Time Out", 120), ("Status", 170)]
    )
    all_pages.append(page)

    this_year = datetime.now().year
    years = []
    for year in range(this_year, this_year - 6, -1):      # this year and the 5 years before
        years.append(str(year))

    # The color of each status in the table
    status_colors = {"Present": OK_GREEN, "Late": WARN_ORANGE, "Absent": BAD_RED,
                     "On Leave": AMBER, "Official Duty": ORANGE}

    count_label = CanvasText()
    message_label = CanvasText()

    def get_date_range():
        """Works out the first and last date to show, from the Date dropdown.
        Gives back (first_date, last_date, error_text). Both None means "all dates"."""
        today = datetime.now().date()
        mode = date_mode_menu.get()

        if mode == "Today":
            return today, today, ""

        if mode == "This Week":
            monday = today - timedelta(days=today.weekday())    # weekday(): Monday is 0
            sunday = monday + timedelta(days=6)
            return monday, sunday, ""

        if mode == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day, ""

        if mode == "Specific Date":
            month_number = MONTHS.index(month_menu.get()) + 1
            try:
                chosen = datetime(int(year_menu.get()), month_number, int(day_menu.get())).date()
            except ValueError:
                return None, None, "That date does not exist. Please check the day."
            return chosen, chosen, ""

        return None, None, ""        # All Dates

    def update_specific_date_menus():
        """Keep date parts clickable so choosing one can switch to Specific Date."""
        month_menu.configure(state="normal")
        day_menu.configure(state="normal")
        year_menu.configure(state="normal")

    def change_status(attendance_id, new_status):
        """Runs when the Admin picks a new status in a row. It saves right away."""
        backend.update_attendance_status(attendance_id, new_status)
        load_attendance_list(keep_scroll=True)          # redraw the table, stay at the same place
        message_label.configure(text=f"Status updated to {new_status}.", text_color=OK_GREEN)

    def load_attendance_list(keep_scroll=False):
        """Reads the filters, finds the records, and shows them in the table."""
        first_date, last_date, error_text = get_date_range()

        if error_text != "":
            message_label.configure(text=error_text, text_color=BAD_RED)
            return

        records = backend.get_attendance_records(
            first_date, last_date, search_entry.get().strip(), status_filter_menu.get()
        )

        count_label.configure(text=f"Found {len(records)} record(s)")
        message_label.configure(text="")

        rows = []
        for record in records:
            # partial(...) makes the status list remember WHICH record it belongs to
            rows.append([
                ("text", record["worker_uid"], WHITE, True),
                record["full_name"],
                record["date"],
                show_or_dash(record["time_in"]),
                show_or_dash(record["time_out"]),
                ("menu", record["status"], status_colors.get(record["status"], WHITE),
                 ATTENDANCE_STATUS_CHOICES, partial(change_status, record["attendance_id"])),
            ])

        page.empty_text = "No attendance records found."
        page.set_rows(rows, keep_scroll)

    def on_filter_change(value):
        """Runs when a filter dropdown changes."""
        update_specific_date_menus()
        load_attendance_list()

    def on_specific_date_part_change(value):
        """Choosing a date part automatically activates the specific-date filter."""
        date_mode_menu.set("Specific Date")
        update_specific_date_menus()
        load_attendance_list()

    def on_enter_key(event):
        load_attendance_list()

    def set_default_filters():
        """Puts every filter back to its starting choice."""
        now = datetime.now()
        search_entry.delete(0, "end")
        date_mode_menu.set("Today")
        month_menu.set(MONTHS[now.month - 1])
        day_menu.set(str(now.day))
        year_menu.set(str(now.year))
        status_filter_menu.set("All Statuses")
        update_specific_date_menus()

    def reset_filters():
        set_default_filters()
        load_attendance_list()

    # ----- The search box and the filter dropdowns (real widgets on top of the glass) -----
    search_entry = ctk.CTkEntry(
        page, placeholder_text="Search by Worker ID or name", height=38
    )
    search_entry.bind("<Return>", on_enter_key)

    date_mode_menu = ctk.CTkOptionMenu(
        page, values=ATTENDANCE_DATE_MODES, width=140, height=34, command=on_filter_change
    )
    month_menu = ctk.CTkOptionMenu(
        page, values=MONTHS, width=130, height=34, command=on_specific_date_part_change
    )
    day_menu = ctk.CTkOptionMenu(
        page, values=DAYS, width=70, height=34, command=on_specific_date_part_change
    )
    year_menu = ctk.CTkOptionMenu(
        page, values=years, width=90, height=34, command=on_specific_date_part_change
    )
    status_filter_menu = ctk.CTkOptionMenu(
        page, values=ATTENDANCE_STATUS_FILTERS, width=140, height=34, command=on_filter_change
    )

    page.controls = [
        {"height": 38, "items": [
            ("widget", search_entry, None),
            ("button", "SEARCH", 100, RED, load_attendance_list),
            ("button", "RESET", 100, EMBER_GRAY, reset_filters),
        ]},
        {"height": 34, "items": [
            ("text", "Date:", 50),
            ("widget", date_mode_menu, 140),
            ("widget", month_menu, 130),
            ("widget", day_menu, 70),
            ("widget", year_menu, 90),
            ("text", "Status:", 70),
            ("widget", status_filter_menu, 140),
        ]},
        {"height": 22, "items": [("info", count_label, TEXT_MUTED)]},
        {"height": 22, "items": [("info", message_label, WHITE)]},
    ]

    # Start with the filters on their default choices (Today, All Statuses)
    set_default_filters()

    return page, load_attendance_list


# =====================================================
# ADMIN PAGE: DUTY / SHIFTS
# =====================================================
SHIFTS = ["Morning", "Afternoon", "Night"]
DUTY_PERIODS = ["Today", "This Week", "This Month", "All Dates"]

# Used to put the shifts of one day in order
SHIFT_ORDER = {"Morning": 1, "Afternoon": 2, "Night": 3}


def create_duty_page(content, all_pages):
    """Builds the Duty / Shifts page inside the "content" area of the Admin screen.
    The Admin assigns a shift to a worker for a date, and can edit or remove it.
    It gives back two things: the page, and a function that reloads it."""

    page = ctk.CTkFrame(content, fg_color="transparent")
    all_pages.append(page)

    this_year = datetime.now().year
    years = []
    for year in range(this_year - 1, this_year + 2):      # last year, this year, next year
        years.append(str(year))

    # This remembers which row is waiting for a second click on REMOVE
    pending = {"id": ""}

    def get_worker_labels():
        """Makes a list like 'UID-8337  -  alrie madula jr' for every Active worker."""
        labels = []
        for worker in backend.read_records("employees"):
            if worker["status"] == "Active":
                labels.append(worker["worker_uid"] + "  -  " + backend.make_name(worker))
        return labels

    def refresh_worker_menu():
        """Fills the Worker dropdown with the newest list of Active workers."""
        labels = get_worker_labels()
        if len(labels) == 0:
            labels = ["No workers registered"]

        worker_menu.configure(values=labels)
        if worker_menu.get() not in labels:
            worker_menu.set(labels[0])

    def read_form_date():
        """Reads the three date dropdowns. Gives back a real date, or None if it does not exist."""
        month_number = MONTHS.index(month_menu.get()) + 1
        try:
            return datetime(int(year_menu.get()), month_number, int(day_menu.get())).date()
        except ValueError:
            return None

    def assign_duty():
        """Runs when ASSIGN DUTY is clicked. Checks the form, then saves the duty."""
        label = worker_menu.get()

        if label == "No workers registered":
            message_label.configure(text="There are no workers yet. Register a worker first.",
                                    text_color=BAD_RED)
            return

        uid = label.split()[0]                 # the Worker ID is the first word, like UID-8337
        worker = backend.get_full_worker(uid)

        if worker is None:
            message_label.configure(text="That worker was not found.", text_color=BAD_RED)
            return

        if worker["status"] != "Active":
            message_label.configure(
                text="This worker is Inactive. Reactivate the worker first.", text_color=BAD_RED
            )
            return

        duty_day = read_form_date()
        if duty_day is None:
            message_label.configure(text="That date does not exist. Please check the day.",
                                    text_color=BAD_RED)
            return

        shift = shift_menu.get()
        assignment = assignment_entry.get().strip()
        if assignment == "":
            assignment = "Fire Station"        # the starting choice

        date_text = duty_day.strftime("%m/%d/%Y")          # like 10/14/2026
        full_name = backend.make_name(worker)

        # Does this worker already have a duty on this date? (save_duty will replace it)
        old_shift = ""
        for record in backend.read_records("duty_schedule"):
            if record["worker_uid"] == uid and record["duty_date"] == date_text:
                old_shift = record["shift"]

        backend.save_duty(uid, date_text, shift, assignment)

        nice_date = duty_day.strftime("%B %d, %Y")
        if old_shift == "":
            text = f"Duty assigned: {full_name} ({uid}) - {shift} shift on {nice_date}."
        else:
            text = (f"Duty updated: {full_name} ({uid}) now has the {shift} shift on "
                    f"{nice_date}. It replaced the {old_shift} shift.")

        pending["id"] = ""
        load_list()
        message_label.configure(text=text, text_color=OK_GREEN)

    def edit_duty(duty_id):
        """Fills the form with a duty, so the Admin can change it and click ASSIGN DUTY."""
        for record in backend.read_records("duty_schedule"):
            if record["duty_id"] != str(duty_id):
                continue

            worker = backend.get_full_worker(record["worker_uid"])
            if worker is None:
                full_name = "(unknown worker)"
            else:
                full_name = backend.make_name(worker)

            worker_menu.set(record["worker_uid"] + "  -  " + full_name)
            shift_menu.set(record["shift"])
            set_entry_text(assignment_entry, record["assignment"])

            try:
                day = datetime.strptime(record["duty_date"], "%m/%d/%Y")
                month_menu.set(MONTHS[day.month - 1])
                day_menu.set(str(day.day))
                year_menu.set(str(day.year))
            except ValueError:
                pass

            pending["id"] = ""
            load_list()
            message_label.configure(
                text="Editing this duty. Change what you need, then click ASSIGN DUTY.",
                text_color=TEXT_MUTED
            )
            return

    def remove_duty(duty_id):
        """First click: asks to confirm. Second click on the same row: removes the duty."""
        if pending["id"] != str(duty_id):
            pending["id"] = str(duty_id)
            load_list()
            message_label.configure(
                text="Click CONFIRM on the same row to remove this duty.", text_color=WARN_ORANGE
            )
            return

        kept = []
        for record in backend.read_records("duty_schedule"):
            if record["duty_id"] != str(duty_id):
                kept.append(record)
        backend.write_records("duty_schedule", kept)

        pending["id"] = ""
        load_list()
        message_label.configure(text="Duty removed.", text_color=BAD_RED)

    def set_entry_text(entry, text):
        """Puts text in a text box (it empties the box first)."""
        entry.delete(0, "end")
        entry.insert(0, text)

    def get_range():
        """Works out the first and last date to show, from the Period dropdown.
        Both are None for "All Dates"."""
        today = datetime.now().date()
        mode = period_menu.get()

        if mode == "Today":
            return today, today

        if mode == "This Week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday

        if mode == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day

        return None, None        # All Dates

    def sort_key(record):
        """Tells Python how to order the duties: by date, then shift, then Worker ID."""
        return (record["day"], SHIFT_ORDER.get(record["shift"], 9), record["worker_uid"])

    def build_rows(records):
        """Draws the table: a header row, then one row for every duty."""
        for widget in table_frame.winfo_children():
            widget.destroy()

        headers = ["Date", "Worker ID", "Name", "Shift", "Time", "Assignment", ""]
        for column in range(len(headers)):
            header_label = ctk.CTkLabel(
                table_frame, text=headers[column], font=("Arial", 13, "bold"), anchor="w"
            )
            header_label.grid(row=0, column=column, padx=8, pady=(5, 8), sticky="w")

        if len(records) == 0:
            none_label = ctk.CTkLabel(
                table_frame, text="No duties found for this period.",
                font=("Arial", 14), text_color=TEXT_MUTED
            )
            none_label.grid(row=1, column=0, columnspan=7, padx=8, pady=20, sticky="w")
            return

        row_number = 1
        for record in records:
            date_label = ctk.CTkLabel(
                table_frame, text=record["day"].strftime("%m/%d/%Y (%a)"),
                font=("Arial", 13), anchor="w"
            )
            date_label.grid(row=row_number, column=0, padx=8, pady=4, sticky="w")

            uid_label = ctk.CTkLabel(
                table_frame, text=record["worker_uid"], font=("Arial", 13, "bold"), anchor="w"
            )
            uid_label.grid(row=row_number, column=1, padx=8, pady=4, sticky="w")

            name_label = ctk.CTkLabel(
                table_frame, text=record["full_name"], font=("Arial", 13), anchor="w"
            )
            name_label.grid(row=row_number, column=2, padx=8, pady=4, sticky="w")

            shift_label = ctk.CTkLabel(
                table_frame, text=record["shift"], font=("Arial", 13, "bold"), anchor="w"
            )
            shift_label.grid(row=row_number, column=3, padx=8, pady=4, sticky="w")

            time_label = ctk.CTkLabel(
                table_frame, text=record["start_time"] + " - " + record["end_time"],
                font=("Arial", 13), anchor="w"
            )
            time_label.grid(row=row_number, column=4, padx=8, pady=4, sticky="w")

            assignment_label = ctk.CTkLabel(
                table_frame, text=record["assignment"], font=("Arial", 13),
                anchor="w", wraplength=130, justify="left"
            )
            assignment_label.grid(row=row_number, column=5, padx=8, pady=4, sticky="w")

            actions_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            actions_frame.grid(row=row_number, column=6, padx=8, pady=4)

            edit_button = GlassButton(
                actions_frame, text="EDIT", width=60, height=28,
                fg_color=ORANGE, hover_color=ORANGE_DARK,
                command=partial(edit_duty, record["duty_id"])
            )
            edit_button.pack(side="left", padx=(0, 5))

            if pending["id"] == record["duty_id"]:
                remove_text = "CONFIRM"
                remove_color = RED
            else:
                remove_text = "REMOVE"
                remove_color = EMBER_GRAY

            remove_button = GlassButton(
                actions_frame, text=remove_text, width=80, height=28, fg_color=remove_color,
                command=partial(remove_duty, record["duty_id"])
            )
            remove_button.pack(side="left")

            row_number = row_number + 1

    def load_list():
        """Reads the filters, finds the duties, and shows them in the table."""
        first_date, last_date = get_range()
        words = search_entry.get().strip().lower().split()

        names = {}
        for worker in backend.read_records("employees"):
            names[worker["worker_uid"]] = backend.make_name(worker)

        found = []
        for record in backend.read_records("duty_schedule"):
            try:
                day = datetime.strptime(record["duty_date"], "%m/%d/%Y").date()
            except ValueError:
                continue                                    # skip a damaged date

            if first_date is not None and (day < first_date or day > last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            everything = (uid + " " + full_name).lower()

            found_all = True
            for word in words:
                if word not in everything:
                    found_all = False
            if not found_all:
                continue

            record["full_name"] = full_name
            record["day"] = day
            found.append(record)

        found.sort(key=sort_key)

        if len(found) > MAX_ROWS:
            count_label.configure(
                text=f"Found {len(found)} duties. Showing the first {MAX_ROWS}. "
                     "Use the filters to narrow the list."
            )
        else:
            count_label.configure(text=f"Found {len(found)} duty record(s)")

        build_rows(found[:MAX_ROWS])

    def on_filter_change(value):
        pending["id"] = ""
        message_label.configure(text="")
        load_list()

    def on_enter_key(event):
        pending["id"] = ""
        load_list()

    def reset_filters():
        search_entry.delete(0, "end")
        period_menu.set("This Week")
        pending["id"] = ""
        message_label.configure(text="")
        load_list()

    def set_default_form():
        """Puts the form back to its starting choices (today, Morning shift)."""
        now = datetime.now()
        month_menu.set(MONTHS[now.month - 1])
        day_menu.set(str(now.day))
        year_menu.set(str(now.year))
        shift_menu.set("Morning")
        assignment_entry.delete(0, "end")

    def load_page():
        """Shows the newest data (it runs whenever the Admin opens this page)."""
        refresh_worker_menu()
        pending["id"] = ""
        load_list()

    title = ctk.CTkLabel(page, text="Duty / Shifts", font=("Arial", 26, "bold"))
    title.pack(anchor="w")

    form_card = ctk.CTkFrame(page, border_width=2, corner_radius=10)
    form_card.pack(fill="x", pady=(8, 0))

    form_row_one = ctk.CTkFrame(form_card, fg_color="transparent")
    form_row_one.pack(fill="x", padx=15, pady=(12, 0))

    worker_title = ctk.CTkLabel(form_row_one, text="Worker:", font=("Arial", 14, "bold"))
    worker_title.pack(side="left", padx=(0, 5))

    worker_menu = ctk.CTkOptionMenu(form_row_one, values=["No workers registered"],
                                    width=300, height=34)
    worker_menu.pack(side="left", padx=(0, 20))

    date_title = ctk.CTkLabel(form_row_one, text="Date:", font=("Arial", 14, "bold"))
    date_title.pack(side="left", padx=(0, 5))

    month_menu = ctk.CTkOptionMenu(form_row_one, values=MONTHS, width=120, height=34)
    month_menu.pack(side="left", padx=(0, 5))

    day_menu = ctk.CTkOptionMenu(form_row_one, values=DAYS, width=65, height=34)
    day_menu.pack(side="left", padx=(0, 5))

    year_menu = ctk.CTkOptionMenu(form_row_one, values=years, width=80, height=34)
    year_menu.pack(side="left")

    form_row_two = ctk.CTkFrame(form_card, fg_color="transparent")
    form_row_two.pack(fill="x", padx=15, pady=(10, 12))

    shift_title = ctk.CTkLabel(form_row_two, text="Shift:", font=("Arial", 14, "bold"))
    shift_title.pack(side="left", padx=(0, 5))

    shift_menu = ctk.CTkOptionMenu(form_row_two, values=SHIFTS, width=130, height=34)
    shift_menu.pack(side="left", padx=(0, 20))

    assignment_title = ctk.CTkLabel(form_row_two, text="Assignment:", font=("Arial", 14, "bold"))
    assignment_title.pack(side="left", padx=(0, 5))

    assignment_entry = ctk.CTkEntry(form_row_two, placeholder_text="Fire Station", height=34)
    assignment_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

    assign_button = GlassButton(
        form_row_two, text="ASSIGN DUTY", width=140, height=34,
        font=("Arial", 13, "bold"), command=assign_duty
    )
    assign_button.pack(side="left")

    message_label = ctk.CTkLabel(
        page, text="", font=("Arial", 14, "bold"), anchor="w", justify="left", wraplength=800
    )
    message_label.pack(fill="x", pady=(6, 0))

    list_title = ctk.CTkLabel(page, text="Scheduled Duties", font=("Arial", 18, "bold"), anchor="w")
    list_title.pack(fill="x", pady=(4, 0))

    filter_row = ctk.CTkFrame(page, fg_color="transparent")
    filter_row.pack(fill="x", pady=(6, 0))

    period_title = ctk.CTkLabel(filter_row, text="Period:", font=("Arial", 14, "bold"))
    period_title.pack(side="left", padx=(0, 5))

    period_menu = ctk.CTkOptionMenu(
        filter_row, values=DUTY_PERIODS, width=130, height=34, command=on_filter_change
    )
    period_menu.set("This Week")
    period_menu.pack(side="left", padx=(0, 15))

    search_entry = ctk.CTkEntry(
        filter_row, placeholder_text="Search by Worker ID or name", height=34
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    search_entry.bind("<Return>", on_enter_key)

    search_button = GlassButton(
        filter_row, text="SEARCH", width=90, height=34, command=load_list
    )
    search_button.pack(side="left", padx=(0, 10))

    reset_button = GlassButton(
        filter_row, text="RESET", width=80, height=34, fg_color=EMBER_GRAY, command=reset_filters
    )
    reset_button.pack(side="left")

    count_label = ctk.CTkLabel(page, text="", font=("Arial", 13), text_color=TEXT_MUTED, anchor="w")
    count_label.pack(fill="x", pady=(6, 3))

    table_frame = ctk.CTkScrollableFrame(page, border_width=2)
    table_frame.pack(fill="both", expand=True)
    table_frame.grid_columnconfigure(2, weight=1)        # the Name column gets the extra space

    set_default_form()

    return page, load_page


# =====================================================
# ADMIN PAGE: LEAVE / ABSENCE
# =====================================================
LEAVE_FILTERS = ["Pending", "Approved", "Rejected", "All Statuses"]
ABSENCE_DATE_MODES = ["All Dates", "Today", "This Week", "This Month"]


def create_leave_page(content, all_pages):
    """Builds the Leave / Absence page inside the "content" area of the Admin screen.
    It gives back two things: the page, and a function that reloads both tables."""

    page = ctk.CTkFrame(content, fg_color="transparent")
    all_pages.append(page)

    def show_leave_tab():
        """Shows the Leave Requests tab and hides the Absence Reports tab."""
        absence_tab.pack_forget()
        leave_tab.pack(fill="both", expand=True)
        leave_tab_button.configure(fg_color=RED)
        absence_tab_button.configure(fg_color=EMBER_GRAY)

    def show_absence_tab():
        """Shows the Absence Reports tab and hides the Leave Requests tab."""
        leave_tab.pack_forget()
        absence_tab.pack(fill="both", expand=True)
        absence_tab_button.configure(fg_color=RED)
        leave_tab_button.configure(fg_color=EMBER_GRAY)

    def make_header_row(table, headers):
        """Draws the first row of a table (the column titles)."""
        for column in range(len(headers)):
            header_label = ctk.CTkLabel(
                table, text=headers[column], font=("Arial", 13, "bold"), anchor="w"
            )
            header_label.grid(row=0, column=column, padx=8, pady=(5, 8), sticky="w")

    # ---------------- LEAVE REQUESTS ----------------
    def decide(leave_id, new_status):
        """Runs when APPROVE, REJECT, or UNDO is clicked. It saves right away."""
        backend.update_leave_status(leave_id, new_status)
        load_leave_list()

        if new_status == "Approved":
            leave_message_label.configure(text="Leave request approved.", text_color=OK_GREEN)
        elif new_status == "Rejected":
            leave_message_label.configure(text="Leave request rejected.", text_color=BAD_RED)
        else:
            leave_message_label.configure(
                text="Leave request set back to Pending.", text_color=WARN_ORANGE
            )

    def build_leave_rows(records):
        """Draws the leave table: a header row, then one row for every request."""
        for widget in leave_table.winfo_children():
            widget.destroy()

        make_header_row(leave_table, ["Worker", "Leave Type", "Dates", "Reason", "Status", "Action"])

        if len(records) == 0:
            none_label = ctk.CTkLabel(
                leave_table, text="No leave requests found.",
                font=("Arial", 14), text_color=TEXT_MUTED
            )
            none_label.grid(row=1, column=0, columnspan=6, padx=8, pady=20, sticky="w")
            return

        row_number = 1
        for record in records:
            worker_label = ctk.CTkLabel(
                leave_table, text=record["worker_uid"] + "\n" + record["full_name"],
                font=("Arial", 13, "bold"), justify="left", anchor="w"
            )
            worker_label.grid(row=row_number, column=0, padx=8, pady=6, sticky="w")

            filed_day = record["date_filed"][:10]       # keeps only the date, like 10/09/2026
            type_label = ctk.CTkLabel(
                leave_table, text=record["leave_type"] + "\nFiled: " + filed_day,
                font=("Arial", 13), justify="left", anchor="w"
            )
            type_label.grid(row=row_number, column=1, padx=8, pady=6, sticky="w")

            dates_label = ctk.CTkLabel(
                leave_table, text=record["start_date"] + "\nto " + record["end_date"],
                font=("Arial", 13), justify="left", anchor="w"
            )
            dates_label.grid(row=row_number, column=2, padx=8, pady=6, sticky="w")

            reason_label = ctk.CTkLabel(
                leave_table, text=show_or_dash(record["reason"]), font=("Arial", 13),
                justify="left", anchor="w", wraplength=230
            )
            reason_label.grid(row=row_number, column=3, padx=8, pady=6, sticky="w")

            if record["status"] == "Approved":
                status_color = OK_GREEN
            elif record["status"] == "Rejected":
                status_color = BAD_RED
            else:
                status_color = WARN_ORANGE
            status_label = ctk.CTkLabel(
                leave_table, text=record["status"], font=("Arial", 14, "bold"),
                text_color=status_color, anchor="w"
            )
            status_label.grid(row=row_number, column=4, padx=8, pady=6, sticky="w")

            actions_frame = ctk.CTkFrame(leave_table, fg_color="transparent")
            actions_frame.grid(row=row_number, column=5, padx=8, pady=6)

            if record["status"] == "Pending":
                approve_button = GlassButton(
                    actions_frame, text="APPROVE", width=85, height=28,
                    fg_color=GREEN_BTN, hover_color=GREEN_BTN_HOVER,
                    command=partial(decide, record["leave_id"], "Approved")
                )
                approve_button.pack(side="left", padx=(0, 5))

                reject_button = GlassButton(
                    actions_frame, text="REJECT", width=85, height=28,
                    fg_color=RED, hover_color=RED_DARK,
                    command=partial(decide, record["leave_id"], "Rejected")
                )
                reject_button.pack(side="left")
            else:
                undo_button = GlassButton(
                    actions_frame, text="UNDO", width=85, height=28, fg_color=EMBER_GRAY,
                    command=partial(decide, record["leave_id"], "Pending")
                )
                undo_button.pack(side="left")

            row_number = row_number + 1

    def load_leave_list():
        """Reads the filters, finds the leave requests, and shows them in the table."""
        records = backend.get_leave_requests(
            leave_filter_menu.get(), leave_search_entry.get().strip()
        )

        pending_total = backend.count_pending_leaves()
        leave_tab_button.configure(text=f"LEAVE REQUESTS  ({pending_total} pending)")

        if len(records) > MAX_ROWS:
            leave_count_label.configure(
                text=f"Found {len(records)} request(s). Showing the newest {MAX_ROWS}. "
                     "Use the filters to narrow the list."
            )
        else:
            leave_count_label.configure(text=f"Found {len(records)} request(s)")

        leave_message_label.configure(text="")
        build_leave_rows(records[:MAX_ROWS])

    def on_leave_filter_change(value):
        load_leave_list()

    def on_leave_enter_key(event):
        load_leave_list()

    def reset_leave_filters():
        leave_search_entry.delete(0, "end")
        leave_filter_menu.set("Pending")
        load_leave_list()

    # ---------------- ABSENCE REPORTS ----------------
    def get_absence_range():
        """Works out the first and last date to show, from the Date dropdown.
        Both are None for "All Dates"."""
        today = datetime.now().date()
        mode = absence_date_menu.get()

        if mode == "Today":
            return today, today

        if mode == "This Week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday

        if mode == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day

        return None, None        # All Dates

    def build_absence_rows(records):
        """Draws the absence table: a header row, then one row for every report."""
        for widget in absence_table.winfo_children():
            widget.destroy()

        make_header_row(
            absence_table, ["Worker", "Absence Date", "Reason", "Explanation", "Filed"]
        )

        if len(records) == 0:
            none_label = ctk.CTkLabel(
                absence_table, text="No absence reports found.",
                font=("Arial", 14), text_color=TEXT_MUTED
            )
            none_label.grid(row=1, column=0, columnspan=5, padx=8, pady=20, sticky="w")
            return

        row_number = 1
        for record in records:
            worker_label = ctk.CTkLabel(
                absence_table, text=record["worker_uid"] + "\n" + record["full_name"],
                font=("Arial", 13, "bold"), justify="left", anchor="w"
            )
            worker_label.grid(row=row_number, column=0, padx=8, pady=6, sticky="w")

            date_label = ctk.CTkLabel(
                absence_table, text=record["absence_date"], font=("Arial", 13), anchor="w"
            )
            date_label.grid(row=row_number, column=1, padx=8, pady=6, sticky="w")

            reason_label = ctk.CTkLabel(
                absence_table, text=record["reason"], font=("Arial", 13),
                justify="left", anchor="w", wraplength=170
            )
            reason_label.grid(row=row_number, column=2, padx=8, pady=6, sticky="w")

            explanation_label = ctk.CTkLabel(
                absence_table, text=show_or_dash(record["explanation"]), font=("Arial", 13),
                justify="left", anchor="w", wraplength=240
            )
            explanation_label.grid(row=row_number, column=3, padx=8, pady=6, sticky="w")

            filed_label = ctk.CTkLabel(
                absence_table, text=record["date_filed"].replace(" ", "\n", 1),
                font=("Arial", 13), justify="left", anchor="w"
            )
            filed_label.grid(row=row_number, column=4, padx=8, pady=6, sticky="w")

            row_number = row_number + 1

    def load_absence_list():
        """Reads the filters, finds the absence reports, and shows them in the table."""
        first_date, last_date = get_absence_range()

        records = backend.get_absence_reports(
            first_date, last_date, absence_search_entry.get().strip()
        )

        if len(records) > MAX_ROWS:
            absence_count_label.configure(
                text=f"Found {len(records)} report(s). Showing the newest {MAX_ROWS}. "
                     "Use the filters to narrow the list."
            )
        else:
            absence_count_label.configure(text=f"Found {len(records)} report(s)")

        build_absence_rows(records[:MAX_ROWS])

    def on_absence_filter_change(value):
        load_absence_list()

    def on_absence_enter_key(event):
        load_absence_list()

    def reset_absence_filters():
        absence_search_entry.delete(0, "end")
        absence_date_menu.set("All Dates")
        load_absence_list()

    def load_page():
        """Reloads both tabs (it runs whenever the Admin opens this page)."""
        load_leave_list()
        load_absence_list()

    title = ctk.CTkLabel(page, text="Leave / Absence Management", font=("Arial", 26, "bold"))
    title.pack(anchor="w")

    tab_row = ctk.CTkFrame(page, fg_color="transparent")
    tab_row.pack(fill="x", pady=(10, 10))

    leave_tab_button = GlassButton(
        tab_row, text="LEAVE REQUESTS", width=240, height=38,
        font=("Arial", 14, "bold"), command=show_leave_tab
    )
    leave_tab_button.pack(side="left", padx=(0, 10))

    absence_tab_button = GlassButton(
        tab_row, text="ABSENCE REPORTS", width=240, height=38,
        font=("Arial", 14, "bold"), command=show_absence_tab
    )
    absence_tab_button.pack(side="left")

    # ----- TAB 1: LEAVE REQUESTS -----
    leave_tab = ctk.CTkFrame(page, fg_color="transparent")

    leave_search_row = ctk.CTkFrame(leave_tab, fg_color="transparent")
    leave_search_row.pack(fill="x")

    leave_search_entry = ctk.CTkEntry(
        leave_search_row, placeholder_text="Search by Worker ID or name", height=38
    )
    leave_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    leave_search_entry.bind("<Return>", on_leave_enter_key)

    leave_status_title = ctk.CTkLabel(leave_search_row, text="Status:", font=("Arial", 14, "bold"))
    leave_status_title.pack(side="left", padx=(0, 5))

    leave_filter_menu = ctk.CTkOptionMenu(
        leave_search_row, values=LEAVE_FILTERS, width=140, height=38,
        command=on_leave_filter_change
    )
    leave_filter_menu.set("Pending")
    leave_filter_menu.pack(side="left", padx=(0, 10))

    leave_search_button = GlassButton(
        leave_search_row, text="SEARCH", width=90, height=38, command=load_leave_list
    )
    leave_search_button.pack(side="left", padx=(0, 10))

    leave_reset_button = GlassButton(
        leave_search_row, text="RESET", width=90, height=38, fg_color=EMBER_GRAY,
        command=reset_leave_filters
    )
    leave_reset_button.pack(side="left")

    leave_count_label = ctk.CTkLabel(
        leave_tab, text="", font=("Arial", 14), text_color=TEXT_MUTED, anchor="w"
    )
    leave_count_label.pack(fill="x", pady=(8, 0))

    leave_message_label = ctk.CTkLabel(leave_tab, text="", font=("Arial", 14, "bold"), anchor="w")
    leave_message_label.pack(fill="x", pady=(0, 5))

    leave_table = ctk.CTkScrollableFrame(leave_tab, border_width=2)
    leave_table.pack(fill="both", expand=True)
    leave_table.grid_columnconfigure(3, weight=1)        # the Reason column gets the extra space

    # ----- TAB 2: ABSENCE REPORTS -----
    absence_tab = ctk.CTkFrame(page, fg_color="transparent")

    absence_search_row = ctk.CTkFrame(absence_tab, fg_color="transparent")
    absence_search_row.pack(fill="x")

    absence_search_entry = ctk.CTkEntry(
        absence_search_row, placeholder_text="Search by Worker ID or name", height=38
    )
    absence_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    absence_search_entry.bind("<Return>", on_absence_enter_key)

    absence_date_title = ctk.CTkLabel(absence_search_row, text="Date:", font=("Arial", 14, "bold"))
    absence_date_title.pack(side="left", padx=(0, 5))

    absence_date_menu = ctk.CTkOptionMenu(
        absence_search_row, values=ABSENCE_DATE_MODES, width=140, height=38,
        command=on_absence_filter_change
    )
    absence_date_menu.set("All Dates")
    absence_date_menu.pack(side="left", padx=(0, 10))

    absence_search_button = GlassButton(
        absence_search_row, text="SEARCH", width=90, height=38, command=load_absence_list
    )
    absence_search_button.pack(side="left", padx=(0, 10))

    absence_reset_button = GlassButton(
        absence_search_row, text="RESET", width=90, height=38, fg_color=EMBER_GRAY,
        command=reset_absence_filters
    )
    absence_reset_button.pack(side="left")

    absence_count_label = ctk.CTkLabel(
        absence_tab, text="", font=("Arial", 14), text_color=TEXT_MUTED, anchor="w"
    )
    absence_count_label.pack(fill="x", pady=(8, 5))

    absence_table = ctk.CTkScrollableFrame(absence_tab, border_width=2)
    absence_table.pack(fill="both", expand=True)
    absence_table.grid_columnconfigure(3, weight=1)      # the Explanation column gets the extra space

    show_leave_tab()

    return page, load_page


# =====================================================
# ADMIN PAGES: INCIDENT REPORT MANAGEMENT (list, details, edit)
# =====================================================
INCIDENT_TYPES = ["Fire", "Vehicle Accident", "Rescue", "Medical Emergency", "Alarm", "Other"]
INCIDENT_TYPE_FILTERS = ["All Types"] + INCIDENT_TYPES

INCIDENT_EDIT_STATUSES = ["Open", "Under Review", "Closed"]
INCIDENT_STATUS_FILTERS = ["All Statuses"] + INCIDENT_EDIT_STATUSES + ["Deleted"]


def get_incident_status_color(status):
    """Gives a color for each incident status."""
    if status == "Open":
        return WARN_ORANGE
    if status == "Under Review":
        return AMBER
    if status == "Closed":
        return OK_GREEN
    return BAD_RED                # Deleted


def create_incident_page(content, all_pages, show_page, go_back_to_reports):
    """Builds the Incident Reports pages inside the "content" area of the Admin screen.
    show_page is the function of the Admin screen that switches pages.
    It has 3 pages: the list, the details, and the edit form.
    It gives back two things: the list page, and a function that reloads the list."""

    list_page = ctk.CTkFrame(content, fg_color="transparent")
    all_pages.append(list_page)

    detail_page = ctk.CTkScrollableFrame(content, fg_color="transparent")
    all_pages.append(detail_page)

    edit_page = ctk.CTkScrollableFrame(content, fg_color="transparent")
    all_pages.append(edit_page)

    # This remembers which report is open, and if we are waiting for a second click
    state = {"id": "", "confirming": False}

    this_year = datetime.now().year
    years = []
    for year in range(this_year, this_year - 6, -1):      # this year and the 5 years before
        years.append(str(year))

    hours = []
    for hour in range(1, 13):
        hours.append(str(hour))

    minutes = []
    for minute in range(0, 60):
        minutes.append(f"{minute:02d}")                   # :02d makes it 2 digits, like 05

    # ---------------- LIST PAGE ----------------
    def build_rows(records):
        """Draws the table: a header row, then one row for every report."""
        for widget in table_frame.winfo_children():
            widget.destroy()

        headers = ["Incident ID", "Type", "Date / Time", "Location", "Reported By", "Status", ""]
        for column in range(len(headers)):
            header_label = ctk.CTkLabel(
                table_frame, text=headers[column], font=("Arial", 13, "bold"), anchor="w"
            )
            header_label.grid(row=0, column=column, padx=8, pady=(5, 8), sticky="w")

        if len(records) == 0:
            none_label = ctk.CTkLabel(
                table_frame, text="No incident reports found.",
                font=("Arial", 14), text_color=TEXT_MUTED
            )
            none_label.grid(row=1, column=0, columnspan=7, padx=8, pady=20, sticky="w")
            return

        row_number = 1
        for record in records:
            number_label = ctk.CTkLabel(
                table_frame, text=record["incident_number"], font=("Arial", 14, "bold"), anchor="w"
            )
            number_label.grid(row=row_number, column=0, padx=8, pady=6, sticky="w")

            type_label = ctk.CTkLabel(
                table_frame, text=record["incident_type"], font=("Arial", 13),
                anchor="w", wraplength=110, justify="left"
            )
            type_label.grid(row=row_number, column=1, padx=8, pady=6, sticky="w")

            date_time_label = ctk.CTkLabel(
                table_frame, text=record["date_time"].replace(" ", "\n", 1),
                font=("Arial", 13), anchor="w", justify="left"
            )
            date_time_label.grid(row=row_number, column=2, padx=8, pady=6, sticky="w")

            location_label = ctk.CTkLabel(
                table_frame, text=record["location"], font=("Arial", 13),
                anchor="w", wraplength=170, justify="left"
            )
            location_label.grid(row=row_number, column=3, padx=8, pady=6, sticky="w")

            reporter_label = ctk.CTkLabel(
                table_frame, text=record["worker_uid"] + "\n" + record["full_name"],
                font=("Arial", 13), anchor="w", justify="left"
            )
            reporter_label.grid(row=row_number, column=4, padx=8, pady=6, sticky="w")

            status_label = ctk.CTkLabel(
                table_frame, text=record["status"], font=("Arial", 13, "bold"),
                text_color=get_incident_status_color(record["status"]), anchor="w"
            )
            status_label.grid(row=row_number, column=5, padx=8, pady=6, sticky="w")

            view_button = GlassButton(
                table_frame, text="VIEW", width=70, height=28,
                command=partial(show_detail, record["incident_id"])
            )
            view_button.grid(row=row_number, column=6, padx=8, pady=6)

            row_number = row_number + 1

    def load_list():
        """Reads the filters, finds the reports, and shows them in the table."""
        records = backend.get_incident_list(
            type_filter_menu.get(), status_filter_menu.get(), search_entry.get().strip()
        )

        if len(records) > MAX_ROWS:
            count_label.configure(
                text=f"Found {len(records)} report(s). Showing the newest {MAX_ROWS}. "
                     "Use the filters to narrow the list."
            )
        else:
            count_label.configure(text=f"Found {len(records)} report(s)")

        build_rows(records[:MAX_ROWS])

    def on_filter_change(value):
        load_list()

    def on_enter_key(event):
        load_list()

    def reset_filters():
        search_entry.delete(0, "end")
        type_filter_menu.set("All Types")
        status_filter_menu.set("All Statuses")
        load_list()

    # ---------------- DETAILS PAGE ----------------
    def fill_detail():
        """Fills the Details page with the open report's information."""
        record = backend.get_incident(state["id"])
        if record is None:
            return

        detail_number_label.configure(text=record["incident_number"])
        detail_status_label.configure(
            text="Status: " + record["status"].upper(),
            text_color=get_incident_status_color(record["status"])
        )

        detail_info_label.configure(
            text=f"Incident Type:  {record['incident_type']}\n\n"
                 f"Date and Time of Incident:  {record['date_time']}\n\n"
                 f"Location:  {record['location']}\n\n"
                 f"Personnel Involved:  {show_or_dash(record['personnel_involved'])}\n\n"
                 f"Reported By:  {record['full_name']}  ({record['worker_uid']})\n\n"
                 f"Date Reported:  {record['date_reported']}"
        )

        detail_description_label.configure(text=show_or_dash(record["description"]))
        detail_actions_label.configure(text=show_or_dash(record["actions_taken"]))
        detail_additional_label.configure(text=show_or_dash(record["additional_info"]))

        # A deleted report can only be restored. Any other report can be deleted or edited.
        if record["status"] == "Deleted":
            detail_delete_button.configure(
                text="RESTORE REPORT", fg_color=GREEN_BTN, hover_color=GREEN_BTN_HOVER
            )
            detail_edit_button.configure(state="disabled")
        else:
            detail_delete_button.configure(
                text="DELETE REPORT", fg_color=RED, hover_color=RED_DARK
            )
            detail_edit_button.configure(state="normal")

        state["confirming"] = False

    def show_detail(incident_id):
        """Opens the Details page for one report."""
        record = backend.get_incident(incident_id)
        if record is None:
            return

        state["id"] = str(incident_id)
        detail_message_label.configure(text="")
        fill_detail()
        show_page(detail_page)

    def back_to_list():
        """Goes back to the list (with the newest data)."""
        load_list()
        show_page(list_page)

    def toggle_delete():
        """Deletes a report (after a second click to confirm) or restores a deleted one."""
        record = backend.get_incident(state["id"])

        if record["status"] == "Deleted":
            backend.set_incident_status(state["id"], "Open")
            fill_detail()
            detail_message_label.configure(
                text="Report restored. Its status is now Open.", text_color=OK_GREEN
            )
            return

        if not state["confirming"]:
            state["confirming"] = True
            detail_delete_button.configure(text="CLICK AGAIN TO CONFIRM")
            detail_message_label.configure(
                text="This report will be hidden from the lists and from the worker. "
                     "You can restore it later.",
                text_color=WARN_ORANGE
            )
            return

        backend.set_incident_status(state["id"], "Deleted")
        fill_detail()
        detail_message_label.configure(text="Report deleted.", text_color=BAD_RED)

    # ---------------- EDIT PAGE ----------------
    def set_entry_text(entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)

    def set_box_text(box, text):
        box.delete("1.0", "end")
        box.insert("1.0", text)

    def start_edit():
        """Opens the Edit page and fills it with the report's current information."""
        record = backend.get_incident(state["id"])
        if record is None:
            return

        edit_number_label.configure(text=record["incident_number"] + "   (cannot be changed)")
        edit_type_menu.set(record["incident_type"])

        try:
            moment = datetime.strptime(record["date_time"], "%m/%d/%Y %I:%M %p")
            edit_month_menu.set(MONTHS[moment.month - 1])
            edit_day_menu.set(str(moment.day))
            edit_year_menu.set(str(moment.year))

            hour_12 = moment.hour % 12          # 13 becomes 1, 12 becomes 0, ...
            if hour_12 == 0:
                hour_12 = 12                    # midnight and noon show as 12
            edit_hour_menu.set(str(hour_12))
            edit_minute_menu.set(f"{moment.minute:02d}")
            if moment.hour < 12:
                edit_am_pm_menu.set("AM")
            else:
                edit_am_pm_menu.set("PM")
        except ValueError:
            edit_month_menu.set("Month")
            edit_day_menu.set("Day")
            edit_year_menu.set("Year")
            edit_hour_menu.set("1")
            edit_minute_menu.set("00")
            edit_am_pm_menu.set("AM")

        set_entry_text(edit_location_entry, record["location"])
        set_entry_text(edit_personnel_entry, record["personnel_involved"])
        set_box_text(edit_description_box, record["description"])
        set_box_text(edit_actions_box, record["actions_taken"])
        set_box_text(edit_additional_box, record["additional_info"])

        if record["status"] in INCIDENT_EDIT_STATUSES:
            edit_status_menu.set(record["status"])
        else:
            edit_status_menu.set("Open")

        edit_message_label.configure(text="")
        show_page(edit_page)

    def cancel_edit():
        show_page(detail_page)

    def save_changes():
        """Checks the Edit form, then saves the changes."""
        incident_type = edit_type_menu.get()
        location = edit_location_entry.get().strip()
        personnel = edit_personnel_entry.get().strip()
        description = edit_description_box.get("1.0", "end").strip()
        actions = edit_actions_box.get("1.0", "end").strip()
        additional = edit_additional_box.get("1.0", "end").strip()
        status = edit_status_menu.get()

        month_text = edit_month_menu.get()
        day_text = edit_day_menu.get()
        year_text = edit_year_menu.get()

        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            edit_message_label.configure(text="Please select the complete date (Month, Day, and Year).")
            return

        month_number = MONTHS.index(month_text) + 1
        try:
            incident_day = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            edit_message_label.configure(text="That date does not exist. Please check the day.")
            return

        hour_number = int(edit_hour_menu.get())
        minute_number = int(edit_minute_menu.get())
        am_pm = edit_am_pm_menu.get()

        # Change the 12-hour clock into the 24-hour clock that Python uses
        if am_pm == "PM" and hour_number != 12:
            hour_number = hour_number + 12
        if am_pm == "AM" and hour_number == 12:
            hour_number = 0

        incident_moment = incident_day.replace(hour=hour_number, minute=minute_number)

        if incident_moment > datetime.now():
            edit_message_label.configure(text="The incident date and time cannot be in the future.")
            return

        if location == "":
            edit_message_label.configure(text="Please enter the location of the incident.")
            return

        if description == "":
            edit_message_label.configure(text="Please enter a description of the incident.")
            return

        date_time_text = incident_moment.strftime("%m/%d/%Y %I:%M %p")      # like 10/09/2026 06:15 AM

        backend.update_incident(
            state["id"], incident_type, date_time_text, location, personnel,
            description, actions, additional, status
        )

        show_detail(state["id"])
        detail_message_label.configure(
            text="Incident report updated successfully.", text_color=OK_GREEN
        )

    def load_page():
        """Shows the list page's newest data (it runs whenever the Admin opens this page)."""
        load_list()

    # ----- WIDGETS: LIST PAGE -----
    reports_back_button = GlassButton(
        list_page, text="< BACK TO REPORTS", width=160, height=32,
        command=go_back_to_reports
    )
    reports_back_button.pack(anchor="w", pady=(0, 5))

    list_title = ctk.CTkLabel(list_page, text="Incident Report Management", font=("Arial", 26, "bold"))
    list_title.pack(anchor="w")

    search_row = ctk.CTkFrame(list_page, fg_color="transparent")
    search_row.pack(fill="x", pady=(10, 0))

    search_entry = ctk.CTkEntry(
        search_row, placeholder_text="Search by incident number, worker, location, or description",
        height=38
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    search_entry.bind("<Return>", on_enter_key)

    search_button = GlassButton(
        search_row, text="SEARCH", width=100, height=38, command=load_list
    )
    search_button.pack(side="left", padx=(0, 10))

    reset_button = GlassButton(
        search_row, text="RESET", width=100, height=38, fg_color=EMBER_GRAY, command=reset_filters
    )
    reset_button.pack(side="left")

    filter_row = ctk.CTkFrame(list_page, fg_color="transparent")
    filter_row.pack(fill="x", pady=(10, 0))

    type_title = ctk.CTkLabel(filter_row, text="Type:", font=("Arial", 14, "bold"))
    type_title.pack(side="left", padx=(0, 5))

    type_filter_menu = ctk.CTkOptionMenu(
        filter_row, values=INCIDENT_TYPE_FILTERS, width=180, height=34, command=on_filter_change
    )
    type_filter_menu.set("All Types")
    type_filter_menu.pack(side="left", padx=(0, 20))

    status_title = ctk.CTkLabel(filter_row, text="Status:", font=("Arial", 14, "bold"))
    status_title.pack(side="left", padx=(0, 5))

    status_filter_menu = ctk.CTkOptionMenu(
        filter_row, values=INCIDENT_STATUS_FILTERS, width=160, height=34, command=on_filter_change
    )
    status_filter_menu.set("All Statuses")
    status_filter_menu.pack(side="left")

    count_label = ctk.CTkLabel(list_page, text="", font=("Arial", 14), text_color=TEXT_MUTED, anchor="w")
    count_label.pack(fill="x", pady=(8, 5))

    table_frame = ctk.CTkScrollableFrame(list_page, border_width=2)
    table_frame.pack(fill="both", expand=True)
    table_frame.grid_columnconfigure(3, weight=1)        # the Location column gets the extra space

    # ----- WIDGETS: DETAILS PAGE -----
    detail_back_button = GlassButton(
        detail_page, text="< BACK TO LIST", width=140, height=32, command=back_to_list
    )
    detail_back_button.pack(anchor="w", padx=10, pady=(5, 0))

    detail_title = ctk.CTkLabel(
        detail_page, text="Incident Report Details", font=("Arial", 26, "bold"), anchor="w"
    )
    detail_title.pack(fill="x", padx=10, pady=(10, 0))

    detail_number_label = ctk.CTkLabel(
        detail_page, text="", font=("Arial", 34, "bold"), text_color=ORANGE, anchor="w"
    )
    detail_number_label.pack(fill="x", padx=10)

    detail_status_label = ctk.CTkLabel(
        detail_page, text="", font=("Arial", 16, "bold"), anchor="w"
    )
    detail_status_label.pack(fill="x", padx=10, pady=(0, 10))

    detail_card = ctk.CTkFrame(detail_page, border_width=2, corner_radius=10)
    detail_card.pack(fill="x", padx=10)

    detail_info_label = ctk.CTkLabel(
        detail_card, text="", font=("Arial", 15), justify="left", anchor="w", wraplength=740
    )
    detail_info_label.pack(fill="x", padx=20, pady=20)

    def make_text_section(title_text):
        """Makes a title and an empty text label for one long text. It gives back the label."""
        section_title = ctk.CTkLabel(
            detail_page, text=title_text, font=("Arial", 16, "bold"), anchor="w"
        )
        section_title.pack(fill="x", padx=10, pady=(18, 0))

        section_label = ctk.CTkLabel(
            detail_page, text="", font=("Arial", 14), justify="left", anchor="w", wraplength=780
        )
        section_label.pack(fill="x", padx=10, pady=(3, 0))
        return section_label

    detail_description_label = make_text_section("Description")
    detail_actions_label = make_text_section("Actions Taken")
    detail_additional_label = make_text_section("Additional Information")

    detail_buttons_row = ctk.CTkFrame(detail_page, fg_color="transparent")
    detail_buttons_row.pack(fill="x", padx=10, pady=(25, 0))

    detail_edit_button = GlassButton(
        detail_buttons_row, text="EDIT REPORT", width=200, height=40,
        font=("Arial", 14, "bold"), fg_color=ORANGE, hover_color=ORANGE_DARK,
        command=start_edit
    )
    detail_edit_button.pack(side="left", padx=(0, 10))

    detail_delete_button = GlassButton(
        detail_buttons_row, text="", width=220, height=40,
        font=("Arial", 14, "bold"), command=toggle_delete
    )
    detail_delete_button.pack(side="left")

    detail_message_label = ctk.CTkLabel(
        detail_page, text="", font=("Arial", 14, "bold"), anchor="w", wraplength=780, justify="left"
    )
    detail_message_label.pack(fill="x", padx=10, pady=(10, 20))

    # ----- WIDGETS: EDIT PAGE -----
    def make_edit_label(text):
        """Makes a small bold title above a field."""
        label = ctk.CTkLabel(edit_page, text=text, font=("Arial", 14, "bold"), anchor="w")
        label.pack(fill="x", padx=40, pady=(12, 0))

    edit_title = ctk.CTkLabel(edit_page, text="Edit Incident Report", font=("Arial", 26, "bold"))
    edit_title.pack(pady=(10, 0))

    edit_number_label = ctk.CTkLabel(
        edit_page, text="", font=("Arial", 16, "bold"), text_color=ORANGE
    )
    edit_number_label.pack(pady=(0, 5))

    make_edit_label("Incident Type")
    edit_type_menu = ctk.CTkOptionMenu(edit_page, values=INCIDENT_TYPES, height=35)
    edit_type_menu.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Date of Incident")
    edit_date_row = ctk.CTkFrame(edit_page, fg_color="transparent")
    edit_date_row.pack(fill="x", padx=40, pady=(2, 0))

    edit_month_menu = ctk.CTkOptionMenu(edit_date_row, values=MONTHS, width=200, height=35)
    edit_month_menu.set("Month")
    edit_month_menu.pack(side="left", padx=(0, 10))

    edit_day_menu = ctk.CTkOptionMenu(edit_date_row, values=DAYS, width=100, height=35)
    edit_day_menu.set("Day")
    edit_day_menu.pack(side="left", padx=(0, 10))

    edit_year_menu = ctk.CTkOptionMenu(edit_date_row, values=years, width=120, height=35)
    edit_year_menu.set("Year")
    edit_year_menu.pack(side="left")

    make_edit_label("Time of Incident")
    edit_time_row = ctk.CTkFrame(edit_page, fg_color="transparent")
    edit_time_row.pack(fill="x", padx=40, pady=(2, 0))

    edit_hour_menu = ctk.CTkOptionMenu(edit_time_row, values=hours, width=100, height=35)
    edit_hour_menu.pack(side="left", padx=(0, 10))

    edit_minute_menu = ctk.CTkOptionMenu(edit_time_row, values=minutes, width=100, height=35)
    edit_minute_menu.pack(side="left", padx=(0, 10))

    edit_am_pm_menu = ctk.CTkOptionMenu(edit_time_row, values=["AM", "PM"], width=100, height=35)
    edit_am_pm_menu.pack(side="left")

    make_edit_label("Location")
    edit_location_entry = ctk.CTkEntry(
        edit_page, placeholder_text="Street, Barangay, City", height=35
    )
    edit_location_entry.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Personnel Involved (optional)")
    edit_personnel_entry = ctk.CTkEntry(
        edit_page, placeholder_text="Names of the firefighters involved", height=35
    )
    edit_personnel_entry.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Description")
    edit_description_box = ctk.CTkTextbox(edit_page, height=100, border_width=2)
    edit_description_box.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Actions Taken (optional)")
    edit_actions_box = ctk.CTkTextbox(edit_page, height=80, border_width=2)
    edit_actions_box.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Additional Information (optional)")
    edit_additional_box = ctk.CTkTextbox(edit_page, height=80, border_width=2)
    edit_additional_box.pack(fill="x", padx=40, pady=(2, 0))

    make_edit_label("Report Status")
    edit_status_menu = ctk.CTkOptionMenu(edit_page, values=INCIDENT_EDIT_STATUSES, height=35)
    edit_status_menu.set("Open")
    edit_status_menu.pack(fill="x", padx=40, pady=(2, 0))

    edit_message_label = ctk.CTkLabel(
        edit_page, text="", font=("Arial", 14, "bold"), text_color=BAD_RED
    )
    edit_message_label.pack(pady=(15, 0))

    edit_save_button = GlassButton(
        edit_page, text="SAVE CHANGES", height=42,
        font=("Arial", 15, "bold"), command=save_changes
    )
    edit_save_button.pack(fill="x", padx=40, pady=(10, 0))

    edit_cancel_button = GlassButton(
        edit_page, text="CANCEL", height=36, fg_color=EMBER_GRAY, command=cancel_edit
    )
    edit_cancel_button.pack(fill="x", padx=40, pady=(10, 30))

    load_list()

    return list_page, load_page


# =====================================================
# ADMIN PAGE: REPORTS
# =====================================================
REPORT_NAMES = ["Daily Attendance", "Duty Schedule", "Absence Records",
                "Leave Records", "Incident Reports", "Worker Activity History"]
REPORT_PERIODS = ["Today", "This Week", "This Month", "Custom Range"]

# The folder where saved reports go (a "reports" folder next to backend.py)
REPORTS_FOLDER = os.path.join(backend.BASE_FOLDER, "reports")


def create_reports_page(content, all_pages, open_incident_management):
    """Builds the Reports page inside the "content" area of the Admin screen.
    open_incident_management is the function that opens the Incident Report pages.
    It gives back two things: the page, and a function that reloads the report."""

    page = ctk.CTkFrame(content, fg_color="transparent")
    all_pages.append(page)

    this_year = datetime.now().year
    years = []
    for year in range(this_year + 1, this_year - 6, -1):      # next year, this year, and 5 before
        years.append(str(year))

    # This remembers the report on the screen, so SAVE AS CSV knows what to save
    last_report = {"report_name": "", "range_text": "", "summary": "",
                   "headers": [], "rows": [], "file_name": ""}

    def read_custom_date(month_box, day_box, year_box):
        """Reads three dropdowns and gives back a real date, or None if the date does not exist."""
        month_number = MONTHS.index(month_box.get()) + 1
        try:
            return datetime(int(year_box.get()), month_number, int(day_box.get())).date()
        except ValueError:
            return None

    def get_date_range():
        """Works out the first and last date of the report, from the Period dropdown.
        Gives back (first_date, last_date, error_text)."""
        today = datetime.now().date()
        period = period_menu.get()

        if period == "Today":
            return today, today, ""

        if period == "This Week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday, ""

        if period == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day, ""

        # Custom Range
        first_date = read_custom_date(from_month_menu, from_day_menu, from_year_menu)
        last_date = read_custom_date(to_month_menu, to_day_menu, to_year_menu)

        if first_date is None:
            return None, None, "The 'From' date does not exist. Please check the day."
        if last_date is None:
            return None, None, "The 'To' date does not exist. Please check the day."
        if first_date > last_date:
            return None, None, "The 'From' date cannot be after the 'To' date."

        return first_date, last_date, ""

    def describe_range(first_date, last_date):
        """Writes the period in words, like 'October 04, 2026 to October 10, 2026'."""
        if first_date == last_date:
            return first_date.strftime("%B %d, %Y")
        return first_date.strftime("%B %d, %Y") + " to " + last_date.strftime("%B %d, %Y")

    def update_custom_menus():
        """Keep date parts clickable so choosing one can switch to Custom Range."""
        for menu in custom_menus:
            menu.configure(state="normal")

    def build_table(headers, rows):
        """Draws the table: a header row, then one row for every report row."""
        for widget in table_frame.winfo_children():
            widget.destroy()

        # The columns in use share the width. The unused columns get no width.
        for column in range(10):
            if column < len(headers):
                table_frame.grid_columnconfigure(column, weight=1)
            else:
                table_frame.grid_columnconfigure(column, weight=0)

        for column in range(len(headers)):
            header_label = ctk.CTkLabel(
                table_frame, text=headers[column], font=("Arial", 13, "bold"), anchor="w"
            )
            header_label.grid(row=0, column=column, padx=8, pady=(5, 8), sticky="w")

        if len(rows) == 0:
            none_label = ctk.CTkLabel(
                table_frame, text="No records found for this report and period.",
                font=("Arial", 14), text_color=TEXT_MUTED
            )
            none_label.grid(row=1, column=0, columnspan=max(1, len(headers)),
                            padx=8, pady=20, sticky="w")
            return

        row_number = 1
        for row in rows:
            for column in range(len(row)):
                cell_label = ctk.CTkLabel(
                    table_frame, text=row[column], font=("Arial", 13),
                    anchor="w", justify="left", wraplength=160
                )
                cell_label.grid(row=row_number, column=column, padx=8, pady=4, sticky="w")
            row_number = row_number + 1

    def generate_report():
        """Reads the filters, builds the report, and shows it."""
        first_date, last_date, error_text = get_date_range()

        if error_text != "":
            message_label.configure(text=error_text, text_color=BAD_RED)
            return

        report_name = report_menu.get()
        headers, rows, summary = backend.get_report(
            report_name, first_date, last_date, search_entry.get().strip()
        )

        range_text = describe_range(first_date, last_date)

        # The name of the CSV file, like Daily_Attendance_2026-10-10.csv
        if first_date == last_date:
            date_part = first_date.strftime("%Y-%m-%d")
        else:
            date_part = first_date.strftime("%Y-%m-%d") + "_to_" + last_date.strftime("%Y-%m-%d")

        last_report["report_name"] = report_name
        last_report["range_text"] = range_text
        last_report["summary"] = summary
        last_report["headers"] = headers
        last_report["rows"] = rows
        last_report["file_name"] = report_name.replace(" ", "_") + "_" + date_part + ".csv"

        report_title_label.configure(text=report_name + " Report")
        range_label.configure(text=range_text)
        summary_label.configure(text=summary)

        if len(rows) > MAX_ROWS:
            message_label.configure(
                text=f"Showing the first {MAX_ROWS} of {len(rows)} rows. "
                     "SAVE AS CSV saves all of them.",
                text_color=TEXT_MUTED
            )
        else:
            message_label.configure(text="")

        build_table(headers, rows[:MAX_ROWS])

    def save_report():
        """Saves the report on the screen as a CSV file in the reports folder."""
        if last_report["report_name"] == "":
            message_label.configure(text="Please generate a report first.", text_color=BAD_RED)
            return

        if len(last_report["rows"]) == 0:
            message_label.configure(
                text="There are no records to save in this report.", text_color=BAD_RED
            )
            return

        try:
            os.makedirs(REPORTS_FOLDER, exist_ok=True)
            path = os.path.join(REPORTS_FOLDER, last_report["file_name"])

            # utf-8-sig makes Excel show every letter correctly
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([last_report["report_name"] + " Report"])
                writer.writerow([last_report["range_text"]])
                writer.writerow([last_report["summary"]])
                writer.writerow([])
                writer.writerow(last_report["headers"])
                for row in last_report["rows"]:
                    writer.writerow(row)
        except OSError:
            message_label.configure(
                text="Could not save the file. If it is open in Excel, close it and try again.",
                text_color=BAD_RED
            )
            return

        message_label.configure(
            text=f"Saved {len(last_report['rows'])} row(s) in the reports folder: "
                 f"{last_report['file_name']}",
            text_color=OK_GREEN
        )

    def on_filter_change(value):
        update_custom_menus()
        generate_report()

    def on_custom_date_part_change(value):
        """Choosing a From/To date part automatically activates Custom Range."""
        period_menu.set("Custom Range")
        update_custom_menus()
        generate_report()

    def on_enter_key(event):
        generate_report()

    def set_default_filters():
        """Puts every filter on its starting choice."""
        now = datetime.now()
        report_menu.set("Daily Attendance")
        period_menu.set("Today")
        search_entry.delete(0, "end")

        for menus in [(from_month_menu, from_day_menu, from_year_menu),
                      (to_month_menu, to_day_menu, to_year_menu)]:
            menus[0].set(MONTHS[now.month - 1])
            menus[1].set(str(now.day))
            menus[2].set(str(now.year))

        update_custom_menus()

    def load_page():
        """Shows the report with the newest data (it runs whenever the Admin opens this page)."""
        generate_report()

    title = ctk.CTkLabel(page, text="Reports", font=("Arial", 26, "bold"))
    title.pack(anchor="w")

    row_one = ctk.CTkFrame(page, fg_color="transparent")
    row_one.pack(fill="x", pady=(10, 0))

    report_title = ctk.CTkLabel(row_one, text="Report:", font=("Arial", 14, "bold"))
    report_title.pack(side="left", padx=(0, 5))

    report_menu = ctk.CTkOptionMenu(
        row_one, values=REPORT_NAMES, width=230, height=34, command=on_filter_change
    )
    report_menu.pack(side="left", padx=(0, 20))

    period_title = ctk.CTkLabel(row_one, text="Period:", font=("Arial", 14, "bold"))
    period_title.pack(side="left", padx=(0, 5))

    period_menu = ctk.CTkOptionMenu(
        row_one, values=REPORT_PERIODS, width=150, height=34, command=on_filter_change
    )
    period_menu.pack(side="left")

    row_two = ctk.CTkFrame(page, fg_color="transparent")
    row_two.pack(fill="x", pady=(10, 0))

    from_title = ctk.CTkLabel(row_two, text="From:", font=("Arial", 14, "bold"))
    from_title.pack(side="left", padx=(0, 5))

    from_month_menu = ctk.CTkOptionMenu(row_two, values=MONTHS, width=125, height=34)
    from_month_menu.pack(side="left", padx=(0, 5))

    from_day_menu = ctk.CTkOptionMenu(row_two, values=DAYS, width=70, height=34)
    from_day_menu.pack(side="left", padx=(0, 5))

    from_year_menu = ctk.CTkOptionMenu(row_two, values=years, width=90, height=34)
    from_year_menu.pack(side="left", padx=(0, 20))

    to_title = ctk.CTkLabel(row_two, text="To:", font=("Arial", 14, "bold"))
    to_title.pack(side="left", padx=(0, 5))

    to_month_menu = ctk.CTkOptionMenu(row_two, values=MONTHS, width=125, height=34)
    to_month_menu.pack(side="left", padx=(0, 5))

    to_day_menu = ctk.CTkOptionMenu(row_two, values=DAYS, width=70, height=34)
    to_day_menu.pack(side="left", padx=(0, 5))

    to_year_menu = ctk.CTkOptionMenu(row_two, values=years, width=90, height=34)
    to_year_menu.pack(side="left")

    # A list of the six dropdowns, so we can turn them on and off together
    custom_menus = [from_month_menu, from_day_menu, from_year_menu,
                    to_month_menu, to_day_menu, to_year_menu]

    row_three = ctk.CTkFrame(page, fg_color="transparent")
    row_three.pack(fill="x", pady=(10, 0))

    search_entry = ctk.CTkEntry(
        row_three, placeholder_text="Worker ID or name (optional)", height=38
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    search_entry.bind("<Return>", on_enter_key)

    generate_button = GlassButton(
        row_three, text="GENERATE REPORT", width=160, height=38,
        font=("Arial", 13, "bold"), command=generate_report
    )
    generate_button.pack(side="left", padx=(0, 10))

    save_button = GlassButton(
        row_three, text="SAVE AS CSV", width=130, height=38,
        font=("Arial", 13, "bold"), fg_color=GREEN_BTN, hover_color=GREEN_BTN_HOVER,
        command=save_report
    )
    save_button.pack(side="left", padx=(0, 10))

    manage_button = GlassButton(
        row_three, text="MANAGE INCIDENTS", width=160, height=38,
        font=("Arial", 13, "bold"), fg_color=ORANGE, hover_color=ORANGE_DARK,
        command=open_incident_management
    )
    manage_button.pack(side="left")

    report_title_label = ctk.CTkLabel(page, text="", font=("Arial", 20, "bold"), anchor="w")
    report_title_label.pack(fill="x", pady=(12, 0))

    range_label = ctk.CTkLabel(page, text="", font=("Arial", 14), text_color=TEXT_MUTED, anchor="w")
    range_label.pack(fill="x")

    summary_label = ctk.CTkLabel(
        page, text="", font=("Arial", 14, "bold"), anchor="w", justify="left", wraplength=800
    )
    summary_label.pack(fill="x", pady=(2, 0))

    message_label = ctk.CTkLabel(
        page, text="", font=("Arial", 14, "bold"), anchor="w", justify="left", wraplength=800
    )
    message_label.pack(fill="x", pady=(0, 5))

    table_frame = ctk.CTkScrollableFrame(page, border_width=2)
    table_frame.pack(fill="both", expand=True)

    set_default_filters()

    return page, load_page

# =====================================================================
# PASTE THIS WHOLE FILE AT THE VERY BOTTOM OF YOUR frontend.py
# (open frontend.py, press Ctrl+End to go to the last line, press Enter twice, then paste)
# You do NOT need to keep this line or the other "PASTE" lines. Start the paste from the
# line that says "# PART 3: THE WORKER SCREENS" if you like.
# =====================================================================


# =====================================================
# PART 3: THE WORKER SCREENS
# =====================================================

# ---------- Lists used by the Worker dropdowns ----------
# Hours (1 to 12) and minutes (00 to 59) for the incident time
HOURS = []
for hour in range(1, 13):
    HOURS.append(str(hour))

MINUTES = []
for minute in range(0, 60):
    MINUTES.append(f"{minute:02d}")    # :02d makes it 2 digits, like 05

AM_PM_LIST = ["AM", "PM"]

# The leave types a worker can choose from
LEAVE_TYPES = ["Sick Leave", "Vacation Leave", "Emergency Leave", "Official Leave", "Other"]


# ---------- Small helper functions for the date and time dropdowns ----------
def make_date_row(parent, label_text, year_list):
    """Builds a label and three dropdowns (Month, Day, Year).
    It gives back the three dropdowns so we can read them later."""
    label = ctk.CTkLabel(parent, text=label_text, font=("Arial", 14, "bold"), anchor="w")
    label.pack(fill="x", padx=60, pady=(15, 0))

    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=60, pady=(2, 0))

    month_box = ctk.CTkOptionMenu(row, values=MONTHS, width=200, height=35)
    month_box.pack(side="left", padx=(0, 10))

    day_box = ctk.CTkOptionMenu(row, values=DAYS, width=100, height=35)
    day_box.pack(side="left", padx=(0, 10))

    year_box = ctk.CTkOptionMenu(row, values=year_list, width=120, height=35)
    year_box.pack(side="left")

    return month_box, day_box, year_box


def make_time_row(parent, label_text):
    """Builds a label and three dropdowns (Hour, Minute, AM/PM).
    It gives back the three dropdowns so we can read them later."""
    label = ctk.CTkLabel(parent, text=label_text, font=("Arial", 14, "bold"), anchor="w")
    label.pack(fill="x", padx=60, pady=(15, 0))

    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=60, pady=(2, 0))

    hour_box = ctk.CTkOptionMenu(row, values=HOURS, width=100, height=35)
    hour_box.pack(side="left", padx=(0, 10))

    minute_box = ctk.CTkOptionMenu(row, values=MINUTES, width=100, height=35)
    minute_box.pack(side="left", padx=(0, 10))

    am_pm_box = ctk.CTkOptionMenu(row, values=AM_PM_LIST, width=100, height=35)
    am_pm_box.pack(side="left")

    return hour_box, minute_box, am_pm_box


def set_date_menus(month_box, day_box, year_box, date_value):
    """Sets the three dropdowns to a date (we use it to show today's date)."""
    month_box.set(MONTHS[date_value.month - 1])    # January is position 0, so we subtract 1
    day_box.set(str(date_value.day))
    year_box.set(str(date_value.year))


def set_time_menus(hour_box, minute_box, am_pm_box, time_value):
    """Sets the three dropdowns to a time (we use it to show the time right now)."""
    hour_12 = time_value.hour % 12          # 13 becomes 1, 12 becomes 0, ...
    if hour_12 == 0:
        hour_12 = 12                        # midnight and noon show as 12
    hour_box.set(str(hour_12))
    minute_box.set(f"{time_value.minute:02d}")
    if time_value.hour < 12:
        am_pm_box.set("AM")
    else:
        am_pm_box.set("PM")


def read_date(month_box, day_box, year_box):
    """Reads the three dropdowns and gives back a real date.
    It gives back None if the date does not exist (like February 30)."""
    month_number = MONTHS.index(month_box.get()) + 1
    try:
        return datetime(int(year_box.get()), month_number, int(day_box.get()))
    except ValueError:
        return None


def get_greeting():
    """Gives Good morning / Good afternoon / Good evening using the computer clock."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


def build_worker_screen(parent, go_back):
    """Builds all the Worker screens (Register, Login, Menu, and the forms).
    parent  = the main window
    go_back = the function that returns to the welcome screen
    It gives back three things: the screen, a function that opens the Login,
    and a function that opens the Registration.
    Everything below is indented 4 spaces because it is all inside this function."""

    screen = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=0)

    # This remembers WHO is logged in (it is empty until someone logs in).
    current_worker = {}
    menu_hook = {"callback": None}

    # ---------- Create the 9 screens ----------
    # Only ONE screen is shown at a time. We switch between them with buttons.
    register_screen = ctk.CTkScrollableFrame(screen, fg_color="transparent")
    success_screen = ctk.CTkFrame(screen, fg_color="transparent")
    login_screen = ctk.CTkFrame(screen, fg_color="transparent")
    menu_screen = ctk.CTkFrame(screen, fg_color="transparent")
    attendance_screen = ctk.CTkFrame(screen, fg_color="transparent")
    absence_screen = ctk.CTkScrollableFrame(screen, fg_color="transparent")
    leave_screen = ctk.CTkScrollableFrame(screen, fg_color="transparent")
    incident_screen = ctk.CTkScrollableFrame(screen, fg_color="transparent")
    duty_screen = ctk.CTkScrollableFrame(screen, fg_color="transparent")

    all_screens = [register_screen, success_screen, login_screen, menu_screen,
                   attendance_screen, absence_screen, leave_screen,
                   incident_screen, duty_screen]

    # ---------- Years for the dropdowns (they use the year it is today) ----------
    current_year = datetime.now().year
    leave_years = [str(current_year), str(current_year + 1)]           # this year and next year
    incident_years = [str(current_year), str(current_year - 1)]        # this year and last year
    absence_years = [str(current_year), str(current_year + 1)]

    # Years for the Birthday dropdown: workers from 18 to 70 years old (newest year first)
    register_years = []
    for year in range(current_year - 18, current_year - 70, -1):
        register_years.append(str(year))

    # ---------- Screen switching functions ----------
    def show_screen(screen_to_show):
        """Hides all screens, then shows the one we want."""
        for each_screen in all_screens:
            each_screen.pack_forget()
        screen_to_show.pack(fill="both", expand=True, padx=20, pady=10)

    def leave_worker_screens():
        """Forgets who was logged in and goes back to the welcome screen."""
        current_worker.clear()
        go_back()

    def go_to_register():
        show_screen(register_screen)

    def go_to_login():
        # Start the login screen clean: empty box, no old error message
        login_entry.delete(0, "end")
        login_error_label.configure(text="")
        show_screen(login_screen)

        if menu_hook["callback"] is not None:
            menu_hook["callback"]()
            return

    def go_to_menu():
        """Fills in the worker's name and ID on the menu screen, then shows it."""
        menu_greeting_label.configure(text=f"{get_greeting()}, {current_worker['first_name']}!")
        menu_name_label.configure(text="Welcome, " + current_worker["full_name"])
        menu_uid_label.configure(text="Worker ID: " + current_worker["uid"])
        menu_message_label.configure(text="")
        show_screen(menu_screen)

    def go_to_attendance():
        """Shows the Attendance screen with the worker's name and today's date."""
        attendance_name_label.configure(
            text=current_worker["full_name"] + "   (" + current_worker["uid"] + ")"
        )
        attendance_date_label.configure(text="Date: " + datetime.now().strftime("%B %d, %Y"))
        attendance_message_label.configure(text="")
        show_screen(attendance_screen)

    def go_to_absence():
        """Shows the Absence screen with a clean form (date set to today)."""
        now = datetime.now()
        absence_name_label.configure(
            text=current_worker["full_name"] + "   (" + current_worker["uid"] + ")"
        )
        absence_month_menu.set(MONTHS[now.month - 1])    # January is position 0, so we subtract 1
        absence_day_menu.set(str(now.day))
        absence_year_menu.set(str(now.year))
        absence_reason_entry.delete(0, "end")
        absence_explanation_box.delete("1.0", "end")
        absence_message_label.configure(text="")
        show_screen(absence_screen)

    def go_to_leave():
        """Shows the Leave screen with a clean form (both dates set to today)."""
        today = datetime.now()
        leave_name_label.configure(
            text=current_worker["full_name"] + "   (" + current_worker["uid"] + ")"
        )
        leave_type_menu.set("Select leave type")
        set_date_menus(start_month_menu, start_day_menu, start_year_menu, today)
        set_date_menus(end_month_menu, end_day_menu, end_year_menu, today)
        leave_reason_box.delete("1.0", "end")
        leave_message_label.configure(text="")
        refresh_leave_list()
        show_screen(leave_screen)

    def go_to_incident():
        """Shows the Incident Report screen with a clean form (date and time set to now)."""
        now = datetime.now()
        incident_name_label.configure(
            text=current_worker["full_name"] + "   (" + current_worker["uid"] + ")"
        )
        incident_type_menu.set("Select incident type")
        set_date_menus(incident_month_menu, incident_day_menu, incident_year_menu, now)
        set_time_menus(incident_hour_menu, incident_minute_menu, incident_am_pm_menu, now)
        incident_location_entry.delete(0, "end")
        incident_personnel_entry.delete(0, "end")
        incident_description_box.delete("1.0", "end")
        incident_actions_box.delete("1.0", "end")
        incident_additional_box.delete("1.0", "end")
        incident_message_label.configure(text="")
        refresh_incident_list()
        show_screen(incident_screen)

    def go_to_duty():
        """Shows the Duty screen with today's duty and the upcoming duties."""
        duty_name_label.configure(
            text=current_worker["full_name"] + "   (" + current_worker["uid"] + ")"
        )
        refresh_duty_screen()
        show_screen(duty_screen)

    def make_logo_label(logo_parent, width):
        """Makes a label with the logo picture. It gives back None if there is no logo file."""
        logo_picture = load_logo()
        if logo_picture is None:
            return None

        logo_ratio = logo_picture.height / logo_picture.width
        logo_image = ctk.CTkImage(light_image=logo_picture, dark_image=logo_picture,
                                  size=(width, int(width * logo_ratio)))
        logo_label = ctk.CTkLabel(logo_parent, text="", image=logo_image)
        logo_label.logo_reference = logo_image      # keeps the picture alive
        return logo_label

    # =====================================================
    # SCREEN: REGISTRATION COMPLETE (shows the new Worker ID)
    # =====================================================
    success_title = ctk.CTkLabel(
        success_screen,
        text="Registration Successful!",
        font=("Arial", 30, "bold"),
        text_color=OK_GREEN
    )
    success_title.pack(pady=(60, 5))

    success_subtitle = ctk.CTkLabel(
        success_screen,
        text="Your worker account has been successfully registered.",
        font=("Arial", 16),
        text_color=TEXT_MUTED
    )
    success_subtitle.pack(pady=(0, 25))

    success_uid_title = ctk.CTkLabel(
        success_screen,
        text="Your permanent Worker ID is:",
        font=("Arial", 18)
    )
    success_uid_title.pack()

    # This big label shows the new Worker ID (it is filled in after registration)
    success_uid_label = ctk.CTkLabel(
        success_screen,
        text="",
        font=("Arial", 56, "bold"),
        text_color=ORANGE
    )
    success_uid_label.pack(pady=(5, 20))

    success_note = ctk.CTkLabel(
        success_screen,
        text="Please keep this ID safe.\n"
             "You will use this ID to log in every time you report for duty.",
        font=("Arial", 16),
        justify="center"
    )
    success_note.pack(pady=(0, 30))

    success_login_button = GlassButton(
        success_screen,
        text="GO TO LOGIN",
        width=300,
        height=50,
        font=("Arial", 16, "bold"),
        command=go_to_login
    )
    success_login_button.pack(pady=(0, 10))

    success_welcome_button = GlassButton(
        success_screen,
        text="BACK TO WELCOME",
        width=300,
        height=40,
        fg_color=EMBER_GRAY,
        command=leave_worker_screens
    )
    success_welcome_button.pack()

    # =====================================================
    # SCREEN: LOGIN
    # =====================================================
    login_logo = make_logo_label(login_screen, 100)
    if login_logo is not None:
        login_logo.pack(pady=(40, 0))
        login_title_space = 10
    else:
        login_title_space = 90

    login_title = ctk.CTkLabel(login_screen, text="Worker Login", font=("Arial", 28, "bold"))
    login_title.pack(pady=(login_title_space, 5))

    login_subtitle = ctk.CTkLabel(
        login_screen,
        text="Enter your permanent Worker ID.",
        font=("Arial", 16),
        text_color=TEXT_MUTED
    )
    login_subtitle.pack(pady=(0, 25))

    login_label = ctk.CTkLabel(login_screen, text="Worker ID", font=("Arial", 14, "bold"))
    login_label.pack()

    login_entry = ctk.CTkEntry(
        login_screen,
        placeholder_text="UID-1234",
        width=300,
        height=45,
        font=("Arial", 18),
        justify="center"
    )
    login_entry.pack(pady=(5, 0))

    # This label shows login error messages in red
    login_error_label = ctk.CTkLabel(login_screen, text="", font=("Arial", 14), text_color=BAD_RED)
    login_error_label.pack(pady=(10, 0))

    def login_worker():
        """Runs when the LOGIN button is clicked. Checks the Worker ID."""

        # .strip() removes extra spaces, .upper() makes "uid-1234" into "UID-1234"
        uid = login_entry.get().strip().upper()

        # Check 1: the box cannot be empty
        if uid == "":
            login_error_label.configure(text="Please enter your Worker ID.")
            return

        # Check 2: look for this ID in the data
        worker = backend.get_worker(uid)

        if worker is None:
            login_error_label.configure(text="Worker ID not found. Please check your ID and try again.")
            return

        # worker is a group of values in this order:
        # (worker_uid, first_name, middle_name, surname, suffix, status)
        first_name = worker[1]
        surname = worker[3]
        suffix = worker[4]
        status = worker[5]

        # Check 3: the worker must be Active
        if status != "Active":
            login_error_label.configure(text="This Worker ID is inactive. Please contact the Admin.")
            return

        # Login is correct! Remember who logged in.
        # (A full name is built here: first name + surname + suffix if there is one.)
        full_name = first_name + " " + surname
        if suffix != "":
            full_name = full_name + " " + suffix

        current_worker["uid"] = worker[0]
        current_worker["first_name"] = first_name
        current_worker["full_name"] = full_name

        login_error_label.configure(text="")
        login_entry.delete(0, "end")

        # No popup! We just switch to the Main Menu screen in the same window.
        go_to_menu()

    login_entry.bind("<Return>", lambda event: login_worker())     # pressing Enter also logs in

    login_button = GlassButton(
        login_screen,
        text="LOGIN",
        width=300,
        height=45,
        font=("Arial", 16, "bold"),
        command=login_worker
    )
    login_button.pack(pady=(10, 10))

    login_back_button = GlassButton(
        login_screen,
        text="BACK",
        width=300,
        height=35,
        fg_color=EMBER_GRAY,
        command=leave_worker_screens
    )
    login_back_button.pack()

    # =====================================================
    # SCREEN: WORKER MAIN MENU
    # =====================================================
    menu_greeting_label = ctk.CTkLabel(menu_screen, text="", font=("Arial", 30, "bold"))
    menu_greeting_label.pack(pady=(40, 0))

    menu_name_label = ctk.CTkLabel(menu_screen, text="", font=("Arial", 18))
    menu_name_label.pack(pady=(5, 0))

    menu_uid_label = ctk.CTkLabel(menu_screen, text="", font=("Arial", 16), text_color=TEXT_MUTED)
    menu_uid_label.pack()

    menu_question_label = ctk.CTkLabel(
        menu_screen,
        text="What would you like to do?",
        font=("Arial", 18, "bold")
    )
    menu_question_label.pack(pady=(25, 10))

    def open_information():
        menu_message_label.configure(text="My Information will be added in a later step.")

    # The menu buttons sit in a grid: 2 columns, 3 rows
    menu_buttons_frame = ctk.CTkFrame(menu_screen, fg_color="transparent")
    menu_buttons_frame.pack()

    attendance_button = GlassButton(
        menu_buttons_frame, text="Attendance", width=260, height=55,
        font=("Arial", 16, "bold"), command=go_to_attendance
    )
    attendance_button.grid(row=0, column=0, padx=10, pady=8)

    absence_button = GlassButton(
        menu_buttons_frame, text="Absence", width=260, height=55,
        font=("Arial", 16, "bold"), command=go_to_absence
    )
    absence_button.grid(row=0, column=1, padx=10, pady=8)

    leave_button = GlassButton(
        menu_buttons_frame, text="Leave", width=260, height=55,
        font=("Arial", 16, "bold"), command=go_to_leave
    )
    leave_button.grid(row=1, column=0, padx=10, pady=8)

    incident_button = GlassButton(
        menu_buttons_frame, text="Incident Report", width=260, height=55,
        font=("Arial", 16, "bold"), command=go_to_incident
    )
    incident_button.grid(row=1, column=1, padx=10, pady=8)

    duty_button = GlassButton(
        menu_buttons_frame, text="My Duty / Shift", width=260, height=55,
        font=("Arial", 16, "bold"), command=go_to_duty
    )
    duty_button.grid(row=2, column=0, padx=10, pady=8)

    information_button = GlassButton(
        menu_buttons_frame, text="My Information", width=260, height=55,
        font=("Arial", 16, "bold"), command=open_information
    )
    information_button.grid(row=2, column=1, padx=10, pady=8)

    # This label shows small messages
    menu_message_label = ctk.CTkLabel(menu_screen, text="", font=("Arial", 14), text_color=TEXT_MUTED)
    menu_message_label.pack(pady=(10, 0))

    logout_button = GlassButton(
        menu_screen, text="LOGOUT", width=300, height=40,
        fg_color=EMBER_GRAY, command=leave_worker_screens
    )
    logout_button.pack(pady=(10, 0))

    # =====================================================
    # SCREEN: ATTENDANCE
    # =====================================================
    attendance_title = ctk.CTkLabel(attendance_screen, text="Attendance", font=("Arial", 28, "bold"))
    attendance_title.pack(pady=(60, 5))

    attendance_name_label = ctk.CTkLabel(attendance_screen, text="", font=("Arial", 18))
    attendance_name_label.pack()

    attendance_date_label = ctk.CTkLabel(
        attendance_screen, text="", font=("Arial", 16), text_color=TEXT_MUTED
    )
    attendance_date_label.pack(pady=(0, 25))

    def record_time_in():
        """Runs when TIME IN is clicked. Saves attendance, or says it was already saved."""
        uid = current_worker["uid"]

        # Get today's date and the current time from the computer clock
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")        # like 10/08/2026
        time_now = now.strftime("%I:%M %p")     # like 06:02 AM

        # Did this worker already record attendance today?
        existing = backend.get_attendance_today(uid, today)

        if existing is not None:
            # Yes. Do NOT save a second record. Just show a message.
            attendance_message_label.configure(
                text="Attendance Already Recorded\n\n"
                     "You have already recorded your attendance today.\n\n"
                     f"Time In: {existing[0]}",
                text_color=WARN_ORANGE
            )
            return

        # No. Save a new attendance record with the status Present.
        backend.save_time_in(uid, today, time_now, "Present")

        attendance_message_label.configure(
            text=f"{get_greeting()}, {current_worker['first_name']}!\n\n"
                 "Attendance Recorded!\n"
                 "You are marked PRESENT for today.\n\n"
                 f"Time In: {time_now}",
            text_color=OK_GREEN
        )

    time_in_button = GlassButton(
        attendance_screen,
        text="TIME IN",
        width=300,
        height=55,
        font=("Arial", 18, "bold"),
        command=record_time_in
    )
    time_in_button.pack(pady=(0, 10))

    def record_time_out():
        """Runs when TIME OUT is clicked. Saves the Time Out in the worker's attendance record."""
        uid = current_worker["uid"]

        now = datetime.now()
        today = now.strftime("%m/%d/%Y")                                 # like 10/09/2026
        yesterday = (now - timedelta(days=1)).strftime("%m/%d/%Y")       # like 10/08/2026
        time_now = now.strftime("%I:%M %p")                              # like 02:03 PM

        # Find the attendance record to close. Normally it is today's record.
        record_date = today
        existing = backend.get_attendance_record(uid, today)

        # A night shift starts yesterday at 10 PM and ends this morning.
        # So in the morning, if there is no record today, we look at yesterday's record.
        if existing is None and now.hour < 12:
            old_record = backend.get_attendance_record(uid, yesterday)
            if old_record is not None and old_record[1] == "":
                existing = old_record
                record_date = yesterday

        # No Time In was found at all
        if existing is None:
            attendance_message_label.configure(
                text="No Time In Found\n\nPlease click TIME IN first.",
                text_color=BAD_RED
            )
            return

        # Time Out was already recorded
        if existing[1] != "":
            attendance_message_label.configure(
                text="Time Out Already Recorded\n\n"
                     f"Time Out: {existing[1]}",
                text_color=WARN_ORANGE
            )
            return

        # Everything is correct! Save the Time Out.
        backend.save_time_out(uid, record_date, time_now)

        attendance_message_label.configure(
            text="Time Out Recorded\n\n"
                 f"Good job, {current_worker['first_name']}!\n\n"
                 f"Your Time Out was recorded at {time_now}.",
            text_color=OK_GREEN
        )

    time_out_button = GlassButton(
        attendance_screen,
        text="TIME OUT",
        width=300,
        height=55,
        font=("Arial", 18, "bold"),
        fg_color=ORANGE,
        hover_color=ORANGE_DARK,
        command=record_time_out
    )
    time_out_button.pack(pady=(0, 20))

    # This label shows the result message (green = saved, orange = already recorded)
    attendance_message_label = ctk.CTkLabel(
        attendance_screen, text="", font=("Arial", 16, "bold"), justify="center"
    )
    attendance_message_label.pack(pady=(0, 20))

    attendance_back_button = GlassButton(
        attendance_screen,
        text="BACK TO MENU",
        width=300,
        height=40,
        fg_color=EMBER_GRAY,
        command=go_to_menu
    )
    attendance_back_button.pack()

    # =====================================================
    # SCREEN: ABSENCE
    # =====================================================
    absence_title = ctk.CTkLabel(absence_screen, text="Report Absence", font=("Arial", 28, "bold"))
    absence_title.pack(pady=(20, 5))

    absence_name_label = ctk.CTkLabel(absence_screen, text="", font=("Arial", 16))
    absence_name_label.pack(pady=(0, 10))

    # ----- Date of absence: three dropdowns -----
    absence_date_title = ctk.CTkLabel(
        absence_screen, text="Date of Absence", font=("Arial", 14, "bold"), anchor="w"
    )
    absence_date_title.pack(fill="x", padx=60, pady=(10, 0))

    absence_date_frame = ctk.CTkFrame(absence_screen, fg_color="transparent")
    absence_date_frame.pack(fill="x", padx=60, pady=(2, 0))

    absence_month_menu = ctk.CTkOptionMenu(absence_date_frame, values=MONTHS, width=200, height=35)
    absence_month_menu.pack(side="left", padx=(0, 10))

    absence_day_menu = ctk.CTkOptionMenu(absence_date_frame, values=DAYS, width=100, height=35)
    absence_day_menu.pack(side="left", padx=(0, 10))

    absence_year_menu = ctk.CTkOptionMenu(absence_date_frame, values=absence_years, width=120, height=35)
    absence_year_menu.pack(side="left")

    # ----- Reason (short text, required) -----
    absence_reason_title = ctk.CTkLabel(
        absence_screen, text="Reason", font=("Arial", 14, "bold"), anchor="w"
    )
    absence_reason_title.pack(fill="x", padx=60, pady=(15, 0))

    absence_reason_entry = ctk.CTkEntry(
        absence_screen, placeholder_text="Enter reason for absence", height=35
    )
    absence_reason_entry.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Additional explanation (bigger box, optional) -----
    absence_explanation_title = ctk.CTkLabel(
        absence_screen, text="Additional Explanation (optional)", font=("Arial", 14, "bold"), anchor="w"
    )
    absence_explanation_title.pack(fill="x", padx=60, pady=(15, 0))

    absence_explanation_box = ctk.CTkTextbox(absence_screen, height=100, border_width=2)
    absence_explanation_box.pack(fill="x", padx=60, pady=(2, 0))

    # This label shows the result message
    absence_message_label = ctk.CTkLabel(
        absence_screen, text="", font=("Arial", 15, "bold"), justify="center"
    )
    absence_message_label.pack(pady=(15, 0))

    def submit_absence():
        """Runs when SUBMIT ABSENCE is clicked. Checks the form, then saves it."""
        uid = current_worker["uid"]

        reason = absence_reason_entry.get().strip()
        # In a textbox, "1.0" means "line 1, first character" and "end" means the last one
        explanation = absence_explanation_box.get("1.0", "end").strip()

        month_text = absence_month_menu.get()
        day_text = absence_day_menu.get()
        year_text = absence_year_menu.get()

        # Check 1: the reason cannot be empty
        if reason == "":
            absence_message_label.configure(
                text="Please enter the reason for your absence.", text_color=BAD_RED
            )
            return

        # Check 2: the date must really exist (for example, February 30 does not)
        month_number = MONTHS.index(month_text) + 1
        try:
            absence_day = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            absence_message_label.configure(
                text="That date does not exist. Please check the day.", text_color=BAD_RED
            )
            return

        absence_date = absence_day.strftime("%m/%d/%Y")     # like 10/08/2026

        # Check 3: did this worker already file an absence for this date?
        if backend.absence_exists(uid, absence_date):
            absence_message_label.configure(
                text="Absence Already Filed\n\nYou already submitted an absence report for this date.",
                text_color=WARN_ORANGE
            )
            return

        # Everything is correct! Save it. date_filed records when the report was sent.
        date_filed = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        backend.save_absence(uid, absence_date, reason, explanation, date_filed)

        absence_message_label.configure(
            text="Absence Report Submitted\n\nYour absence has been recorded and sent to the Admin.",
            text_color=OK_GREEN
        )

        # Empty the reason and explanation boxes
        absence_reason_entry.delete(0, "end")
        absence_explanation_box.delete("1.0", "end")

    absence_submit_button = GlassButton(
        absence_screen,
        text="SUBMIT ABSENCE",
        height=45,
        font=("Arial", 16, "bold"),
        command=submit_absence
    )
    absence_submit_button.pack(fill="x", padx=60, pady=(10, 0))

    absence_back_button = GlassButton(
        absence_screen,
        text="BACK TO MENU",
        height=35,
        fg_color=EMBER_GRAY,
        command=go_to_menu
    )
    absence_back_button.pack(fill="x", padx=60, pady=(10, 20))

    # =====================================================
    # SCREEN: LEAVE
    # =====================================================
    leave_title = ctk.CTkLabel(leave_screen, text="File Leave Request", font=("Arial", 28, "bold"))
    leave_title.pack(pady=(20, 5))

    leave_name_label = ctk.CTkLabel(leave_screen, text="", font=("Arial", 16))
    leave_name_label.pack(pady=(0, 10))

    # ----- Leave type: one dropdown -----
    leave_type_title = ctk.CTkLabel(
        leave_screen, text="Leave Type", font=("Arial", 14, "bold"), anchor="w"
    )
    leave_type_title.pack(fill="x", padx=60, pady=(10, 0))

    leave_type_menu = ctk.CTkOptionMenu(leave_screen, values=LEAVE_TYPES, height=35)
    leave_type_menu.set("Select leave type")
    leave_type_menu.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Start date and End date: three dropdowns each -----
    # make_date_row gives back three dropdowns, and we keep them in three names.
    start_month_menu, start_day_menu, start_year_menu = make_date_row(
        leave_screen, "Start Date", leave_years
    )
    end_month_menu, end_day_menu, end_year_menu = make_date_row(
        leave_screen, "End Date", leave_years
    )

    # ----- Reason (bigger box, required) -----
    leave_reason_title = ctk.CTkLabel(
        leave_screen, text="Reason", font=("Arial", 14, "bold"), anchor="w"
    )
    leave_reason_title.pack(fill="x", padx=60, pady=(15, 0))

    leave_reason_box = ctk.CTkTextbox(leave_screen, height=90, border_width=2)
    leave_reason_box.pack(fill="x", padx=60, pady=(2, 0))

    # This label shows the result message
    leave_message_label = ctk.CTkLabel(
        leave_screen, text="", font=("Arial", 15, "bold"), justify="center"
    )
    leave_message_label.pack(pady=(15, 0))

    # This label shows the worker's last 5 leave requests (placed at the bottom of this screen)
    leave_list_label = ctk.CTkLabel(
        leave_screen, text="", font=("Arial", 14), justify="left", anchor="w"
    )

    def refresh_leave_list():
        """Reloads the worker's last 5 leave requests and shows them."""
        rows = backend.get_worker_leaves(current_worker["uid"])

        if len(rows) == 0:
            leave_list_label.configure(text="No leave requests yet.")
            return

        lines = []
        for row in rows:
            # row = (leave_type, start_date, end_date, status)
            lines.append(f"{row[0]}:  {row[1]} to {row[2]}   -   {row[3]}")

        # "\n".join puts each line on its own row
        leave_list_label.configure(text="\n".join(lines))

    def submit_leave():
        """Runs when SUBMIT LEAVE REQUEST is clicked. Checks the form, then saves it."""
        uid = current_worker["uid"]

        leave_type = leave_type_menu.get()
        reason = leave_reason_box.get("1.0", "end").strip()

        # Check 1: a leave type must be chosen
        if leave_type == "Select leave type":
            leave_message_label.configure(text="Please select a leave type.", text_color=BAD_RED)
            return

        # Check 2: both dates must really exist (read_date gives back None if they do not)
        start_date = read_date(start_month_menu, start_day_menu, start_year_menu)
        end_date = read_date(end_month_menu, end_day_menu, end_year_menu)

        if start_date is None:
            leave_message_label.configure(
                text="The start date does not exist. Please check the day.", text_color=BAD_RED
            )
            return

        if end_date is None:
            leave_message_label.configure(
                text="The end date does not exist. Please check the day.", text_color=BAD_RED
            )
            return

        # Check 3: the end date cannot be before the start date
        if end_date < start_date:
            leave_message_label.configure(
                text="The end date cannot be before the start date.", text_color=BAD_RED
            )
            return

        # Check 4: the reason cannot be empty
        if reason == "":
            leave_message_label.configure(
                text="Please enter the reason for your leave.", text_color=BAD_RED
            )
            return

        # Turn the dates into text like 10/08/2026 so we can save them
        start_text = start_date.strftime("%m/%d/%Y")
        end_text = end_date.strftime("%m/%d/%Y")

        # Check 5: did this worker already send the same request?
        if backend.leave_exists(uid, start_text, end_text):
            leave_message_label.configure(
                text="Leave Request Already Sent\n\n"
                     "You already have a request for these dates.",
                text_color=WARN_ORANGE
            )
            return

        # Everything is correct! Save it. date_filed records when the request was sent.
        date_filed = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        backend.save_leave(uid, leave_type, start_text, end_text, reason, date_filed)

        leave_message_label.configure(
            text="Leave Request Submitted\n\nYour request has been sent to the Admin for review.",
            text_color=OK_GREEN
        )

        # Empty the reason box and update the list at the bottom
        leave_reason_box.delete("1.0", "end")
        refresh_leave_list()

    leave_submit_button = GlassButton(
        leave_screen,
        text="SUBMIT LEAVE REQUEST",
        height=45,
        font=("Arial", 16, "bold"),
        command=submit_leave
    )
    leave_submit_button.pack(fill="x", padx=60, pady=(10, 0))

    leave_back_button = GlassButton(
        leave_screen,
        text="BACK TO MENU",
        height=35,
        fg_color=EMBER_GRAY,
        command=go_to_menu
    )
    leave_back_button.pack(fill="x", padx=60, pady=(10, 0))

    leave_list_title = ctk.CTkLabel(
        leave_screen, text="My Recent Leave Requests", font=("Arial", 16, "bold"), anchor="w"
    )
    leave_list_title.pack(fill="x", padx=60, pady=(25, 0))

    leave_list_label.pack(fill="x", padx=60, pady=(5, 30))

    # =====================================================
    # SCREEN: INCIDENT REPORT
    # =====================================================
    incident_title = ctk.CTkLabel(incident_screen, text="Incident Report", font=("Arial", 28, "bold"))
    incident_title.pack(pady=(20, 5))

    incident_name_label = ctk.CTkLabel(incident_screen, text="", font=("Arial", 16))
    incident_name_label.pack(pady=(0, 10))

    # ----- Incident type: one dropdown -----
    incident_type_title = ctk.CTkLabel(
        incident_screen, text="Incident Type", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_type_title.pack(fill="x", padx=60, pady=(10, 0))

    incident_type_menu = ctk.CTkOptionMenu(incident_screen, values=INCIDENT_TYPES, height=35)
    incident_type_menu.set("Select incident type")
    incident_type_menu.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Date and time of the incident -----
    incident_month_menu, incident_day_menu, incident_year_menu = make_date_row(
        incident_screen, "Date of Incident", incident_years
    )
    incident_hour_menu, incident_minute_menu, incident_am_pm_menu = make_time_row(
        incident_screen, "Time of Incident"
    )

    # ----- Location (short text, required) -----
    incident_location_title = ctk.CTkLabel(
        incident_screen, text="Location", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_location_title.pack(fill="x", padx=60, pady=(15, 0))

    incident_location_entry = ctk.CTkEntry(
        incident_screen, placeholder_text="Street, Barangay, City", height=35
    )
    incident_location_entry.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Personnel involved (short text, optional) -----
    incident_personnel_title = ctk.CTkLabel(
        incident_screen, text="Personnel Involved (optional)", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_personnel_title.pack(fill="x", padx=60, pady=(15, 0))

    incident_personnel_entry = ctk.CTkEntry(
        incident_screen, placeholder_text="Names of the firefighters involved", height=35
    )
    incident_personnel_entry.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Description (bigger box, required) -----
    incident_description_title = ctk.CTkLabel(
        incident_screen, text="Description", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_description_title.pack(fill="x", padx=60, pady=(15, 0))

    incident_description_box = ctk.CTkTextbox(incident_screen, height=100, border_width=2)
    incident_description_box.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Actions taken (bigger box, optional) -----
    incident_actions_title = ctk.CTkLabel(
        incident_screen, text="Actions Taken (optional)", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_actions_title.pack(fill="x", padx=60, pady=(15, 0))

    incident_actions_box = ctk.CTkTextbox(incident_screen, height=80, border_width=2)
    incident_actions_box.pack(fill="x", padx=60, pady=(2, 0))

    # ----- Additional information (bigger box, optional) -----
    incident_additional_title = ctk.CTkLabel(
        incident_screen, text="Additional Information (optional)", font=("Arial", 14, "bold"), anchor="w"
    )
    incident_additional_title.pack(fill="x", padx=60, pady=(15, 0))

    incident_additional_box = ctk.CTkTextbox(incident_screen, height=80, border_width=2)
    incident_additional_box.pack(fill="x", padx=60, pady=(2, 0))

    # This label shows the result message
    incident_message_label = ctk.CTkLabel(
        incident_screen, text="", font=("Arial", 15, "bold"), justify="center"
    )
    incident_message_label.pack(pady=(15, 0))

    # This label shows the worker's last 5 incident reports (placed at the bottom of this screen)
    incident_list_label = ctk.CTkLabel(
        incident_screen, text="", font=("Arial", 14), justify="left", anchor="w"
    )

    def refresh_incident_list():
        """Reloads the worker's last 5 incident reports and shows them."""
        rows = backend.get_worker_incidents(current_worker["uid"])

        if len(rows) == 0:
            incident_list_label.configure(text="No incident reports yet.")
            return

        lines = []
        for row in rows:
            # row = (incident_id, incident_type, date_time, status)
            incident_number = f"INC-{row[0]:04d}"      # 1 becomes INC-0001
            lines.append(f"{incident_number}:  {row[1]}  -  {row[2]}  -  {row[3]}")

        incident_list_label.configure(text="\n".join(lines))

    def submit_incident():
        """Runs when SUBMIT INCIDENT REPORT is clicked. Checks the form, then saves it."""
        uid = current_worker["uid"]

        incident_type = incident_type_menu.get()
        location = incident_location_entry.get().strip()
        personnel = incident_personnel_entry.get().strip()
        description = incident_description_box.get("1.0", "end").strip()
        actions = incident_actions_box.get("1.0", "end").strip()
        additional = incident_additional_box.get("1.0", "end").strip()

        # Check 1: an incident type must be chosen
        if incident_type == "Select incident type":
            incident_message_label.configure(text="Please select an incident type.", text_color=BAD_RED)
            return

        # Check 2: the date must really exist (read_date gives back None if it does not)
        incident_day = read_date(incident_month_menu, incident_day_menu, incident_year_menu)

        if incident_day is None:
            incident_message_label.configure(
                text="That date does not exist. Please check the day.", text_color=BAD_RED
            )
            return

        # Check 3: build the full date and time, and make sure it is not in the future
        hour_number = int(incident_hour_menu.get())
        minute_number = int(incident_minute_menu.get())
        am_pm = incident_am_pm_menu.get()

        # Change the 12-hour clock into the 24-hour clock that Python uses
        if am_pm == "PM" and hour_number != 12:
            hour_number = hour_number + 12
        if am_pm == "AM" and hour_number == 12:
            hour_number = 0

        incident_moment = incident_day.replace(hour=hour_number, minute=minute_number)

        if incident_moment > datetime.now():
            incident_message_label.configure(
                text="The incident date and time cannot be in the future.", text_color=BAD_RED
            )
            return

        # Check 4: the location cannot be empty
        if location == "":
            incident_message_label.configure(
                text="Please enter the location of the incident.", text_color=BAD_RED
            )
            return

        # Check 5: the description cannot be empty
        if description == "":
            incident_message_label.configure(
                text="Please enter a description of the incident.", text_color=BAD_RED
            )
            return

        # Everything is correct! Save it.
        date_time_text = incident_moment.strftime("%m/%d/%Y %I:%M %p")      # like 10/08/2026 06:15 AM
        date_reported = datetime.now().strftime("%m/%d/%Y %I:%M %p")        # when the report was sent

        new_id = backend.save_incident(
            uid, date_time_text, incident_type, location, personnel,
            description, actions, additional, date_reported
        )

        incident_message_label.configure(
            text=f"Incident Report Submitted Successfully.\n\n"
                 f"Report number: INC-{new_id:04d}\n"
                 "Your report has been sent to the Admin.",
            text_color=OK_GREEN
        )

        # Empty the boxes and update the list at the bottom
        incident_location_entry.delete(0, "end")
        incident_personnel_entry.delete(0, "end")
        incident_description_box.delete("1.0", "end")
        incident_actions_box.delete("1.0", "end")
        incident_additional_box.delete("1.0", "end")
        refresh_incident_list()

    incident_submit_button = GlassButton(
        incident_screen,
        text="SUBMIT INCIDENT REPORT",
        height=45,
        font=("Arial", 16, "bold"),
        command=submit_incident
    )
    incident_submit_button.pack(fill="x", padx=60, pady=(10, 0))

    incident_back_button = GlassButton(
        incident_screen,
        text="BACK TO MENU",
        height=35,
        fg_color=EMBER_GRAY,
        command=go_to_menu
    )
    incident_back_button.pack(fill="x", padx=60, pady=(10, 0))

    incident_list_title = ctk.CTkLabel(
        incident_screen, text="My Recent Incident Reports", font=("Arial", 16, "bold"), anchor="w"
    )
    incident_list_title.pack(fill="x", padx=60, pady=(25, 0))

    incident_list_label.pack(fill="x", padx=60, pady=(5, 30))

    # =====================================================
    # SCREEN: MY DUTY / SHIFT
    # =====================================================
    duty_title = ctk.CTkLabel(duty_screen, text="My Duty / Shift", font=("Arial", 28, "bold"))
    duty_title.pack(pady=(20, 5))

    duty_name_label = ctk.CTkLabel(duty_screen, text="", font=("Arial", 16))
    duty_name_label.pack(pady=(0, 10))

    # ----- Today's duty (shown inside a box) -----
    duty_today_title = ctk.CTkLabel(
        duty_screen, text="Today's Duty", font=("Arial", 18, "bold"), anchor="w"
    )
    duty_today_title.pack(fill="x", padx=60, pady=(10, 0))

    duty_card = ctk.CTkFrame(duty_screen, border_width=2, corner_radius=10)
    duty_card.pack(fill="x", padx=60, pady=(5, 0))

    duty_today_label = ctk.CTkLabel(
        duty_card, text="", font=("Arial", 18), justify="left", anchor="w"
    )
    duty_today_label.pack(fill="x", padx=20, pady=20)

    # ----- Upcoming duties -----
    duty_upcoming_title = ctk.CTkLabel(
        duty_screen, text="Upcoming Duties", font=("Arial", 18, "bold"), anchor="w"
    )
    duty_upcoming_title.pack(fill="x", padx=60, pady=(30, 0))

    duty_upcoming_label = ctk.CTkLabel(
        duty_screen, text="", font=("Arial", 15), justify="left", anchor="w"
    )
    duty_upcoming_label.pack(fill="x", padx=60, pady=(5, 0))

    def refresh_duty_screen():
        """Loads the worker's duties, then shows today's duty and the next 5 upcoming ones."""
        now = datetime.now()
        today_text = now.strftime("%m/%d/%Y")           # like 10/09/2026

        rows = backend.get_worker_duties(current_worker["uid"])

        today_duty = None       # stays None if there is no duty today
        upcoming = []           # a list of (date, duty) for future days

        for row in rows:
            # row = (duty_date, shift, start_time, end_time, assignment)
            duty_day = datetime.strptime(row[0], "%m/%d/%Y")    # turn the text into a real date

            if row[0] == today_text:
                today_duty = row
            elif duty_day.date() > now.date():
                upcoming.append((duty_day, row))

        # ----- Today's duty -----
        if today_duty is None:
            duty_today_label.configure(text="No duty assigned for today.", text_color=TEXT_MUTED)
        else:
            duty_today_label.configure(
                text=f"Worker: {current_worker['full_name']}\n"
                     f"Date: {now.strftime('%B %d, %Y')}\n"
                     f"Shift: {today_duty[1]}\n"
                     f"Time: {today_duty[2]} - {today_duty[3]}\n"
                     f"Assignment: {today_duty[4]}",
                text_color=TEXT
            )

        # ----- Upcoming duties -----
        if len(upcoming) == 0:
            duty_upcoming_label.configure(text="No upcoming duties yet.")
            return

        upcoming.sort(key=lambda item: item[0])         # puts the dates in order, nearest day first

        lines = []
        for duty_day, row in upcoming[:5]:      # [:5] means only the first 5
            lines.append(
                f"{duty_day.strftime('%B %d, %Y')}:  {row[1]} ({row[2]} - {row[3]})  -  {row[4]}"
            )

        duty_upcoming_label.configure(text="\n".join(lines))

    duty_back_button = GlassButton(
        duty_screen,
        text="BACK TO MENU",
        height=35,
        fg_color=EMBER_GRAY,
        command=go_to_menu
    )
    duty_back_button.pack(fill="x", padx=60, pady=(30, 20))

    # =====================================================
    # SCREEN: REGISTRATION
    # =====================================================
    register_back_button = GlassButton(
        register_screen,
        text="< BACK",
        width=100,
        height=30,
        fg_color=EMBER_GRAY,
        command=leave_worker_screens
    )
    register_back_button.pack(anchor="w", padx=40, pady=(10, 0))

    form_title = ctk.CTkLabel(register_screen, text="Worker Registration", font=("Arial", 24, "bold"))
    form_title.pack(pady=(10, 0))

    form_subtitle = ctk.CTkLabel(
        register_screen,
        text="Fill in all fields. Suffix is optional.",
        font=("Arial", 14),
        text_color=TEXT_MUTED
    )
    form_subtitle.pack()

    # ---------- Helper function ----------
    # This function makes one label + one text box, so we don't repeat code.
    def make_field(field_parent, label_text, placeholder):
        label = ctk.CTkLabel(field_parent, text=label_text, font=("Arial", 14, "bold"), anchor="w")
        label.pack(fill="x", padx=40, pady=(10, 0))

        # placeholder_text shows gray guide text that disappears when you type
        entry = ctk.CTkEntry(field_parent, placeholder_text=placeholder, height=35)
        entry.pack(fill="x", padx=40, pady=(2, 0))
        return entry

    # ---------- Form fields ----------
    first_name_entry = make_field(register_screen, "First Name", "Enter your first name")
    middle_name_entry = make_field(register_screen, "Middle Name", "Enter your middle name")
    surname_entry = make_field(register_screen, "Surname", "Enter your surname")
    suffix_entry = make_field(register_screen, "Suffix (optional)", "Jr., Sr., III")
    address_entry = make_field(register_screen, "Address", "Street, City, Province")

    # Birthday: three dropdowns (Month, Day, Year)
    birthday_label = ctk.CTkLabel(register_screen, text="Birthday", font=("Arial", 14, "bold"), anchor="w")
    birthday_label.pack(fill="x", padx=40, pady=(10, 0))

    birthday_frame = ctk.CTkFrame(register_screen, fg_color="transparent")
    birthday_frame.pack(fill="x", padx=40, pady=(2, 0))

    month_menu = ctk.CTkOptionMenu(birthday_frame, values=MONTHS, width=200, height=35)
    month_menu.set("Month")            # the text shown before choosing
    month_menu.pack(side="left", padx=(0, 10))

    day_menu = ctk.CTkOptionMenu(birthday_frame, values=DAYS, width=120, height=35)
    day_menu.set("Day")
    day_menu.pack(side="left", padx=(0, 10))

    year_menu = ctk.CTkOptionMenu(birthday_frame, values=register_years, width=140, height=35)
    year_menu.set("Year")
    year_menu.pack(side="left")

    # Sex: two radio buttons, so the worker only clicks (no typing)
    sex_label = ctk.CTkLabel(register_screen, text="Sex", font=("Arial", 14, "bold"), anchor="w")
    sex_label.pack(fill="x", padx=40, pady=(10, 0))

    sex_variable = ctk.StringVar(value="")   # remembers which button is chosen

    sex_frame = ctk.CTkFrame(register_screen, fg_color="transparent")
    sex_frame.pack(fill="x", padx=40, pady=(2, 0))

    male_button = ctk.CTkRadioButton(sex_frame, text="Male", variable=sex_variable, value="Male")
    male_button.pack(side="left", padx=(0, 30))

    female_button = ctk.CTkRadioButton(sex_frame, text="Female", variable=sex_variable, value="Female")
    female_button.pack(side="left")

    phone_entry = make_field(register_screen, "Phone Number", "09XXXXXXXXX")

    # This label will show error messages in red
    error_label = ctk.CTkLabel(register_screen, text="", font=("Arial", 14), text_color=BAD_RED)
    error_label.pack(pady=(15, 0))

    # ---------- Functions ----------
    def clear_form():
        """Empties every field so the form is ready for the next person."""
        first_name_entry.delete(0, "end")
        middle_name_entry.delete(0, "end")
        surname_entry.delete(0, "end")
        suffix_entry.delete(0, "end")
        address_entry.delete(0, "end")
        phone_entry.delete(0, "end")
        month_menu.set("Month")
        day_menu.set("Day")
        year_menu.set("Year")
        sex_variable.set("")
        error_label.configure(text="")

    def register_worker():
        """Runs when the Register button is clicked. Checks the form first."""

        # .get() reads what was typed. .strip() removes extra spaces at the start/end.
        first_name = first_name_entry.get().strip()
        middle_name = middle_name_entry.get().strip()
        surname = surname_entry.get().strip()
        suffix = suffix_entry.get().strip()        # may be empty, that is allowed
        address = address_entry.get().strip()
        sex = sex_variable.get()
        phone = phone_entry.get().strip()

        # The three birthday dropdowns
        month_text = month_menu.get()
        day_text = day_menu.get()
        year_text = year_menu.get()

        # Check 1: required text fields cannot be empty (suffix is not required)
        if (first_name == "" or middle_name == "" or surname == "" or
                address == "" or phone == ""):
            error_label.configure(text="Please complete all required fields.")
            return    # "return" stops the function here

        # Check 2: the worker must choose a Month, a Day, and a Year
        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            error_label.configure(text="Please select your complete birthday (Month, Day, and Year).")
            return

        # Check 3: the date must really exist (for example, February 30 does not)
        month_number = MONTHS.index(month_text) + 1     # January =  1, February = 2, ...
        try:
            birthday = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            error_label.configure(text="That birthday date does not exist. Please check the day.")
            return

        # Turn the birthday into text like 05/20/2000 so we can save it
        birthday_text = birthday.strftime("%m/%d/%Y")

        # Check 4: sex must be selected
        if sex == "":
            error_label.configure(text="Please select your sex (Male or Female).")
            return

        # Check 5: phone must be 11 digits and start with 09
        if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
            error_label.configure(text="Please enter a valid phone number like 09123456789.")
            return

        # Everything is correct! Clear the error and make a new Worker ID.
        error_label.configure(text="")
        new_uid = backend.generate_unique_uid()

        # Save the worker
        saved = backend.save_worker(
            new_uid, first_name, middle_name, surname, suffix,
            address, birthday_text, sex, phone
        )

        if not saved:
            error_label.configure(text="Something went wrong while saving. Please try again.")
            return

        # No popups! Show the new Worker ID on the Registration Complete screen.
        clear_form()
        success_uid_label.configure(text=new_uid)
        show_screen(success_screen)

    # ---------- Register button ----------
    register_button = GlassButton(
        register_screen,
        text="REGISTER",
        height=40,
        font=("Arial", 16, "bold"),
        command=register_worker      # runs register_worker when clicked
    )
    register_button.pack(padx=40, pady=(10, 30), fill="x")

    def open_login():
        """Called by main.py when the Login button is clicked."""
        current_worker.clear()
        go_to_login()

    def open_register():
        """Called by main.py when the Register button is clicked."""
        clear_form()
        go_to_register()

    def open_form(worker, which):
        """Opens one long form for a worker who is already logged in on the welcome card."""
        current_worker.clear()
        current_worker.update(worker)
        forms = {"absence": go_to_absence, "leave": go_to_leave,
                 "incident": go_to_incident, "duty": go_to_duty}
        forms[which]()

    def set_menu_hook(function):
        menu_hook["callback"] = function

    return screen, open_login, open_register, open_form, set_menu_hook


# =====================================================================
# PASTE THIS WHOLE FILE AT THE VERY BOTTOM OF YOUR frontend.py
# (open frontend.py, press Ctrl+End to go to the last line, press Enter twice, then paste)
# =====================================================================


# =====================================================
# GLASS PAGES: DUTY / SHIFTS, LEAVE / ABSENCE, and REPORTS
# These three functions have the SAME names as the old pages. Python always uses the
# LAST function with a given name, so these new glass pages replace the old ones.
# =====================================================
SHIFTS = ["Morning", "Afternoon", "Night"]
DUTY_PERIODS = ["Today", "This Week", "This Month", "All Dates"]

# Used to put the shifts of one day in order
SHIFT_ORDER = {"Morning": 1, "Afternoon": 2, "Night": 3}

LEAVE_FILTERS = ["Pending", "Approved", "Rejected", "All Statuses"]
ABSENCE_DATE_MODES = ["All Dates", "Today", "This Week", "This Month"]

REPORT_NAMES = ["Daily Attendance", "Duty Schedule", "Absence Records",
                "Leave Records", "Incident Reports", "Worker Activity History"]
REPORT_PERIODS = ["Today", "This Week", "This Month", "Custom Range"]

# The folder where saved reports go (a "reports" folder next to backend.py)
REPORTS_FOLDER = os.path.join(backend.BASE_FOLDER, "reports")

# How wide each column is, compared to the others (a bigger number = a wider column)
LEAVE_COLUMNS = [("Worker", 2.0), ("Leave Type", 1.7), ("Dates", 1.4), ("Reason", 2.8),
                 ("Status", 1.1), ("", 1.1), ("", 1.1)]
ABSENCE_COLUMNS = [("Worker", 2.0), ("Absence Date", 1.3), ("Reason", 2.0),
                   ("Explanation", 3.2), ("Filed", 1.7)]

# The column widths of each report on the Reports page (same order as the report's headings)
REPORT_COLUMN_WEIGHTS = {
    "Daily Attendance": [1.1, 1.0, 2.2, 1.0, 1.0, 1.0],
    "Duty Schedule": [1.1, 1.0, 2.0, 1.0, 1.6, 1.6],
    "Absence Records": [1.0, 1.0, 1.8, 1.8, 2.2, 1.7],
    "Leave Records": [1.0, 1.8, 1.3, 1.0, 1.0, 1.8, 1.0, 1.6],
    "Incident Reports": [1.0, 1.7, 1.4, 2.0, 2.2, 1.0],
    "Worker Activity History": [1.0, 2.2, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
}


def shorten(text, limit):
    """Cuts a long text short with '...' so it never spills into the next row."""
    text = str(text).replace("\n", " ")
    if len(text) > limit:
        return text[:limit - 3] + "..."
    return text


class GlassWeightedTablePage(GlassTablePage):
    """Like GlassTablePage, but the columns share the width by 'weights'.
    So the table fits the window when you make it bigger or smaller.
    columns = [("Heading", weight), ...]  (a bigger weight = a wider column)"""

    def __init__(self, parent, screen, page_title, columns, row_height=46):
        GlassTablePage.__init__(self, parent, screen, page_title,
                                [(heading, None) for heading, weight in columns], row_height)
        self.column_weights = columns

    def set_columns(self, columns):
        """Changes the columns. Empty the rows first, then call redraw()."""
        self.column_weights = columns

    def paint(self, canvas, W, H):
        usable = max(300, W - 88)                    # the width inside the glass panel
        total = 0
        for heading, weight in self.column_weights:
            total = total + weight

        self.table_columns = []
        for heading, weight in self.column_weights:
            self.table_columns.append((heading, int(usable * weight / total)))

        GlassTablePage.paint(self, canvas, W, H)


# =====================================================
# ADMIN PAGE: DUTY / SHIFTS (glass)
# =====================================================
def create_duty_page(content, all_pages, screen=None):
    """Builds the Duty / Shifts page (a glass table).
    The Admin assigns a shift to a worker for a date, and can edit or remove it.
    It gives back two things: the page, and a function that reloads it."""

    if screen is None:
        screen = content.master.master          # content -> body -> the Admin screen

    page = GlassWeightedTablePage(
        content, screen, "Duty / Shifts",
        [("Date", 1.4), ("Worker ID", 1.0), ("Name", 2.2), ("Shift", 1.0),
         ("Time", 1.2), ("Assignment", 1.5), ("Worker report", 1.0), ("Result", 0.9),
         ("", 0.45), ("", 0.45), ("", 0.65), ("", 0.8)]
    )
    all_pages.append(page)

    this_year = datetime.now().year
    years = []
    for year in range(this_year - 1, this_year + 2):      # last year, this year, next year
        years.append(str(year))

    # This remembers which row is waiting for a second click on REMOVE
    pending = {"id": ""}

    message_label = CanvasText()
    count_label = CanvasText()

    def get_worker_labels():
        """Makes a list like 'UID-8337  -  alrie madula jr' for every Active worker."""
        labels = []
        for worker in backend.read_records("employees"):
            if worker["status"] == "Active":
                labels.append(worker["worker_uid"] + "  -  " + backend.make_name(worker))
        return labels

    def refresh_worker_menu():
        """Fills the Worker dropdown with the newest list of Active workers."""
        labels = get_worker_labels()
        if len(labels) == 0:
            labels = ["No workers registered"]

        worker_menu.configure(values=labels)
        if worker_menu.get() not in labels:
            worker_menu.set(labels[0])

    def read_form_date():
        """Reads the three date dropdowns. Gives back a real date, or None if it does not exist."""
        month_number = MONTHS.index(month_menu.get()) + 1
        try:
            return datetime(int(year_menu.get()), month_number, int(day_menu.get())).date()
        except ValueError:
            return None

    def set_entry_text(entry, text):
        """Puts text in a text box (it empties the box first)."""
        entry.delete(0, "end")
        entry.insert(0, text)

    def assign_duty():
        """Runs when ASSIGN DUTY is clicked. Checks the form, then saves the duty."""
        label = worker_menu.get()

        # Check 1: there must be a worker to choose
        if label == "No workers registered":
            message_label.configure(text="There are no workers yet. Register a worker first.",
                                    text_color=BAD_RED)
            return

        uid = label.split()[0]                 # the Worker ID is the first word, like UID-8337
        worker = backend.get_full_worker(uid)

        if worker is None:
            message_label.configure(text="That worker was not found.", text_color=BAD_RED)
            return

        # Check 2: only Active workers can be given a duty
        if worker["status"] != "Active":
            message_label.configure(
                text="This worker is Inactive. Reactivate the worker first.", text_color=BAD_RED
            )
            return

        # Check 3: the date must really exist (for example, February 30 does not)
        duty_day = read_form_date()
        if duty_day is None:
            message_label.configure(text="That date does not exist. Please check the day.",
                                    text_color=BAD_RED)
            return

        shift = shift_menu.get()
        assignment = assignment_entry.get().strip()
        if assignment == "":
            assignment = "Fire Station"        # the starting choice

        date_text = duty_day.strftime("%m/%d/%Y")          # like 10/14/2026
        full_name = backend.make_name(worker)

        # Does this worker already have a duty on this date? (save_duty will replace it)
        old_shift = ""
        for record in backend.read_records("duty_schedule"):
            if record["worker_uid"] == uid and record["duty_date"] == date_text:
                old_shift = record["shift"]

        backend.save_duty(uid, date_text, shift, assignment)

        nice_date = duty_day.strftime("%B %d, %Y")
        if old_shift == "":
            text = f"Duty assigned: {full_name} ({uid}) - {shift} shift on {nice_date}."
        else:
            text = (f"Duty updated: {full_name} ({uid}) now has the {shift} shift on "
                    f"{nice_date}. It replaced the {old_shift} shift.")

        pending["id"] = ""
        load_list()
        message_label.configure(text=text, text_color=OK_GREEN)

    def edit_duty(duty_id):
        """Fills the form with a duty, so the Admin can change it and click ASSIGN DUTY."""
        for record in backend.read_records("duty_schedule"):
            if record["duty_id"] != str(duty_id):
                continue

            worker = backend.get_full_worker(record["worker_uid"])
            if worker is None:
                full_name = "(unknown worker)"
            else:
                full_name = backend.make_name(worker)

            worker_menu.set(record["worker_uid"] + "  -  " + full_name)
            shift_menu.set(record["shift"])
            set_entry_text(assignment_entry, record["assignment"])

            try:
                day = datetime.strptime(record["duty_date"], "%m/%d/%Y")
                month_menu.set(MONTHS[day.month - 1])
                day_menu.set(str(day.day))
                year_menu.set(str(day.year))
            except ValueError:
                pass

            pending["id"] = ""
            load_list(keep_scroll=True)
            message_label.configure(
                text="Editing this duty. Change what you need, then click ASSIGN DUTY.",
                text_color=TEXT_MUTED
            )
            return

    def remove_duty(duty_id):
        """First click: asks to confirm. Second click on the same row: removes the duty."""
        if pending["id"] != str(duty_id):
            pending["id"] = str(duty_id)
            load_list(keep_scroll=True)
            message_label.configure(
                text="Click CONFIRM on the same row to remove this duty.", text_color=WARN_ORANGE
            )
            return

        # Keep every duty EXCEPT this one
        kept = []
        for record in backend.read_records("duty_schedule"):
            if record["duty_id"] != str(duty_id):
                kept.append(record)
        backend.write_records("duty_schedule", kept)

        pending["id"] = ""
        load_list(keep_scroll=True)
        message_label.configure(text="Duty removed.", text_color=BAD_RED)

    def review_duty(duty_id, decision):
        """Record the Admin's decision on a worker's completion report."""
        try:
            saved = backend.verify_duty_report(duty_id, decision)
        except ValueError as exc:
            message_label.configure(text=str(exc), text_color=BAD_RED)
            return
        if not saved:
            message_label.configure(text="This report is no longer pending.", text_color=BAD_RED)
            load_list(keep_scroll=True)
            return
        load_list(keep_scroll=True)
        result = "verified" if decision == "verify" else "marked Unfinish"
        message_label.configure(text=f"Duty report {result}.", text_color=OK_GREEN)

    def get_range():
        """Works out the first and last date to show, from the Period dropdown.
        Both are None for "All Dates"."""
        today = datetime.now().date()
        mode = period_menu.get()

        if mode == "Today":
            return today, today

        if mode == "This Week":
            monday = today - timedelta(days=today.weekday())    # weekday(): Monday is 0
            sunday = monday + timedelta(days=6)
            return monday, sunday

        if mode == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day

        return None, None        # All Dates

    def sort_key(record):
        """Tells Python how to order the duties: by date, then shift, then Worker ID."""
        return (record["day"], SHIFT_ORDER.get(record["shift"], 9), record["worker_uid"])

    def load_list(keep_scroll=False):
        """Reads the filters, finds the duties, and shows them in the glass table."""
        first_date, last_date = get_range()
        words = search_entry.get().strip().lower().split()

        # A list of every worker's name, so we can show names next to the IDs
        names = {}
        for worker in backend.read_records("employees"):
            names[worker["worker_uid"]] = backend.make_name(worker)

        found = []
        for record in backend.read_records("duty_schedule"):
            try:
                day = datetime.strptime(record["duty_date"], "%m/%d/%Y").date()
            except ValueError:
                continue                                    # skip a damaged date

            if first_date is not None and (day < first_date or day > last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            everything = (uid + " " + full_name).lower()

            found_all = True
            for word in words:
                if word not in everything:
                    found_all = False
            if not found_all:
                continue

            record["full_name"] = full_name
            record["day"] = day
            found.append(record)

        found.sort(key=sort_key)

        count_label.configure(text=f"Found {len(found)} duty record(s)")

        rows = []
        for record in found:
            if pending["id"] == record["duty_id"]:
                remove_text = "CONFIRM"
                remove_color = RED
            else:
                remove_text = "REMOVE"
                remove_color = EMBER_GRAY

            worker_report = record.get("worker_report", "")
            verification = record.get("verification_status", "")
            completion = record.get("completion_status", "")
            result_text = completion or ("Pending" if verification == "Pending" else "—")
            if verification == "Pending":
                verify_cell = ("button", "✓", GREEN_BTN,
                               partial(review_duty, record["duty_id"], "verify"))
                reject_cell = ("button", "X", RED,
                               partial(review_duty, record["duty_id"], "unfinish"))
            else:
                verify_cell = "✓" if completion == "Done" else ""
                reject_cell = "X" if completion == "Unfinish" and verification == "Rejected" else ""

            # partial(...) makes each button remember WHICH duty it belongs to
            rows.append([
                record["day"].strftime("%m/%d/%Y (%a)"),
                ("text", record["worker_uid"], WHITE, True),
                record["full_name"],
                ("text", record["shift"], WHITE, True),
                record["start_time"] + " - " + record["end_time"],
                shorten(record["assignment"], 40),
                worker_report or "—",
                result_text,
                verify_cell,
                reject_cell,
                ("button", "EDIT", ORANGE, partial(edit_duty, record["duty_id"])),
                ("button", remove_text, remove_color, partial(remove_duty, record["duty_id"])),
            ])

        page.empty_text = "No duties found for this period."
        page.set_rows(rows, keep_scroll)

    def on_filter_change(value):
        """Runs when the Period dropdown changes."""
        pending["id"] = ""
        message_label.configure(text="")
        load_list()

    def on_enter_key(event):
        pending["id"] = ""
        load_list()

    def reset_filters():
        search_entry.delete(0, "end")
        period_menu.set("This Week")
        pending["id"] = ""
        message_label.configure(text="")
        load_list()

    def set_default_form():
        """Puts the form back to its starting choices (today, Morning shift)."""
        now = datetime.now()
        month_menu.set(MONTHS[now.month - 1])
        day_menu.set(str(now.day))
        year_menu.set(str(now.year))
        shift_menu.set("Morning")
        assignment_entry.delete(0, "end")

    def load_page():
        """Shows the newest data (it runs whenever the Admin opens this page)."""
        refresh_worker_menu()
        pending["id"] = ""
        load_list()

    # ----- The form and the filters (real widgets that sit on top of the glass) -----
    worker_menu = ctk.CTkOptionMenu(page, values=["No workers registered"], width=300, height=34)
    month_menu = ctk.CTkOptionMenu(page, values=MONTHS, width=125, height=34)
    day_menu = ctk.CTkOptionMenu(page, values=DAYS, width=70, height=34)
    year_menu = ctk.CTkOptionMenu(page, values=years, width=90, height=34)
    shift_menu = ctk.CTkOptionMenu(page, values=SHIFTS, width=130, height=34)
    assignment_entry = ctk.CTkEntry(page, placeholder_text="Fire Station", height=34)

    period_menu = ctk.CTkOptionMenu(page, values=DUTY_PERIODS, width=130, height=34,
                                    command=on_filter_change)
    period_menu.set("This Week")
    search_entry = ctk.CTkEntry(page, placeholder_text="Search by Worker ID or name", height=34)
    search_entry.bind("<Return>", on_enter_key)

    page.controls = [
        {"height": 34, "items": [
            ("text", "Worker:", 75),
            ("widget", worker_menu, 300),
            ("text", "Date:", 50),
            ("widget", month_menu, 125),
            ("widget", day_menu, 70),
            ("widget", year_menu, 90),
        ]},
        {"height": 34, "items": [
            ("text", "Shift:", 55),
            ("widget", shift_menu, 130),
            ("text", "Assignment:", 105),
            ("widget", assignment_entry, None),
            ("button", "ASSIGN DUTY", 150, RED, assign_duty),
        ]},
        {"height": 22, "items": [("info", message_label, WHITE)]},
        {"height": 34, "items": [
            ("text", "Period:", 65),
            ("widget", period_menu, 130),
            ("widget", search_entry, None),
            ("button", "SEARCH", 90, RED, load_list),
            ("button", "RESET", 90, EMBER_GRAY, reset_filters),
        ]},
        {"height": 22, "items": [("info", count_label, TEXT_MUTED)]},
    ]

    set_default_form()

    return page, load_page


# =====================================================
# ADMIN PAGE: LEAVE / ABSENCE (glass, with two tabs)
# =====================================================
def create_leave_page(content, all_pages, screen=None):
    """Builds the Leave / Absence page (a glass table with two tabs).
    It gives back two things: the page, and a function that reloads it."""

    if screen is None:
        screen = content.master.master          # content -> body -> the Admin screen

    page = GlassWeightedTablePage(content, screen, "Leave / Absence Management",
                                  LEAVE_COLUMNS, row_height=58)
    all_pages.append(page)

    # tab = which tab is open ("leave" or "absence").  pending = the number on the tab button.
    state = {"tab": "leave", "pending": 0}

    leave_count_label = CanvasText()
    leave_message_label = CanvasText()
    absence_count_label = CanvasText()

    def build_controls():
        """Sets the tools above the table for the tab that is open."""
        if state["tab"] == "leave":
            leave_tint = RED
            absence_tint = EMBER_GRAY
        else:
            leave_tint = EMBER_GRAY
            absence_tint = RED

        tabs_row = {"height": 38, "items": [
            ("button", f"LEAVE REQUESTS  ({state['pending']} pending)", 290, leave_tint, show_leave_tab),
            ("button", "ABSENCE REPORTS", 230, absence_tint, show_absence_tab),
        ]}

        if state["tab"] == "leave":
            page.set_columns(LEAVE_COLUMNS)
            page.controls = [
                tabs_row,
                {"height": 38, "items": [
                    ("widget", leave_search_entry, None),
                    ("text", "Status:", 70),
                    ("widget", leave_filter_menu, 140),
                    ("button", "SEARCH", 100, RED, load_leave_list),
                    ("button", "RESET", 100, EMBER_GRAY, reset_leave_filters),
                ]},
                {"height": 22, "items": [("info", leave_count_label, TEXT_MUTED)]},
                {"height": 22, "items": [("info", leave_message_label, WHITE)]},
            ]
        else:
            page.set_columns(ABSENCE_COLUMNS)
            page.controls = [
                tabs_row,
                {"height": 38, "items": [
                    ("widget", absence_search_entry, None),
                    ("text", "Date:", 55),
                    ("widget", absence_date_menu, 140),
                    ("button", "SEARCH", 100, RED, load_absence_list),
                    ("button", "RESET", 100, EMBER_GRAY, reset_absence_filters),
                ]},
                {"height": 22, "items": [("info", absence_count_label, TEXT_MUTED)]},
            ]

    def show_leave_tab():
        """Opens the Leave Requests tab."""
        state["tab"] = "leave"
        page.set_rows([])                 # empty the rows first (the columns are about to change)
        build_controls()
        page.redraw()
        load_leave_list()

    def show_absence_tab():
        """Opens the Absence Reports tab."""
        state["tab"] = "absence"
        page.set_rows([])
        build_controls()
        page.redraw()
        load_absence_list()

    def update_pending_number():
        """Shows the newest number of pending requests on the tab button."""
        pending_total = backend.count_pending_leaves()
        if pending_total != state["pending"]:
            state["pending"] = pending_total
            build_controls()
            page.redraw()

    # ---------------- LEAVE REQUESTS ----------------
    def decide(leave_id, new_status):
        """Runs when APPROVE, REJECT, or UNDO is clicked. It saves right away."""
        backend.update_leave_status(leave_id, new_status)
        load_leave_list(keep_scroll=True)

        if new_status == "Approved":
            leave_message_label.configure(text="Leave request approved.", text_color=OK_GREEN)
        elif new_status == "Rejected":
            leave_message_label.configure(text="Leave request rejected.", text_color=BAD_RED)
        else:
            leave_message_label.configure(
                text="Leave request set back to Pending.", text_color=WARN_ORANGE
            )

    def load_leave_list(keep_scroll=False):
        """Reads the filters, finds the leave requests, and shows them in the table."""
        update_pending_number()

        records = backend.get_leave_requests(
            leave_filter_menu.get(), leave_search_entry.get().strip()
        )
        leave_count_label.configure(text=f"Found {len(records)} request(s)")

        rows = []
        for record in records:
            filed_day = record["date_filed"][:10]       # keeps only the date, like 10/09/2026

            if record["status"] == "Approved":
                status_color = OK_GREEN
            elif record["status"] == "Rejected":
                status_color = BAD_RED
            else:
                status_color = WARN_ORANGE

            # partial(...) makes each button remember WHICH request it belongs to
            if record["status"] == "Pending":
                first_button = ("button", "APPROVE", GREEN_BTN,
                                partial(decide, record["leave_id"], "Approved"))
                second_button = ("button", "REJECT", RED,
                                 partial(decide, record["leave_id"], "Rejected"))
            else:
                first_button = ("button", "UNDO", EMBER_GRAY,
                                partial(decide, record["leave_id"], "Pending"))
                second_button = ""

            rows.append([
                ("text", record["worker_uid"] + "\n" + record["full_name"], WHITE, True),
                record["leave_type"] + "\nFiled: " + filed_day,
                record["start_date"] + "\nto " + record["end_date"],
                shorten(show_or_dash(record["reason"]), 80),
                ("text", record["status"], status_color, True),
                first_button,
                second_button,
            ])

        page.empty_text = "No leave requests found."
        page.set_rows(rows, keep_scroll)

    def on_leave_filter_change(value):
        load_leave_list()

    def on_leave_enter_key(event):
        load_leave_list()

    def reset_leave_filters():
        leave_search_entry.delete(0, "end")
        leave_filter_menu.set("Pending")
        load_leave_list()

    # ---------------- ABSENCE REPORTS ----------------
    def get_absence_range():
        """Works out the first and last date to show, from the Date dropdown.
        Both are None for "All Dates"."""
        today = datetime.now().date()
        mode = absence_date_menu.get()

        if mode == "Today":
            return today, today

        if mode == "This Week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday

        if mode == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day

        return None, None        # All Dates

    def load_absence_list(keep_scroll=False):
        """Reads the filters, finds the absence reports, and shows them in the table."""
        update_pending_number()

        first_date, last_date = get_absence_range()
        records = backend.get_absence_reports(
            first_date, last_date, absence_search_entry.get().strip()
        )
        absence_count_label.configure(text=f"Found {len(records)} report(s)")

        rows = []
        for record in records:
            rows.append([
                ("text", record["worker_uid"] + "\n" + record["full_name"], WHITE, True),
                record["absence_date"],
                shorten(record["reason"], 50),
                shorten(show_or_dash(record["explanation"]), 90),
                record["date_filed"].replace(" ", "\n", 1),
            ])

        page.empty_text = "No absence reports found."
        page.set_rows(rows, keep_scroll)

    def on_absence_filter_change(value):
        load_absence_list()

    def on_absence_enter_key(event):
        load_absence_list()

    def reset_absence_filters():
        absence_search_entry.delete(0, "end")
        absence_date_menu.set("All Dates")
        load_absence_list()

    def load_page():
        """Reloads the tab that is open (it runs whenever the Admin opens this page)."""
        if state["tab"] == "leave":
            load_leave_list()
        else:
            load_absence_list()

    # ----- The search boxes and dropdowns (real widgets that sit on top of the glass) -----
    leave_search_entry = ctk.CTkEntry(page, placeholder_text="Search by Worker ID or name", height=38)
    leave_search_entry.bind("<Return>", on_leave_enter_key)

    leave_filter_menu = ctk.CTkOptionMenu(page, values=LEAVE_FILTERS, width=140, height=34,
                                          command=on_leave_filter_change)
    leave_filter_menu.set("Pending")

    absence_search_entry = ctk.CTkEntry(page, placeholder_text="Search by Worker ID or name", height=38)
    absence_search_entry.bind("<Return>", on_absence_enter_key)

    absence_date_menu = ctk.CTkOptionMenu(page, values=ABSENCE_DATE_MODES, width=140, height=34,
                                          command=on_absence_filter_change)
    absence_date_menu.set("All Dates")

    # Start on the Leave Requests tab
    state["pending"] = backend.count_pending_leaves()
    build_controls()

    return page, load_page


# =====================================================
# ADMIN PAGE: REPORTS (glass)
# =====================================================
def create_reports_page(content, all_pages, open_incident_management, screen=None):
    """Builds the Reports page (a glass table).
    open_incident_management is the function that opens the Incident Report pages.
    It gives back two things: the page, and a function that reloads the report."""

    if screen is None:
        screen = content.master.master          # content -> body -> the Admin screen

    page = GlassWeightedTablePage(
        content, screen, "Reports",
        [("Date", 1.1), ("Worker ID", 1.0), ("Name", 2.2), ("Time In", 1.0),
         ("Time Out", 1.0), ("Status", 1.0)],
        row_height=52
    )
    all_pages.append(page)

    this_year = datetime.now().year
    years = []
    for year in range(this_year + 1, this_year - 6, -1):      # next year, this year, and 5 before
        years.append(str(year))

    # This remembers the report on the screen, so SAVE AS CSV knows what to save
    last_report = {"report_name": "", "range_text": "", "summary": "",
                   "headers": [], "rows": [], "file_name": ""}

    heading_label = CanvasText()
    summary_label = CanvasText()
    message_label = CanvasText()

    def read_custom_date(month_box, day_box, year_box):
        """Reads three dropdowns and gives back a real date, or None if the date does not exist."""
        month_number = MONTHS.index(month_box.get()) + 1
        try:
            return datetime(int(year_box.get()), month_number, int(day_box.get())).date()
        except ValueError:
            return None

    def get_date_range():
        """Works out the first and last date of the report, from the Period dropdown.
        Gives back (first_date, last_date, error_text)."""
        today = datetime.now().date()
        period = period_menu.get()

        if period == "Today":
            return today, today, ""

        if period == "This Week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday, ""

        if period == "This Month":
            first_day = today.replace(day=1)
            if today.month == 12:
                first_of_next = today.replace(year=today.year + 1, month=1, day=1)
            else:
                first_of_next = today.replace(month=today.month + 1, day=1)
            last_day = first_of_next - timedelta(days=1)
            return first_day, last_day, ""

        # Custom Range
        first_date = read_custom_date(from_month_menu, from_day_menu, from_year_menu)
        last_date = read_custom_date(to_month_menu, to_day_menu, to_year_menu)

        if first_date is None:
            return None, None, "The 'From' date does not exist. Please check the day."
        if last_date is None:
            return None, None, "The 'To' date does not exist. Please check the day."
        if first_date > last_date:
            return None, None, "The 'From' date cannot be after the 'To' date."

        return first_date, last_date, ""

    def describe_range(first_date, last_date):
        """Writes the period in words, like 'October 04, 2026 to October 10, 2026'."""
        if first_date == last_date:
            return first_date.strftime("%B %d, %Y")
        return first_date.strftime("%B %d, %Y") + " to " + last_date.strftime("%B %d, %Y")

    def update_custom_menus():
        """Keep date parts clickable so choosing one can switch to Custom Range."""
        for menu in custom_menus:
            menu.configure(state="normal")

    def generate_report():
        """Reads the filters, builds the report, and shows it in the glass table."""
        first_date, last_date, error_text = get_date_range()

        if error_text != "":
            message_label.configure(text=error_text, text_color=BAD_RED)
            return

        report_name = report_menu.get()
        headers, rows, summary = backend.get_report(
            report_name, first_date, last_date, search_entry.get().strip()
        )

        range_text = describe_range(first_date, last_date)

        # The name of the CSV file, like Daily_Attendance_2026-10-10.csv
        if first_date == last_date:
            date_part = first_date.strftime("%Y-%m-%d")
        else:
            date_part = first_date.strftime("%Y-%m-%d") + "_to_" + last_date.strftime("%Y-%m-%d")

        # Remember this report, so SAVE AS CSV can save it
        last_report["report_name"] = report_name
        last_report["range_text"] = range_text
        last_report["summary"] = summary
        last_report["headers"] = headers
        last_report["rows"] = rows
        last_report["file_name"] = report_name.replace(" ", "_") + "_" + date_part + ".csv"

        heading_label.configure(text=report_name + " Report   -   " + range_text, text_color=AMBER)
        summary_label.configure(text=summary, text_color=WHITE)
        message_label.configure(text="", text_color=WHITE)

        # Each report has its own columns. Empty the rows first, then change the columns.
        weights = REPORT_COLUMN_WEIGHTS.get(report_name)
        if weights is None or len(weights) != len(headers):
            weights = [1.0] * len(headers)

        columns = []
        for position in range(len(headers)):
            columns.append((headers[position], weights[position]))

        page.set_rows([])
        page.set_columns(columns)
        page.redraw()

        table_rows = []
        for row in rows:
            cells = []
            for value in row:
                cells.append(shorten(value, 70))
            table_rows.append(cells)

        page.empty_text = "No records found for this report and period."
        page.set_rows(table_rows)

    def save_report():
        """Saves the report on the screen as a CSV file in the reports folder."""
        if last_report["report_name"] == "":
            message_label.configure(text="Please generate a report first.", text_color=BAD_RED)
            return

        if len(last_report["rows"]) == 0:
            message_label.configure(
                text="There are no records to save in this report.", text_color=BAD_RED
            )
            return

        try:
            os.makedirs(REPORTS_FOLDER, exist_ok=True)
            path = os.path.join(REPORTS_FOLDER, last_report["file_name"])

            # utf-8-sig makes Excel show every letter correctly
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([last_report["report_name"] + " Report"])
                writer.writerow([last_report["range_text"]])
                writer.writerow([last_report["summary"]])
                writer.writerow([])
                writer.writerow(last_report["headers"])
                for row in last_report["rows"]:
                    writer.writerow(row)
        except OSError:
            message_label.configure(
                text="Could not save the file. If it is open in Excel, close it and try again.",
                text_color=BAD_RED
            )
            return

        message_label.configure(
            text=f"Saved {len(last_report['rows'])} row(s) in the reports folder: "
                 f"{last_report['file_name']}",
            text_color=OK_GREEN
        )

    def on_filter_change(value):
        update_custom_menus()
        generate_report()

    def on_custom_date_part_change(value):
        """Choosing a From/To date part automatically activates Custom Range."""
        period_menu.set("Custom Range")
        update_custom_menus()
        generate_report()

    def on_enter_key(event):
        generate_report()

    def set_default_filters():
        """Puts every filter on its starting choice."""
        now = datetime.now()
        report_menu.set("Daily Attendance")
        period_menu.set("Today")
        search_entry.delete(0, "end")

        for menus in [(from_month_menu, from_day_menu, from_year_menu),
                      (to_month_menu, to_day_menu, to_year_menu)]:
            menus[0].set(MONTHS[now.month - 1])
            menus[1].set(str(now.day))
            menus[2].set(str(now.year))

        update_custom_menus()

    def load_page():
        """Shows the report with the newest data (it runs whenever the Admin opens this page)."""
        generate_report()

    # ----- The dropdowns, the search box and the buttons -----
    report_menu = ctk.CTkOptionMenu(page, values=REPORT_NAMES, width=230, height=34,
                                    command=on_filter_change)
    period_menu = ctk.CTkOptionMenu(page, values=REPORT_PERIODS, width=150, height=34,
                                    command=on_filter_change)

    from_month_menu = ctk.CTkOptionMenu(page, values=MONTHS, width=125, height=34,
                                        command=on_custom_date_part_change)
    from_day_menu = ctk.CTkOptionMenu(page, values=DAYS, width=70, height=34,
                                      command=on_custom_date_part_change)
    from_year_menu = ctk.CTkOptionMenu(page, values=years, width=90, height=34,
                                       command=on_custom_date_part_change)
    to_month_menu = ctk.CTkOptionMenu(page, values=MONTHS, width=125, height=34,
                                      command=on_custom_date_part_change)
    to_day_menu = ctk.CTkOptionMenu(page, values=DAYS, width=70, height=34,
                                    command=on_custom_date_part_change)
    to_year_menu = ctk.CTkOptionMenu(page, values=years, width=90, height=34,
                                     command=on_custom_date_part_change)

    # A list of the six dropdowns, so we can turn them on and off together
    custom_menus = [from_month_menu, from_day_menu, from_year_menu,
                    to_month_menu, to_day_menu, to_year_menu]

    search_entry = ctk.CTkEntry(page, placeholder_text="Worker ID or name (optional)", height=38)
    search_entry.bind("<Return>", on_enter_key)

    page.controls = [
        {"height": 34, "items": [
            ("text", "Report:", 70),
            ("widget", report_menu, 230),
            ("text", "Period:", 65),
            ("widget", period_menu, 150),
        ]},
        {"height": 34, "items": [
            ("text", "From:", 55),
            ("widget", from_month_menu, 125),
            ("widget", from_day_menu, 70),
            ("widget", from_year_menu, 90),
            ("text", "To:", 35),
            ("widget", to_month_menu, 125),
            ("widget", to_day_menu, 70),
            ("widget", to_year_menu, 90),
        ]},
        {"height": 38, "items": [
            ("widget", search_entry, None),
            ("button", "GENERATE REPORT", 170, RED, generate_report),
            ("button", "SAVE AS CSV", 140, GREEN_BTN, save_report),
            ("button", "MANAGE INCIDENTS", 170, ORANGE, open_incident_management),
        ]},
        {"height": 22, "items": [("info", heading_label, AMBER)]},
        {"height": 22, "items": [("info", summary_label, WHITE)]},
        {"height": 22, "items": [("info", message_label, WHITE)]},
    ]

    # Start with the filters on their default choices (Daily Attendance, Today)
    set_default_filters()

    return page, load_page

# =====================================================================
# PASTE THIS WHOLE FILE AT THE VERY BOTTOM OF YOUR frontend.py
# (open frontend.py, press Ctrl+End to go to the last line, press Enter twice, then paste)
# It must be the LAST thing in the file (below the Worker screens and the glass pages).
# =====================================================================

# =====================================================
# SIZE FIX (paste at the VERY BOTTOM of frontend.py)
# Panels are smaller, the text is bigger, and the search bar is bigger.
# =====================================================
import tkinter.font as tkfont

PANEL_SCALE = 1280 / 1920     # 0.667 = panels/margins/gaps at 1280x720 size. 1.0 = old size
FONT_SCALE = 1.15             # bigger = bigger text on every glass page
CONTROL_SCALE = 1.35          # height of search bars, dropdowns, buttons above the table
ROW_SCALE = 1.15              # height of the table rows
COL_SCALE = 1.15              # width of the fixed table columns


def px(number):
    """A layout size (margin, gap, panel) made smaller by PANEL_SCALE."""
    return max(1, int(number * PANEL_SCALE))


def fpx(size):
    """A font size in PIXELS, made bigger by FONT_SCALE."""
    return max(10, int(size * 1.33 * FONT_SCALE))


def ctl(number):
    """The height of a search bar / dropdown / button."""
    return int(number * CONTROL_SCALE)


def text_width(text, size, bold=True):
    """How many pixels wide a text is, so boxes and buttons can fit it."""
    font = tkfont.Font(family="Arial", size=-fpx(size), weight="bold" if bold else "normal")
    return font.measure(text)


def scaled_create_text(self, *args, **options):
    """Like create_text, but the font size goes through fpx() (same size on every screen)."""
    font = options.get("font")
    if isinstance(font, tuple) and len(font) >= 2 and isinstance(font[1], int) and font[1] > 0:
        options["font"] = (font[0], -fpx(font[1])) + tuple(font[2:])
    return tk.Canvas.create_text(self, *args, **options)


GlassCanvas.create_text = scaled_create_text
GlassButton.create_text = scaled_create_text

widget_fonts = {}


def get_widget_font():
    """The bigger font for the real search boxes and dropdowns."""
    if "font" not in widget_fonts:
        widget_fonts["font"] = ctk.CTkFont(family="Arial", size=fpx(13))
    return widget_fonts["font"]


# ---------- The glass table pages ----------
original_table_init = GlassTablePage.__init__


def compact_table_init(self, parent, screen, page_title, columns, row_height=46):
    original_table_init(self, parent, screen, page_title, columns, row_height)
    self.row_height = int(row_height * ROW_SCALE)
    self.skip_col_scale = False


def compact_paint(self, canvas, W, H):
    margin = px(30)
    title_y = fpx(26) // 2 + px(14)
    canvas.create_text(px(36), title_y, text=self.page_title, anchor="w",
                       fill=WHITE, font=("Arial", 26, "bold"))

    y = title_y * 2 + px(6)
    for row in self.controls:
        y = self.place_row(canvas, row, y, W)

    # ----- the glass panel for the table -----
    top = y
    bottom = H - px(30)
    self.glass((margin, top, W - margin, bottom), 16, 140)

    inner_left = margin + px(30)
    inner_right = W - margin - px(34)

    scale = 1.0 if getattr(self, "skip_col_scale", False) else COL_SCALE
    fixed = 0
    for heading, width in self.table_columns:
        if width is not None:
            fixed = fixed + int(width * scale)
    stretch = max(120, (inner_right - inner_left) - fixed)

    self.col_x = []
    self.col_w = []
    header_h = fpx(13) + px(30)
    x = inner_left
    for heading, width in self.table_columns:
        if width is None:
            width = stretch
        else:
            width = int(width * scale)
        self.col_x.append(x)
        self.col_w.append(width)
        canvas.create_text(x, top + header_h // 2, text=heading, anchor="w",
                           fill=AMBER, font=("Arial", 13, "bold"))
        x = x + width

    canvas.create_line(inner_left, top + header_h, inner_right, top + header_h, fill="#8A4A33")

    self.area_top = top + header_h + px(8)
    self.area_left = inner_left
    self.area_right = inner_right
    self.scroll_x = W - margin - px(20)
    area_height = bottom - px(14) - self.area_top
    self.page_rows = max(1, area_height // self.row_height)
    self.draw_rows()


def compact_weighted_paint(self, canvas, W, H):
    """For the pages whose columns share the width by weights."""
    usable = max(300, W - px(30) * 2 - px(64))
    total = 0
    for heading, weight in self.column_weights:
        total = total + weight

    self.table_columns = []
    for heading, weight in self.column_weights:
        self.table_columns.append((heading, int(usable * weight / total)))

    self.skip_col_scale = True            # these widths are already exact
    compact_paint(self, canvas, W, H)


def compact_place_row(self, canvas, row, y, W):
    """Places one row of tools above the table. Boxes are bigger, buttons fit their text."""
    items = row["items"]
    height = ctl(row["height"])
    gap = px(14)
    left = px(36)
    total = W - 2 * left

    # a line of text
    if items[0][0] == "info":
        label = items[0][1]
        color = items[0][2]
        label.attach(canvas, left, y + height // 2, anchor="w", fill=color,
                     font=("Arial", 13), width=total, justify="left")
        return y + height + px(4)

    def item_width(item):
        kind = item[0]
        wanted = item[2]
        if wanted is None:
            return None
        if kind == "text":
            return text_width(item[1], 14) + px(8)
        if kind == "button":
            return max(px(wanted), text_width(item[1], 12) + px(44))
        return int(wanted * 1.2)                  # real widgets (dropdowns, boxes)

    fixed = gap * (len(items) - 1)
    stretch_count = 0
    for item in items:
        if item_width(item) is None:
            stretch_count = stretch_count + 1
        else:
            fixed = fixed + item_width(item)

    stretch = max(160, (total - fixed) // max(1, stretch_count))
    stretch = min(stretch, 1000)

    x = left
    for item in items:
        kind = item[0]
        width = item_width(item)
        if width is None:
            width = stretch

        if kind == "text":
            canvas.create_text(x, y + height // 2, text=item[1], anchor="w",
                               fill=WHITE, font=("Arial", 14, "bold"))
        elif kind == "widget":
            widget = item[1]
            try:
                widget.configure(font=get_widget_font())
            except Exception:
                pass
            try:
                widget.configure(dropdown_font=get_widget_font())
            except Exception:
                pass
            canvas.create_window(x, y, window=widget, anchor="nw", width=width, height=height)
        elif kind == "button":
            self.put_button(x, y, width, height, item[1], item[3], item[4], "chrome", self.keep)

        x = x + width + gap

    return y + height + px(12)


def compact_draw_cell(self, cell, x, width, row_y, middle):
    if isinstance(cell, str):
        cell = ("text", cell, WHITE, False)

    kind = cell[0]

    if kind == "text":
        if cell[3]:
            font = ("Arial", 14, "bold")
        else:
            font = ("Arial", 13)
        self.create_text(x, middle, text=cell[1], anchor="w", fill=cell[2],
                         font=font, width=width - 10, tags="rows")

    elif kind == "button":
        button_h = int(self.row_height * 0.62)
        button_w = min(width - 10, text_width(cell[1], 12) + px(44))
        self.put_button(x, middle - button_h // 2, button_w, button_h, cell[1], cell[2],
                        cell[3], "rows", self.row_photos)

    elif kind == "menu":
        self.count += 1
        unique = "mn" + str(self.count)
        self.create_text(x, middle, text=cell[1] + "   \u25BE", anchor="w", fill=cell[2],
                         font=("Arial", 14, "bold"), tags=("rows", unique))
        self.tag_bind(unique, "<Button-1>", partial(self.open_menu, cell[3], cell[4]))
        self.tag_bind(unique, "<Enter>", lambda event: self.config(cursor="hand2"))
        self.tag_bind(unique, "<Leave>", lambda event: self.config(cursor=""))


GlassTablePage.__init__ = compact_table_init
GlassTablePage.paint = compact_paint
GlassTablePage.place_row = compact_place_row
GlassTablePage.draw_cell = compact_draw_cell
GlassWeightedTablePage.paint = compact_weighted_paint
