# main.py
# Iligan City Fire Station System - the file you RUN.
# ONE window, ONE page: the glass card on the welcome screen grows (with animation)
# into the Login, Register, Worker Menu and Attendance panels.
#
#   backend.py  = all the data (reads and saves the text files)
#   frontend.py = the Admin screens, the fire colors, and small shared helpers
#   main.py     = this file: the window, the animated glass card (ALL worker screens),
#                 and the bell sound
#
# Pictures used (same folder as this file): background.png, fire_logo.png and smc_logo.png

import os
import math
import re
import struct
import wave
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageOps
from datetime import datetime, timedelta
from tkinter import filedialog

import backend
import frontend

ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)

frontend.apply_theme()  
backend.create_tables()
backend.migrate_uids()      # one time: old IDs like UID-4673 become 4673 (safe to run again)

# ---------- SETTINGS (easy to change) ----------
START_W, START_H = 1000, 650
SYSTEM_NAME = "Iligan City Fire Station System"

DARK_TINT = (25, 8, 8)
FIRE_RED = (200, 25, 25)
FIRE_ORANGE = (230, 100, 15)
FIRE_DARK_RED = (120, 10, 10)
FIRE_GRAY = (93, 64, 55)

MSG_COLOR = "#FFB74D"        # normal message
BAD_COLOR = "#FF8A80"        # error message
GOOD_COLOR = "#81C784"       # success message
ABOUT_TEXT = "#FFE9D6"       # warm cream text used on the About card

ANIMATION_SPEED = 0.22       # 0.1 = slow and floaty, 0.4 = fast
FRAME_MS = 16                # about 60 frames per second

# The size of the glass card for each screen (width, height) at normal scale
PANEL_SIZES = {
    "home": (320, 420),
    "login": (400, 400),
    "menu": (480, 450),
    "attendance": (420, 495),
    "register": (640, 620),
    "success": (420, 430),
    "absence": (560, 560),
    "leave": (600, 650),
    "incident": (700, 840),
    "duty": (600, 650),
    "information": (600, 660),
    "edit_information": (640, 620),
    "admin_login": (420, 520),
    "admin_register": (460, 590),
    "about": (760, 740),
}

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


# =====================================================
# THE BELL SOUND (made by code, so you need no sound file)
# =====================================================
BELL_FILE = os.path.join(BASE_FOLDER, "bell.wav")


def make_bell_file():
    """Makes bell.wav one time: a few soft tones that fade out like a small bell."""
    if os.path.exists(BELL_FILE):
        return
    rate = 44100
    total = int(rate * 1.6)
    # (pitch in Hz, loudness, how fast it fades)
    tones = [(880, 1.0, 3.0), (2217, 0.5, 4.5), (2640, 0.35, 6.0), (4400, 0.15, 8.0)]

    data = bytearray()
    for i in range(total):
        t = i / rate
        value = 0.0
        for pitch, loudness, fade in tones:
            value += loudness * math.exp(-fade * t) * math.sin(2 * math.pi * pitch * t)
        value = value * min(1.0, t * 200) * 0.4          # a tiny fade-in avoids a click
        value = max(-1.0, min(1.0, value))
        data += struct.pack("<h", int(value * 32767))

    with wave.open(BELL_FILE, "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(rate)
        sound.writeframes(bytes(data))


def play_bell():
    """Plays the bell without freezing the window. If it cannot, it uses the normal beep."""
    try:
        import winsound
        winsound.PlaySound(BELL_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        try:
            app.bell()
        except Exception:
            pass


def add_bell_to(function_name):
    """Wraps one backend save function, so the bell rings every time it saves something.
    The frontend does not need to change: it calls backend.save_... and the bell follows."""
    original = getattr(backend, function_name)

    def with_bell(*args, **kwargs):
        result = original(*args, **kwargs)
        if result is not False and backend.get_setting("notifications", "on") == "on":
            play_bell()
        return result

    setattr(backend, function_name, with_bell)


make_bell_file()
for each_name in ["save_time_in", "save_time_out", "save_absence",
                  "save_leave", "save_incident", "save_worker"]:
    add_bell_to(each_name)


# =====================================================
# GLASS PICTURE
# =====================================================
def make_glass(background, box, radius, tint, alpha, blur=True):
    """Makes a see-through 'glass' picture for the area `box` of the background.
    blur=False is used while the card is moving (the background is already blurred)."""
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    radius = max(2, min(radius, w // 2, h // 2))

    piece = background.crop(box)
    if blur:
        piece = piece.filter(ImageFilter.GaussianBlur(10))
    piece = piece.convert("RGBA")

    piece = Image.alpha_composite(piece, Image.new("RGBA", (w, h), tint + (alpha,)))

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    piece.putalpha(mask)

    ImageDraw.Draw(piece).rounded_rectangle(
        (0, 0, w - 1, h - 1), radius=radius, outline=(255, 190, 120, 150), width=2
    )
    return piece


# =====================================================
# THE WELCOME SCREEN WITH THE ANIMATED GLASS CARD
# =====================================================
class WelcomeScreen(tk.Canvas):
    """The first screen. The glass card on the right grows and shrinks smoothly
    to show Login, Register, the Menu, Attendance and the new Worker ID."""

    def __init__(self, parent, go):
        super().__init__(parent, highlightthickness=0, bd=0, bg="#1a0808")
        self.go = go                  # go("admin") opens the Admin screen
        self.list_item = None         # the "recent requests" text on the Leave / Incident cards

        self.keep = []                # keeps pictures alive
        self.widgets = []             # real widgets (text boxes, dropdowns) inside the card
        self.button_count = 0

        self.mode = "home"            # home, login, menu, attendance, register, success
        self.worker = {}              # who is logged in
        self.new_uid = ""             # the Worker ID shown after registering
        self.prefill_uid = ""         # filled in the Login box after registering

        self.message = None           # the message text item inside the card
        self.message_text = ""
        self.message_color = MSG_COLOR
        self.entry = None             # the Worker ID box on the Login screen
        self.fields = {}              # the boxes of the Register form
        self.sex_var = None
        self.worker_photo_path = ""
        self.photo_name_item = None

        self.scale = 1.0
        self.cur_rect = [0, 0, 1, 1]  # where the card is right now (it moves each frame)
        self.target = [0, 0, 1, 1]    # where the card is going
        self.anim = None
        self.on_done = None
        self.panel_photo = None
        self.bg = None
        self.blurred = None
        self.last_size = (0, 0)
        self.timer = None

        bg_path = os.path.join(BASE_FOLDER, "background.png")
        if os.path.exists(bg_path):
            self.original_bg = Image.open(bg_path).convert("RGB")
        else:
            print("WARNING: background.png was not found in:", BASE_FOLDER)
            self.original_bg = Image.new("RGB", (1000, 650), (40, 12, 10))

        logo = frontend.load_logo()
        if logo is None:
            print("WARNING: fire_logo.png was not found in:", BASE_FOLDER)
            logo = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        self.original_logo = logo

        school_logo_path = os.path.join(BASE_FOLDER, "smc_logo.png")
        self.original_school_logo = None
        if os.path.exists(school_logo_path):
            try:
                school_logo = Image.open(school_logo_path).convert("RGBA")
                for corner in [(0, 0), (school_logo.width - 1, 0),
                               (0, school_logo.height - 1),
                               (school_logo.width - 1, school_logo.height - 1)]:
                    ImageDraw.floodfill(school_logo, corner, (255, 255, 255, 0), thresh=50)
                self.original_school_logo = school_logo
            except (OSError, ValueError) as exc:
                print("WARNING: smc_logo.png could not be loaded:", exc)
        else:
            print("WARNING: smc_logo.png was not found in:", BASE_FOLDER)

        self.bind("<Configure>", self.on_resize)

    # ---------------- window size ----------------
    def on_resize(self, event):
        if (event.width, event.height) == self.last_size:
            return
        self.last_size = (event.width, event.height)
        if self.timer is not None:
            self.after_cancel(self.timer)
        self.timer = self.after(100, self.draw)

    def target_rect(self, mode):
        """Works out where the card should be for a screen: (x1, y1, x2, y2).
        It shrinks the card if the window is too small for it."""
        W, H = self.winfo_width(), self.winfo_height()
        base_w, base_h = PANEL_SIZES[mode]
        k = min(self.scale, (H - 120) / base_h, (W * 0.92) / base_w)
        k = max(k, 0.4)
        w, h = base_w * k, base_h * k

        # Every worker screen uses the same centered animated glass card.
        cx = W / 2
        cy = H / 2
        return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

    def geo(self):
        """Gives (left, top, middle, k) of the card that is on the screen.
        k is how much bigger or smaller than normal the card is."""
        x1, y1, x2, y2 = self.target
        k = (x2 - x1) / PANEL_SIZES[self.mode][0]
        return x1, y1, (x1 + x2) / 2, k

    # ---------------- drawing the whole screen ----------------
    def draw(self):
        """Draws everything to fit the CURRENT window size."""
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 50 or H < 50:
            return

        if self.anim is not None:                 # stop any animation that is running
            self.after_cancel(self.anim)
            self.anim = None
            self.on_done = None

        self.clear_content()
        self.delete("all")
        self.keep = []
        self.button_count = 0

        self.scale = max(0.6, min(W / 1000, H / 650))

        self.bg = ImageOps.fit(self.original_bg, (W, H))
        self.blurred = self.bg.filter(ImageFilter.GaussianBlur(10))   # blurred ONE time
        self.show_picture(0, 0, self.bg, "bg")

        self.cur_rect = self.target_rect(self.mode)
        self.target = list(self.cur_rect)
        self.draw_panel()
        self.build_content()

        # Admin button (small, top right corner of the window)
        if self.mode not in ("admin_login", "admin_register"):
            s = self.scale
            self.add_button((W - int(140 * s), int(15 * s), W - int(25 * s), int(50 * s)),
                            "Admin", FIRE_DARK_RED, lambda: self.set_mode("admin_login"), s, 11, "static")
        if self.mode not in ("admin_login", "admin_register"):
            s = self.scale
            self.add_button((int(18 * s), H - int(52 * s), int(132 * s), H - int(16 * s)),
                            "About", FIRE_GRAY, lambda: self.go("about"), s, 11, "static")

    def draw_panel(self):
        """Draws the glass card at its current size. It runs on every frame of the animation."""
        self.delete("panel")
        W, H = self.winfo_width(), self.winfo_height()
        x1, y1, x2, y2 = [int(v) for v in self.cur_rect]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(W, x2), min(H, y2)
        if x2 - x1 < 10 or y2 - y1 < 10:
            return

        image = make_glass(self.blurred, (x1, y1, x2, y2), int(36 * self.scale),
                           DARK_TINT, 110, blur=False)
        self.panel_photo = ImageTk.PhotoImage(image)
        self.create_image(x1, y1, image=self.panel_photo, anchor="nw", tags="panel")
        self.tag_raise("panel", "bg")             # the card sits just above the background

    # ---------------- the smooth animation ----------------
    def animate_to(self, rect, done):
        """Moves the card to a new size. 'done' runs when it arrives."""
        self.target = rect
        self.on_done = done
        if self.anim is None:
            self.step()

    def step(self):
        """One frame: the card moves a part of the way to its target (smooth ease-out)."""
        new = []
        for current, goal in zip(self.cur_rect, self.target):
            new.append(current + (goal - current) * ANIMATION_SPEED)

        arrived = True
        for value, goal in zip(new, self.target):
            if abs(value - goal) > 1.5:
                arrived = False
        if arrived:
            new = list(self.target)

        self.cur_rect = new
        self.draw_panel()

        if arrived:
            self.anim = None
            done = self.on_done
            self.on_done = None
            if done is not None:
                done()
        else:
            self.anim = self.after(FRAME_MS, self.step)

    def set_mode(self, mode, message=""):
        """Changes the screen inside the card: the old content disappears, the card
        grows or shrinks, and then the new content appears."""
        self.clear_content()
        self.mode = mode
        self.message_text = message
        self.message_color = MSG_COLOR
        self.animate_to(self.target_rect(mode), self.build_content)

    def reset_home(self):
        """Goes back to the first card at once (used when we come back from another screen)."""
        if self.mode != "home":
            self.worker = {}
            self.mode = "home"
            self.message_text = ""
            self.draw()

    # ---------------- small drawing tools ----------------
    def show_picture(self, x, y, pil_image, tag=None):
        photo = ImageTk.PhotoImage(pil_image)
        self.keep.append(photo)
        return self.create_image(x, y, image=photo, anchor="nw", tags=tag if tag else ())

    def put_logo(self, cx, y, size):    
        logo = self.original_logo.copy()
        logo.thumbnail((size, size))
        self.show_picture(int(cx - logo.width // 2), int(y), logo, "content")

    def put_text(self, x, y, text, size, color, bold=False, italic=False, width=None,
                 anchor="center"):
        style = []
        if bold:
            style.append("bold")
        if italic:
            style.append("italic")
        options = {}
        if width is not None:
            options["width"] = int(width)
            options["justify"] = "center"
        return self.create_text(int(x), int(y), text=text, fill=color, anchor=anchor,
                                font=("Segoe UI", max(8, int(size)), " ".join(style)),
                                tags="content", **options)

    def make_message(self, x, y, width, size):
        """The line of text that shows messages INSIDE the card (no popups)."""
        self.message = self.put_text(x, y, self.message_text, size, self.message_color,
                                     bold=True, width=width)

    def show_message(self, text, color=MSG_COLOR):
        self.message_text = text
        self.message_color = color
        if self.message is not None:
            self.itemconfig(self.message, text=text, fill=color)

    def clear_content(self):
        """Removes everything inside the card (texts, buttons, text boxes)."""
        self.delete("content")
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []
        self.message = None
        self.list_item = None
        self.entry = None
        self.fields = {}

    def put_widget(self, widget, x, y, w, h):
        self.create_window(int(x), int(y), window=widget, anchor="nw",
                           width=int(w), height=int(h), tags="content")
        self.widgets.append(widget)

    def widget_font(self, size):
        return ctk.CTkFont(family="Segoe UI", size=max(10, int(size)))

    def make_entry(self, x, y, w, h, placeholder, size, center=False):
        entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=int(w), height=int(h),
                             font=self.widget_font(size),
                             justify="center" if center else "left")
        self.put_widget(entry, x, y, w, h)
        return entry

    def make_menu(self, x, y, w, h, values, start, size):
        menu = ctk.CTkOptionMenu(self, values=values, width=int(w), height=int(h),
                                 font=self.widget_font(size),
                                 dropdown_font=self.widget_font(size))
        menu.set(start)
        self.put_widget(menu, x, y, w, h)
        return menu

    def field_label(self, x, y, text, k):
        """A small bold title above a field."""
        self.create_text(int(x), int(y), text=text, anchor="w", fill="#FFE0B2",
                         font=("Segoe UI", max(8, int(10 * k)), "bold"), tags="content")

    def make_textbox(self, x, y, w, h, size):
        box = ctk.CTkTextbox(self, width=int(w), height=int(h), border_width=2,
                             font=self.widget_font(size))
        self.put_widget(box, x, y, w, h)
        return box

    def make_top_message(self, cx, y, width, size):
        """A message line whose TOP edge is fixed, so long messages grow downward."""
        self.message = self.create_text(int(cx), int(y), text=self.message_text,
                                        fill=self.message_color, anchor="n", tags="content",
                                        font=("Segoe UI", max(8, int(size)), "bold"),
                                        width=int(width), justify="center")

    def form_header(self, cx, y1, k, title):
        """The title and the logged-in worker's name, the same on every worker card."""
        u = lambda value: int(value * k)
        self.put_text(cx, y1 + u(34), title, u(20), "#FFE0B2", bold=True)
        if self.worker:
            self.put_text(cx, y1 + u(62), self.worker["full_name"] + "   (" + self.worker["uid"] + ")",
                          u(11), "#FFCC80", width=u(500))

    def make_date_menus(self, x, y, k, widths, years, when):
        """Month, Day and Year dropdowns, set to the date `when`."""
        u = lambda value: int(value * k)
        month = self.make_menu(x, y, u(widths[0]), u(36), frontend.MONTHS,
                               frontend.MONTHS[when.month - 1], u(12))
        day = self.make_menu(x + u(widths[0] + 5), y, u(widths[1]), u(36), frontend.DAYS,
                             str(when.day), u(12))
        year = self.make_menu(x + u(widths[0] + widths[1] + 10), y, u(widths[2]), u(36),
                              years, str(when.year), u(12))
        return month, day, year

    def back_to_menu_button(self, cx, y_top, k, width=280):
        """THE one BACK TO MENU button used by every worker card. It always goes to set_mode("menu")."""
        u = lambda value: int(value * k)
        self.add_button((cx - u(width // 2), y_top, cx + u(width // 2), y_top + u(40)),
                        "BACK TO MENU", FIRE_GRAY, lambda: self.set_mode("menu"), k, 11)

    def add_button(self, box, text, tint, command, s, font_size=15, group="content"):
        """Makes a glass button. It gets brighter when the mouse is over it."""
        x1, y1, x2, y2 = [int(v) for v in box]
        radius = 12
        normal = ImageTk.PhotoImage(make_glass(self.bg, (x1, y1, x2, y2), radius, tint, 140))
        hover = ImageTk.PhotoImage(make_glass(self.bg, (x1, y1, x2, y2), radius, tint, 215))
        self.keep += [normal, hover]

        self.button_count += 1
        tag = "button" + str(self.button_count)
        tags = (tag, group)

        picture = self.create_image(x1, y1, image=normal, anchor="nw", tags=tags)
        self.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text, fill="#FFF3E0",
                         font=("Segoe UI", max(8, int(font_size * s)), "bold"), tags=tags)

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
    # THE CONTENT OF EACH SCREEN
    # =====================================================
    def build_content(self):
        """Fills the card with the content of the current screen."""
        builders = {
            "home": self.build_home,
            "login": self.build_login,
            "menu": self.build_menu,
            "attendance": self.build_attendance,
            "register": self.build_register,
            "success": self.build_success,
            "absence": self.build_absence,
            "leave": self.build_leave,
            "incident": self.build_incident,
            "duty": self.build_duty,
            "information": self.build_information,
            "edit_information": self.build_edit_information,
            "admin_login": self.build_admin_login,
            "admin_register": self.build_admin_register,
            "about": self.build_about,
        }
        builders[self.mode]()

    # ---------- HOME ----------
    def build_home(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_logo(cx, y1 + u(18), u(90))
        self.put_text(cx, y1 + u(140), SYSTEM_NAME, u(17), "#FFE0B2", bold=True, width=u(280))
        self.put_text(cx, y1 + u(190), "Welcome! Please choose an option.", u(11), "#FFCC80")

        half = u(125)
        self.add_button((cx - half, y1 + u(222), cx + half, y1 + u(270)), "Login",
                        FIRE_RED, lambda: self.set_mode("login"), k, 13)
        self.add_button((cx - half, y1 + u(285), cx + half, y1 + u(333)), "Register",
                        FIRE_ORANGE, lambda: self.set_mode("register"), k, 13)

        self.make_message(cx, y1 + u(375), u(280), u(10))

    # ---------- ABOUT ----------
    def build_about(self):
        """Builds a scrollable About page so the information stays balanced."""
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        # The About card is intentionally scrollable instead of squeezing
        # every line into the fixed glass panel.
        panel_w = max(360, int((self.target[2] - self.target[0]) - u(44)))
        panel_h = max(300, int((self.target[3] - self.target[1]) - u(54)))

        outer = tk.Frame(
            self,
            bg="#24100F",
            highlightthickness=1,
            highlightbackground="#8F4A2F",
            bd=0,
        )
        outer.pack_propagate(False)
        self.put_widget(outer, x1 + u(22), y1 + u(22), panel_w, panel_h)

        inner_canvas = tk.Canvas(
            outer,
            bg="#24100F",
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        scrollbar = tk.Scrollbar(
            outer,
            orient="vertical",
            command=inner_canvas.yview,
            bg="#5C2418",
            activebackground="#A94420",
            troughcolor="#160A09",
            relief="flat",
            width=max(12, int(u(12))),
        )
        inner_canvas.configure(yscrollcommand=scrollbar.set)
        inner_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = tk.Frame(inner_canvas, bg="#24100F")
        window_id = inner_canvas.create_window((0, 0), window=content, anchor="nw")

        def update_scroll_region(event=None):
            inner_canvas.configure(scrollregion=inner_canvas.bbox("all"))
            inner_canvas.itemconfigure(window_id, width=inner_canvas.winfo_width())

        content.bind("<Configure>", update_scroll_region)
        inner_canvas.bind("<Configure>", update_scroll_region)

        def scroll_about(event):
            if event.delta:
                inner_canvas.yview_scroll(int(-event.delta / 120), "units")
            return "break"

        inner_canvas.bind("<MouseWheel>", scroll_about)
        content.bind("<MouseWheel>", scroll_about)
        inner_canvas.bind("<Button-4>", lambda event: (inner_canvas.yview_scroll(-1, "units"), "break")[-1])
        inner_canvas.bind("<Button-5>", lambda event: (inner_canvas.yview_scroll(1, "units"), "break")[-1])

        self.about_scroll_widget = outer

        content_pad = max(18, u(24))
        logo_row = tk.Frame(content, bg="#24100F")
        logo_row.pack(fill="x", padx=content_pad, pady=(content_pad, u(8)))

        # Main Fire Protection logo.
        if self.original_logo is not None:
            fire_logo = self.original_logo.copy()
            fire_logo.thumbnail((u(105), u(105)))
            fire_photo = ImageTk.PhotoImage(fire_logo)
            self.keep.append(fire_photo)
            fire_label = tk.Label(logo_row, image=fire_photo, bg="#24100F", bd=0)
            fire_label.pack(side="left", expand=True)

        # St. Michael's College logo.
        if self.original_school_logo is not None:
            school_logo = self.original_school_logo.copy()
            school_logo.thumbnail((u(105), u(105)))
            school_photo = ImageTk.PhotoImage(school_logo)
            self.keep.append(school_photo)
            school_label = tk.Label(logo_row, image=school_photo, bg="#24100F", bd=0)
            school_label.pack(side="left", expand=True)

        def about_label(text, size, color, bold=False, pady=(4, 4)):
            label = tk.Label(
                content,
                text=text,
                bg="#24100F",
                fg=color,
                font=("Segoe UI", max(9, u(size)), "bold" if bold else "normal"),
                justify="center",
                anchor="center",
                wraplength=max(280, panel_w - u(80)),
            )
            label.pack(fill="x", padx=content_pad, pady=pady)
            return label

        about_label("BUREAU OF FIRE PROTECTION", 9, "#FFFFFF", True, (0, 2))
        about_label("ST. MICHAEL'S COLLEGE", 9, "#FFFFFF", True, (0, 12))
        about_label("About Our System", 24, "#FFE0B2", True, (4, 4))
        about_label(
            "Iligan City Fire Station Employee Management System",
            14,
            "#FFCC80",
            True,
            (2, 14),
        )

        description = (
            "The Iligan City Fire Station Employee Management System is designed to help "
            "fire station personnel manage their daily work activities more easily and "
            "efficiently. It provides features for recording attendance, reporting absences, "
            "filing leave requests, submitting incident reports, and viewing assigned duties "
            "and work shifts."
        )
        about_label(description, 12, ABOUT_TEXT, False, (4, 18))

        purpose = (
            "This system aims to improve record management, organize employee information, "
            "and make daily operations more convenient for both workers and administrators."
        )
        about_label(purpose, 12, ABOUT_TEXT, False, (4, 18))

        about_label("Developed by", 14, "#FFCC80", True, (12, 4))
        about_label("BSIT 2nd Year Students • St. Michael's College", 12, ABOUT_TEXT, False, (2, 18))

        about_label("Credits", 16, "#FFCC80", True, (8, 8))
        developers = "Gabriel Gabuya\nAlwin Jan Rebuton\nAlrie Madula\nSelwyn Cuesta"
        about_label(developers, 13, ABOUT_TEXT, False, (4, 18))

        academic_note = (
            "This system was developed as an academic project to apply our knowledge and "
            "skills in Information Technology to a real-world workplace setting."
        )
        about_label(academic_note, 11, "#FFCC80", False, (18, 22))

        back_button = tk.Button(
            content,
            text="BACK",
            command=lambda: self.go("about_back"),
            bg="#5D4037",
            activebackground="#795548",
            fg="#FFF3E0",
            activeforeground="#FFFFFF",
            font=("Segoe UI", max(9, u(11)), "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=u(24),
            pady=u(8),
        )
        back_button.pack(pady=(4, content_pad))

        # Start at the top every time About opens.
        inner_canvas.yview_moveto(0)

    # ---------- LOGIN ----------
    def build_login(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_logo(cx, y1 + u(16), u(70))
        self.put_text(cx, y1 + u(122), "Worker Login", u(20), "#FFE0B2", bold=True)
        self.put_text(cx, y1 + u(152), "Enter your 4-digit Worker ID.", u(11), "#FFCC80")

        self.entry = self.make_entry(cx - u(140), y1 + u(180), u(280), u(46),
                                     "1234", u(16), center=True)
        self.entry.bind("<Return>", lambda event: self.do_login())
        if self.prefill_uid != "":
            self.entry.insert(0, self.prefill_uid)
            self.prefill_uid = ""

        self.make_message(cx, y1 + u(246), u(320), u(10))

        self.add_button((cx - u(140), y1 + u(272), cx + u(140), y1 + u(320)), "LOGIN",
                        FIRE_RED, self.do_login, k, 13)
        self.add_button((cx - u(140), y1 + u(332), cx + u(140), y1 + u(374)), "BACK",
                        FIRE_GRAY, lambda: self.set_mode("home"), k, 11)

        self.after(60, self.entry.focus_set)

    # ---------- ADMIN LOGIN / ONE-TIME REGISTRATION ----------
    def admin_entry(self, x, y, width, height, placeholder, password=False, allowed=None):
        validate = None
        if allowed is not None:
            validate = (self.register(lambda value: bool(re.fullmatch(allowed, value))), "%P")
        entry = ctk.CTkEntry(self, placeholder_text=placeholder, show="•" if password else "",
                             width=int(width), height=int(height), font=self.widget_font(13),
                             validate="key" if validate else "none", validatecommand=validate)
        self.put_widget(entry, x, y, width, height)
        return entry

    def build_admin_login(self):
        _, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.put_logo(cx, y1 + u(18), u(82))
        self.put_text(cx, y1 + u(112), "Admin Login", u(21), "#FFE0B2", bold=True)
        left = cx - u(155)
        self.field_label(left, y1 + u(155), "Username", k)
        self.admin_username = self.admin_entry(left, y1 + u(174), u(310), u(42),
                                                "Lowercase letters and numbers, max 10", allowed=r"[a-z0-9]{0,10}")
        self.field_label(left, y1 + u(230), "Password", k)
        self.admin_password = self.admin_entry(left, y1 + u(249), u(310), u(42),
                                                "Letters and numbers, max 5", password=True, allowed=r"[A-Za-z0-9]{0,5}")
        self.make_message(cx, y1 + u(308), u(340), u(10))
        self.admin_username.bind("<Return>", lambda event: self.admin_password.focus_set())
        self.admin_password.bind("<Return>", lambda event: self.admin_login())
        self.add_button((cx - u(155), y1 + u(344), cx + u(155), y1 + u(390)), "LOGIN",
                        FIRE_RED, self.admin_login, k, 13)
        if not backend.has_admin_account():
            self.add_button((cx - u(155), y1 + u(402), cx + u(155), y1 + u(446)), "REGISTER ADMIN ACCOUNT",
                            FIRE_ORANGE, lambda: self.set_mode("admin_register"), k, 10)
        self.add_button((cx - u(155), y1 + u(458), cx + u(155), y1 + u(498)), "BACK",
                        FIRE_GRAY, lambda: self.set_mode("home"), k, 11)
        self.after(60, self.admin_username.focus_set)

    def admin_login(self):
        username = self.admin_username.get().strip()
        password = self.admin_password.get()
        if not backend.has_admin_account():
            self.show_message("Register the first admin account first.", BAD_COLOR)
            return
        if not backend.verify_admin_account(username, password):
            self.show_message("Incorrect admin username or password.", BAD_COLOR)
            return
        self.go("admin")

    def build_admin_register(self):
        _, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.put_logo(cx, y1 + u(18), u(82))
        self.put_text(cx, y1 + u(112), "Admin Registration", u(21), "#FFE0B2", bold=True)
        self.put_text(cx, y1 + u(143), "Create the first administrator account.", u(11), "#FFCC80")
        left = cx - u(165)
        self.field_label(left, y1 + u(180), "Username (lowercase letters and numbers, max 10)", k)
        self.admin_username = self.admin_entry(left, y1 + u(201), u(330), u(42),
                                                "Choose a username", allowed=r"[a-z0-9]{0,10}")
        self.field_label(left, y1 + u(258), "Password (letters and numbers, max 5)", k)
        self.admin_password = self.admin_entry(left, y1 + u(279), u(330), u(42),
                                                "Choose a password", password=True, allowed=r"[A-Za-z0-9]{0,5}")
        self.field_label(left, y1 + u(336), "Confirm Password", k)
        self.admin_confirm = self.admin_entry(left, y1 + u(357), u(330), u(42),
                                               "Re-enter your password", password=True, allowed=r"[A-Za-z0-9]{0,5}")
        self.make_message(cx, y1 + u(412), u(360), u(10))
        self.admin_confirm.bind("<Return>", lambda event: self.admin_register())
        self.add_button((cx - u(165), y1 + u(448), cx + u(165), y1 + u(494)), "CREATE ADMIN ACCOUNT",
                        FIRE_RED, self.admin_register, k, 12)
        self.add_button((cx - u(165), y1 + u(506), cx + u(165), y1 + u(548)), "BACK TO ADMIN LOGIN",
                        FIRE_GRAY, lambda: self.set_mode("admin_login"), k, 10)

    def admin_register(self):
        username = self.admin_username.get().strip()
        password = self.admin_password.get()
        confirm = self.admin_confirm.get()
        if not username or not password or not confirm:
            self.show_message("Please complete all fields.", BAD_COLOR)
            return
        if password != confirm:
            self.show_message("Passwords do not match.", BAD_COLOR)
            return
        try:
            created = backend.create_admin_account(username, password)
        except FileExistsError:
            created = False
        if not created:
            self.show_message("An admin account is already registered.", BAD_COLOR)
            return
        self.set_mode("admin_login", "Admin account created. Please log in.")

    def do_login(self):
        """Checks the Worker ID. If it is correct, the card changes into the menu."""
        if self.entry is None:
            return
        uid = self.entry.get().strip().upper()
        if uid.startswith("UID-"):            # still works if someone types the old way
            uid = uid[4:].strip()

        if uid == "":
            self.show_message("Please enter your Worker ID.", BAD_COLOR)
            return

        if not uid.isdigit():
            self.show_message("Your Worker ID is 4 numbers, like 1234.", BAD_COLOR)
            return
        uid = uid.zfill(4)                    # 42 becomes 0042

        worker = backend.get_worker(uid)
        if worker is None:
            self.show_message("Worker ID not found. Please check your ID and try again.", BAD_COLOR)
            return

        # worker = (worker_uid, first_name, middle_name, surname, suffix, status)
        if worker[5] != "Active":
            self.show_message("This Worker ID is inactive. Please contact the Admin.", BAD_COLOR)
            return

        full_name = worker[1] + " " + worker[3]
        if worker[4] != "":
            full_name = full_name + " " + worker[4]

        self.worker = {"uid": worker[0], "first_name": worker[1], "full_name": full_name}
        self.set_mode("menu")

    # ---------- MENU ----------
    def build_menu(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_text(cx, y1 + u(46), f"{frontend.get_greeting()}, {self.worker['first_name']}!",
                      u(22), "#FFE0B2", bold=True, width=u(440))
        self.put_text(cx, y1 + u(84), "Welcome, " + self.worker["full_name"], u(13), "#FFCC80",
                      width=u(440))
        self.put_text(cx, y1 + u(110), "Worker ID: " + self.worker["uid"], u(11), "#FFFFFF")
        self.put_text(cx, y1 + u(148), "What would you like to do?", u(14), "#FFE0B2", bold=True)

        left = (cx - u(207), cx - u(7))
        right = (cx + u(7), cx + u(207))

        def button(columns, top, text, tint, command):
            self.add_button((columns[0], y1 + u(top), columns[1], y1 + u(top + 48)),
                            text, tint, command, k, 12)

        button(left, 176, "Attendance", FIRE_RED, lambda: self.set_mode("attendance"))
        button(right, 176, "Absence", FIRE_RED, lambda: self.set_mode("absence"))
        button(left, 236, "Leave", FIRE_ORANGE, lambda: self.set_mode("leave"))
        button(right, 236, "Incident Report", FIRE_ORANGE, lambda: self.set_mode("incident"))
        button(left, 296, "My Duty / Shift", FIRE_DARK_RED, lambda: self.set_mode("duty"))
        button(right, 296, "My Information", FIRE_DARK_RED, lambda: self.set_mode("information"))

        self.add_button((cx - u(207), y1 + u(368), cx + u(207), y1 + u(410)), "LOGOUT",
                        FIRE_GRAY, self.logout, k, 11)

    def logout(self):
        self.worker = {}
        self.set_mode("home")

    # ---------- ATTENDANCE ----------
    def build_attendance(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_text(cx, y1 + u(44), "Attendance", u(22), "#FFE0B2", bold=True)
        self.put_text(cx, y1 + u(82), self.worker["full_name"] + "   (" + self.worker["uid"] + ")",
                      u(12), "#FFCC80", width=u(380))
        self.put_text(cx, y1 + u(108), "Date: " + datetime.now().strftime("%B %d, %Y"),
                      u(11), "#FFFFFF")

        half = u(140)
        self.add_button((cx - half, y1 + u(140), cx + half, y1 + u(194)), "TIME IN",
                        FIRE_RED, self.record_time_in, k, 15)
        self.add_button((cx - half, y1 + u(206), cx + half, y1 + u(260)), "TIME OUT",
                        FIRE_ORANGE, self.record_time_out, k, 15)

        # the message sits under the buttons (its top edge is fixed, so long messages grow down)
        self.message = self.create_text(int(cx), y1 + u(280), text=self.message_text,
                                        fill=self.message_color, anchor="n", tags="content",
                                        font=("Segoe UI", max(8, u(11)), "bold"),
                                        width=u(360), justify="center")

        self.back_to_menu_button(cx, y1 + u(432), k, 280)

    def record_time_in(self):
        uid = self.worker["uid"]
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        time_now = now.strftime("%I:%M %p")

        existing = backend.get_attendance_today(uid, today)
        if existing is not None:
            self.show_message("Attendance Already Recorded\n\n"
                              "You have already recorded your attendance today.\n\n"
                              f"Time In: {existing[0]}", MSG_COLOR)
            return

        backend.save_time_in(uid, today, time_now, "Present")      # the bell rings here
        self.show_message(f"{frontend.get_greeting()}, {self.worker['first_name']}!\n\n"
                          "Attendance Recorded!\nYou are marked PRESENT for today.\n\n"
                          f"Time In: {time_now}", GOOD_COLOR)

    def record_time_out(self):
        uid = self.worker["uid"]
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        yesterday = (now - timedelta(days=1)).strftime("%m/%d/%Y")
        time_now = now.strftime("%I:%M %p")

        record_date = today
        existing = backend.get_attendance_record(uid, today)

        # A night shift starts yesterday at 10 PM and ends this morning
        if existing is None and now.hour < 12:
            old_record = backend.get_attendance_record(uid, yesterday)
            if old_record is not None and old_record[1] == "":
                existing = old_record
                record_date = yesterday

        if existing is None:
            self.show_message("No Time In Found\n\nPlease click TIME IN first.", BAD_COLOR)
            return

        if existing[1] != "":
            self.show_message(f"Time Out Already Recorded\n\nTime Out: {existing[1]}", MSG_COLOR)
            return

        backend.save_time_out(uid, record_date, time_now)           # the bell rings here
        self.show_message("Time Out Recorded\n\n"
                          f"Good job, {self.worker['first_name']}!\n\n"
                          f"Your Time Out was recorded at {time_now}.", GOOD_COLOR)

    # ---------- REGISTER ----------
    def choose_worker_photo(self):
        path = filedialog.askopenfilename(
            parent=self, title="Choose worker photo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All files", "*.*")])
        if not path:
            return
        try:
            with Image.open(path) as selected_image:
                selected_image.verify()
        except Exception:
            self.show_message("That file is not a supported image. Please choose another photo.", BAD_COLOR)
            return
        self.worker_photo_path = path
        if self.photo_name_item is not None:
            self.itemconfig(self.photo_name_item, text=os.path.basename(path))
        self.show_message("Photo selected.", GOOD_COLOR)

    def build_register(self):
        self.worker_photo_path = ""
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_text(cx, y1 + u(36), "Worker Registration", u(19), "#FFE0B2", bold=True)
        self.put_text(cx, y1 + u(62), "Fill in all fields. Suffix is optional.", u(10), "#FFCC80")

        left_x = cx - u(280)
        right_x = cx + u(5)
        col_w = u(275)
        full_w = u(560)
        box_h = u(36)
        size = u(12)

        def label(x, top, text):
            self.create_text(int(x), y1 + u(top), text=text, anchor="w", fill="#FFE0B2",
                             font=("Segoe UI", max(8, u(10)), "bold"), tags="content")

        label(left_x, 90, "First Name")
        label(right_x, 90, "Middle Name")
        self.fields["first"] = self.make_entry(left_x, y1 + u(102), col_w, box_h,
                                               "Enter your first name", size)
        self.fields["middle"] = self.make_entry(right_x, y1 + u(102), col_w, box_h,
                                                "Enter your middle name", size)

        label(left_x, 150, "Surname")
        label(right_x, 150, "Suffix (optional)")
        self.fields["surname"] = self.make_entry(left_x, y1 + u(162), col_w, box_h,
                                                 "Enter your surname", size)
        self.fields["suffix"] = self.make_entry(right_x, y1 + u(162), col_w, box_h,
                                                "Jr., Sr., III", size)

        label(left_x, 210, "Address")
        self.fields["address"] = self.make_entry(left_x, y1 + u(222), full_w, box_h,
                                                 "Street, City, Province", size)

        label(left_x, 270, "Birthday")
        label(right_x + u(45), 270, "Sex")
        this_year = datetime.now().year
        years = [str(year) for year in range(this_year - 18, this_year - 70, -1)]
        self.fields["month"] = self.make_menu(left_x, y1 + u(282), u(145), box_h,
                                              frontend.MONTHS, "Month", size)
        self.fields["day"] = self.make_menu(left_x + u(150), y1 + u(282), u(70), box_h,
                                            frontend.DAYS, "Day", size)
        self.fields["year"] = self.make_menu(left_x + u(225), y1 + u(282), u(90), box_h,
                                             years, "Year", size)

        self.sex_var = ctk.StringVar(value="")
        male = ctk.CTkRadioButton(self, text="Male", variable=self.sex_var, value="Male",
                                  font=self.widget_font(size))
        female = ctk.CTkRadioButton(self, text="Female", variable=self.sex_var, value="Female",
                                    font=self.widget_font(size))
        self.put_widget(male, right_x + u(45), y1 + u(288), u(110), u(26))
        self.put_widget(female, right_x + u(165), y1 + u(288), u(120), u(26))

        label(left_x, 336, "Phone Number")
        self.fields["phone"] = self.make_entry(left_x, y1 + u(348), full_w, box_h,
                                               "09XXXXXXXXX", size)

        label(left_x, 396, "Worker Photo (required)")
        self.add_button((left_x, y1 + u(408), left_x + u(180), y1 + u(448)), "UPLOAD PHOTO",
                        FIRE_ORANGE, self.choose_worker_photo, k, 10)
        self.photo_name_item = self.create_text(
            int(left_x + u(198)), int(y1 + u(428)), text="No photo selected", anchor="w",
            fill="#FFCC80", font=("Segoe UI", max(8, u(10))), width=u(360), tags="content")

        self.make_message(cx, y1 + u(458), full_w, u(10))

        self.add_button((left_x, y1 + u(478), left_x + full_w, y1 + u(524)), "REGISTER",
                        FIRE_RED, self.do_register, k, 13)
        self.add_button((left_x, y1 + u(536), left_x + full_w, y1 + u(576)), "BACK",
                        FIRE_GRAY, lambda: self.set_mode("home"), k, 11)

    def do_register(self):
        """Checks the form. If it is correct, it saves the worker and shows the new ID."""
        f = self.fields
        first = f["first"].get().strip()
        middle = f["middle"].get().strip()
        surname = f["surname"].get().strip()
        suffix = f["suffix"].get().strip()
        address = f["address"].get().strip()
        phone = f["phone"].get().strip()
        sex = self.sex_var.get()
        month_text = f["month"].get()
        day_text = f["day"].get()
        year_text = f["year"].get()

        if first == "" or middle == "" or surname == "" or address == "" or phone == "":
            self.show_message("Please complete all required fields.", BAD_COLOR)
            return

        if not self.worker_photo_path:
            self.show_message("Please upload a worker photo before registering.", BAD_COLOR)
            return

        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            self.show_message("Please select your complete birthday (Month, Day, and Year).",
                              BAD_COLOR)
            return

        month_number = frontend.MONTHS.index(month_text) + 1
        try:
            birthday = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            self.show_message("That birthday date does not exist. Please check the day.",
                              BAD_COLOR)
            return

        if sex == "":
            self.show_message("Please select your sex (Male or Female).", BAD_COLOR)
            return

        if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
            self.show_message("Please enter a valid phone number like 09123456789.", BAD_COLOR)
            return

        new_uid = backend.generate_unique_uid()
        try:
            photo_path = backend.store_worker_photo(new_uid, self.worker_photo_path)
        except OSError:
            photo_path = ""
        if not photo_path:
            self.show_message("Could not save the photo. Please choose another image.", BAD_COLOR)
            return

        saved = backend.save_worker(new_uid, first, middle, surname, suffix,
                                    address, birthday.strftime("%m/%d/%Y"), sex, phone, photo_path)
        if not saved:
            backend.delete_worker_photo(photo_path)
            self.show_message("Something went wrong while saving. Please try again.", BAD_COLOR)
            return

        # the bell rang inside save_worker. Now the card shows the new ID.
        self.new_uid = new_uid
        self.set_mode("success")

    # ---------- REGISTRATION COMPLETE ----------
    def build_success(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)

        self.put_text(cx, y1 + u(54), "Registration Successful!", u(20), GOOD_COLOR, bold=True)
        self.put_text(cx, y1 + u(88), "Your worker account has been registered.", u(11),
                      "#FFCC80", width=u(360))
        self.put_text(cx, y1 + u(140), "Your permanent Worker ID is:", u(13), "#FFE0B2")
        self.put_text(cx, y1 + u(194), self.new_uid, u(40), "#FF9800", bold=True)
        self.put_text(cx, y1 + u(256), "Please keep this ID safe.\n"
                      "You will use it to log in every time you report for duty.",
                      u(10), "#FFFFFF", width=u(340))

        half = u(140)
        self.add_button((cx - half, y1 + u(304), cx + half, y1 + u(352)), "GO TO LOGIN",
                        FIRE_RED, self.go_to_login_after_register, k, 13)
        self.add_button((cx - half, y1 + u(364), cx + half, y1 + u(404)), "BACK TO WELCOME",
                        FIRE_GRAY, lambda: self.set_mode("home"), k, 11)

    def go_to_login_after_register(self):
        self.prefill_uid = self.new_uid        # the new ID is already typed in the Login box
        self.set_mode("login", "Registered! Click LOGIN to continue.")



    # =====================================================
    # WORKER CARDS: ABSENCE, LEAVE, INCIDENT, DUTY, INFORMATION
    # (they use the same card, the same buttons, and the same BACK TO MENU as Attendance)
    # =====================================================
    # ---------- ABSENCE ----------
    def build_absence(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.form_header(cx, y1, k, "Report Absence")

        left = cx - u(250)
        full = u(500)
        now = datetime.now()
        years = [str(now.year), str(now.year + 1)]

        self.field_label(left, y1 + u(96), "Date of Absence", k)
        self.fields["month"], self.fields["day"], self.fields["year"] = self.make_date_menus(
            left, y1 + u(108), k, (210, 100, 130), years, now)

        self.field_label(left, y1 + u(162), "Reason", k)
        self.fields["reason"] = self.make_entry(left, y1 + u(174), full, u(36),
                                                "Enter reason for absence", u(12))

        self.field_label(left, y1 + u(224), "Additional Explanation (optional)", k)
        self.fields["explanation"] = self.make_textbox(left, y1 + u(236), full, u(110), u(12))

        self.make_top_message(cx, y1 + u(358), full, u(11))

        self.add_button((left, y1 + u(436), left + full, y1 + u(482)), "SUBMIT ABSENCE",
                        FIRE_RED, self.submit_absence, k, 13)
        self.back_to_menu_button(cx, y1 + u(494), k, 500)

    def submit_absence(self):
        f = self.fields
        uid = self.worker["uid"]
        reason = f["reason"].get().strip()
        explanation = f["explanation"].get("1.0", "end").strip()

        if reason == "":
            self.show_message("Please enter the reason for your absence.", BAD_COLOR)
            return

        absence_day = frontend.read_date(f["month"], f["day"], f["year"])
        if absence_day is None:
            self.show_message("That date does not exist. Please check the day.", BAD_COLOR)
            return

        absence_date = absence_day.strftime("%m/%d/%Y")
        if backend.absence_exists(uid, absence_date):
            self.show_message("Absence Already Filed\n\n"
                              "You already submitted an absence report for this date.", MSG_COLOR)
            return

        date_filed = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        backend.save_absence(uid, absence_date, reason, explanation, date_filed)   # bell rings

        self.show_message("Absence Report Submitted\n\n"
                          "Your absence has been recorded and sent to the Admin.", GOOD_COLOR)
        f["reason"].delete(0, "end")
        f["explanation"].delete("1.0", "end")

    # ---------- LEAVE ----------
    def build_leave(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.form_header(cx, y1, k, "File Leave Request")

        left = cx - u(270)
        right = cx + u(5)
        full = u(540)
        now = datetime.now()
        years = [str(now.year), str(now.year + 1)]

        self.field_label(left, y1 + u(92), "Leave Type", k)
        self.fields["type"] = self.make_menu(left, y1 + u(104), full, u(36), frontend.LEAVE_TYPES,
                                             "Select leave type", u(12))

        self.field_label(left, y1 + u(152), "Start Date", k)
        self.field_label(right, y1 + u(152), "End Date", k)
        self.fields["s_month"], self.fields["s_day"], self.fields["s_year"] = self.make_date_menus(
            left, y1 + u(164), k, (120, 55, 80), years, now)
        self.fields["e_month"], self.fields["e_day"], self.fields["e_year"] = self.make_date_menus(
            right, y1 + u(164), k, (120, 55, 80), years, now)

        self.field_label(left, y1 + u(212), "Reason", k)
        self.fields["reason"] = self.make_textbox(left, y1 + u(224), full, u(90), u(12))

        self.make_top_message(cx, y1 + u(324), full, u(11))

        self.add_button((left, y1 + u(398), left + full, y1 + u(444)), "SUBMIT LEAVE REQUEST",
                        FIRE_RED, self.submit_leave, k, 13)
        self.back_to_menu_button(cx, y1 + u(454), k, 540)

        self.put_text(left, y1 + u(516), "My Recent Leave Requests", u(11), "#FFE0B2",
                      bold=True, anchor="w")
        self.list_item = self.create_text(left, y1 + u(534), text="", anchor="nw", fill="#FFFFFF",
                                          font=("Segoe UI", max(8, u(10))), width=full,
                                          justify="left", tags="content")
        self.refresh_leave_list()

    def refresh_leave_list(self):
        rows = backend.get_worker_leaves(self.worker["uid"])
        if len(rows) == 0:
            text = "No leave requests yet."
        else:
            text = "\n".join(f"{row[0]}:  {row[1]} to {row[2]}   -   {row[3]}" for row in rows)
        if self.list_item is not None:
            self.itemconfig(self.list_item, text=text)

    def submit_leave(self):
        f = self.fields
        uid = self.worker["uid"]
        leave_type = f["type"].get()
        reason = f["reason"].get("1.0", "end").strip()

        if leave_type == "Select leave type":
            self.show_message("Please select a leave type.", BAD_COLOR)
            return

        start_date = frontend.read_date(f["s_month"], f["s_day"], f["s_year"])
        end_date = frontend.read_date(f["e_month"], f["e_day"], f["e_year"])

        if start_date is None:
            self.show_message("The start date does not exist. Please check the day.", BAD_COLOR)
            return
        if end_date is None:
            self.show_message("The end date does not exist. Please check the day.", BAD_COLOR)
            return
        if end_date < start_date:
            self.show_message("The end date cannot be before the start date.", BAD_COLOR)
            return
        if reason == "":
            self.show_message("Please enter the reason for your leave.", BAD_COLOR)
            return

        start_text = start_date.strftime("%m/%d/%Y")
        end_text = end_date.strftime("%m/%d/%Y")

        if backend.leave_exists(uid, start_text, end_text):
            self.show_message("Leave Request Already Sent\n\n"
                              "You already have a request for these dates.", MSG_COLOR)
            return

        date_filed = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        backend.save_leave(uid, leave_type, start_text, end_text, reason, date_filed)  # bell rings

        self.show_message("Leave Request Submitted\n\n"
                          "Your request has been sent to the Admin for review.", GOOD_COLOR)
        f["reason"].delete("1.0", "end")
        self.refresh_leave_list()

    # ---------- INCIDENT REPORT ----------
    def build_incident(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.form_header(cx, y1, k, "Incident Report")

        left = cx - u(325)
        right = cx + u(10)
        col = u(315)
        full = u(640)
        now = datetime.now()
        years = [str(now.year), str(now.year - 1)]

        self.field_label(left, y1 + u(88), "Incident Type", k)
        self.field_label(right, y1 + u(88), "Date of Incident", k)
        self.fields["type"] = self.make_menu(left, y1 + u(100), col, u(36),
                                             frontend.INCIDENT_TYPES, "Select incident type", u(12))
        self.fields["month"], self.fields["day"], self.fields["year"] = self.make_date_menus(
            right, y1 + u(100), k, (150, 70, 85), years, now)

        self.field_label(left, y1 + u(148), "Time of Incident", k)
        self.field_label(right, y1 + u(148), "Location", k)
        hour = self.make_menu(left, y1 + u(160), u(90), u(36), frontend.HOURS, "1", u(12))
        minute = self.make_menu(left + u(95), y1 + u(160), u(90), u(36), frontend.MINUTES, "00", u(12))
        am_pm = self.make_menu(left + u(190), y1 + u(160), u(90), u(36), frontend.AM_PM_LIST, "AM", u(12))
        frontend.set_time_menus(hour, minute, am_pm, now)
        self.fields["hour"], self.fields["minute"], self.fields["am_pm"] = hour, minute, am_pm
        self.fields["location"] = self.make_entry(right, y1 + u(160), col, u(36),
                                                  "Street, Barangay, City", u(12))

        self.field_label(left, y1 + u(208), "Personnel Involved (optional)", k)
        self.fields["personnel"] = self.make_entry(left, y1 + u(220), full, u(36),
                                                   "Names of the firefighters involved", u(12))

        self.field_label(left, y1 + u(268), "Description", k)
        self.fields["description"] = self.make_textbox(left, y1 + u(280), full, u(80), u(12))
        self.field_label(left, y1 + u(368), "Actions Taken (optional)", k)
        self.fields["actions"] = self.make_textbox(left, y1 + u(380), full, u(64), u(12))
        self.field_label(left, y1 + u(452), "Additional Information (optional)", k)
        self.fields["additional"] = self.make_textbox(left, y1 + u(464), full, u(64), u(12))

        self.make_top_message(cx, y1 + u(536), full, u(11))

        self.add_button((left, y1 + u(612), left + full, y1 + u(658)), "SUBMIT INCIDENT REPORT",
                        FIRE_RED, self.submit_incident, k, 13)
        self.back_to_menu_button(cx, y1 + u(666), k, 640)

        self.put_text(left, y1 + u(724), "My Recent Incident Reports", u(11), "#FFE0B2",
                      bold=True, anchor="w")
        self.list_item = self.create_text(left, y1 + u(742), text="", anchor="nw", fill="#FFFFFF",
                                          font=("Segoe UI", max(8, u(10))), width=full,
                                          justify="left", tags="content")
        self.refresh_incident_list()

    def refresh_incident_list(self):
        rows = backend.get_worker_incidents(self.worker["uid"])
        if len(rows) == 0:
            text = "No incident reports yet."
        else:
            text = "\n".join(f"INC-{row[0]:04d}:  {row[1]}  -  {row[2]}  -  {row[3]}" for row in rows)
        if self.list_item is not None:
            self.itemconfig(self.list_item, text=text)

    def submit_incident(self):
        f = self.fields
        uid = self.worker["uid"]
        incident_type = f["type"].get()
        location = f["location"].get().strip()
        personnel = f["personnel"].get().strip()
        description = f["description"].get("1.0", "end").strip()
        actions = f["actions"].get("1.0", "end").strip()
        additional = f["additional"].get("1.0", "end").strip()

        if incident_type == "Select incident type":
            self.show_message("Please select an incident type.", BAD_COLOR)
            return

        incident_day = frontend.read_date(f["month"], f["day"], f["year"])
        if incident_day is None:
            self.show_message("That date does not exist. Please check the day.", BAD_COLOR)
            return

        hour_number = int(f["hour"].get())
        minute_number = int(f["minute"].get())
        am_pm = f["am_pm"].get()
        if am_pm == "PM" and hour_number != 12:
            hour_number = hour_number + 12
        if am_pm == "AM" and hour_number == 12:
            hour_number = 0

        incident_moment = incident_day.replace(hour=hour_number, minute=minute_number)
        if incident_moment > datetime.now():
            self.show_message("The incident date and time cannot be in the future.", BAD_COLOR)
            return
        if location == "":
            self.show_message("Please enter the location of the incident.", BAD_COLOR)
            return
        if description == "":
            self.show_message("Please enter a description of the incident.", BAD_COLOR)
            return

        date_time_text = incident_moment.strftime("%m/%d/%Y %I:%M %p")
        date_reported = datetime.now().strftime("%m/%d/%Y %I:%M %p")

        new_id = backend.save_incident(uid, date_time_text, incident_type, location, personnel,
                                       description, actions, additional, date_reported)  # bell rings

        self.show_message("Incident Report Submitted Successfully.\n\n"
                          f"Report number: INC-{new_id:04d}\n"
                          "Your report has been sent to the Admin.", GOOD_COLOR)
        f["location"].delete(0, "end")
        f["personnel"].delete(0, "end")
        for name in ("description", "actions", "additional"):
            f[name].delete("1.0", "end")
        self.refresh_incident_list()

    # ---------- MY DUTY / SHIFT ----------
    def build_duty(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.form_header(cx, y1, k, "My Duty / Shift")

        left = cx - u(260)
        full = u(520)
        uid = self.worker["uid"]
        records = backend.get_worker_duty_records(uid)
        today = datetime.now().date()
        eligible = []
        for record in records:
            try:
                duty_day = datetime.strptime(record["duty_date"], "%m/%d/%Y").date()
            except ValueError:
                continue
            if duty_day <= today:
                eligible.append(record)

        self.put_text(left, y1 + u(82), "Report an assigned duty", u(13), "#FFE0B2",
                      bold=True, anchor="w")
        report_choices = {}
        labels = []
        for record in eligible:
            label = (f"{record['duty_date']} — {record['shift']}: "
                     f"{record['assignment']}")
            labels.append(label)
            report_choices[label] = record["duty_id"]

        if labels:
            selected_duty = self.make_menu(left, y1 + u(106), full, u(36), labels,
                                           labels[0], u(11))
            selected_report = self.make_menu(left, y1 + u(153), full, u(36),
                                             ["Select status", "Done", "Not yet"],
                                             "Select status", u(11))

            def submit_report():
                label = selected_duty.get()
                report = selected_report.get()
                if report not in ("Done", "Not yet"):
                    self.show_message("Select Done or Not yet before submitting.", BAD_COLOR)
                    return
                if backend.submit_duty_report(uid, report_choices[label], report):
                    self.set_mode("duty", "Report sent to Admin for verification.")
                else:
                    self.show_message("This duty report could not be saved.", BAD_COLOR)

            self.add_button((left, y1 + u(198), left + full, y1 + u(238)),
                            "SUBMIT DUTY REPORT", FIRE_RED, submit_report, k, 11)
        else:
            self.create_text(left, y1 + u(108), text="No current or past duties to report.",
                             anchor="nw", fill="#FFFFFF", font=("Segoe UI", max(8, u(12))),
                             width=full, tags="content")

        self.put_text(left, y1 + u(252), "Recent Assignments", u(13), "#FFE0B2",
                      bold=True, anchor="w")
        lines = []
        for record in records[:5]:
            verification = record.get("verification_status", "")
            result = record.get("completion_status", "")
            if result:
                status = result
            elif verification == "Pending":
                status = "Awaiting Admin Verification"
            else:
                status = "Not reported"
            lines.append(f"{record['duty_date']}  |  {record['shift']}  |  "
                         f"{record['assignment']}  |  {status}")
        recent_text = "\n".join(lines) if lines else "No assigned duties yet."
        self.create_text(left, y1 + u(278), text=recent_text, anchor="nw", fill="#FFFFFF",
                         font=("Segoe UI", max(8, u(11))), width=full, justify="left",
                         tags="content")

        self.back_to_menu_button(cx, y1 + u(588), k, 500)

    # ---------- MY INFORMATION ----------
    def build_information(self):
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        self.form_header(cx, y1, k, "My Information")

        left = cx - u(220)
        record = backend.get_full_worker(self.worker["uid"])
        if record is None:
            self.put_text(cx, y1 + u(150), "Your record could not be found.", u(13), BAD_COLOR, bold=True)
        else:
            photo_path = backend.get_worker_photo_path(record.get("photo_path", ""))
            photo_size = u(130)
            photo_x = int(cx - photo_size / 2)
            photo_y = int(y1 + u(78))
            if photo_path:
                try:
                    with Image.open(photo_path) as source_photo:
                        profile_photo = ImageOps.fit(source_photo.convert("RGB"),
                                                     (max(1, photo_size), max(1, photo_size)))
                    self.show_picture(photo_x, photo_y, profile_photo, "content")
                    self.create_rectangle(photo_x, photo_y, photo_x + photo_size, photo_y + photo_size,
                                          outline="#FFBE78", width=max(1, u(2)), tags="content")
                except Exception:
                    self.put_text(cx, photo_y + photo_size // 2, "Photo unavailable", u(10),
                                  BAD_COLOR, width=u(160))
            else:
                self.put_text(cx, photo_y + photo_size // 2, "No photo available", u(10),
                              "#FFCC80", width=u(160))
            rows = [("Full Name", backend.make_name(record)), ("Sex", record["sex"]),
                    ("Birthday", record["birthday"]), ("Phone Number", record["phone_number"]),
                    ("Address", record["address"]), ("Registered", record["registration_date"]),
                    ("Status", record["status"])]
            y = 226
            for caption, value in rows:
                self.create_text(left, y1 + u(y), text=caption, anchor="nw", fill="#FFB300",
                                 font=("Segoe UI", max(8, u(11)), "bold"), tags="content")
                self.create_text(left + u(130), y1 + u(y), text=value if value else "-", anchor="nw",
                                 fill="#FFFFFF", font=("Segoe UI", max(8, u(12))),
                                 width=u(310), justify="left", tags="content")
                y = y + 44

        self.make_message(cx, y1 + u(566), u(430), u(10))
        button_w = u(205)
        button_gap = u(16)
        buttons_left = cx - (2 * button_w + button_gap) // 2
        self.add_button((buttons_left, y1 + u(592), buttons_left + button_w, y1 + u(632)),
                        "EDIT INFORMATION", FIRE_ORANGE,
                        lambda: self.set_mode("edit_information"), k, 10)
        self.add_button((buttons_left + button_w + button_gap, y1 + u(592),
                         buttons_left + 2 * button_w + button_gap, y1 + u(632)),
                        "BACK TO MENU", FIRE_GRAY, lambda: self.set_mode("menu"), k, 10)

    # ---------- EDIT MY INFORMATION ----------
    def build_edit_information(self):
        self.worker_photo_path = ""
        x1, y1, cx, k = self.geo()
        u = lambda value: int(value * k)
        record = backend.get_full_worker(self.worker["uid"])
        if record is None:
            self.put_text(cx, y1 + u(100), "Your worker record could not be found.",
                          u(13), BAD_COLOR, bold=True, width=u(500))
            self.add_button((cx - u(160), y1 + u(180), cx + u(160), y1 + u(224)), "BACK",
                            FIRE_GRAY, lambda: self.set_mode("information"), k, 11)
            return

        self.put_text(cx, y1 + u(34), "Edit My Information", u(20), "#FFE0B2", bold=True)
        self.put_text(cx, y1 + u(62), "Worker ID, registration date, and account status are managed by the system.",
                      u(10), "#FFCC80", width=u(520))
        left_x = cx - u(280)
        right_x = cx + u(5)
        col_w = u(275)
        full_w = u(560)
        box_h = u(36)
        size = u(12)

        def label(x, top, text):
            self.create_text(int(x), y1 + u(top), text=text, anchor="w", fill="#FFE0B2",
                             font=("Segoe UI", max(8, u(10)), "bold"), tags="content")

        label(left_x, 90, "First Name")
        label(right_x, 90, "Middle Name")
        self.fields["first"] = self.make_entry(left_x, y1 + u(102), col_w, box_h, "First name", size)
        self.fields["first"].insert(0, record["first_name"])
        self.fields["middle"] = self.make_entry(right_x, y1 + u(102), col_w, box_h, "Middle name", size)
        self.fields["middle"].insert(0, record["middle_name"])

        label(left_x, 150, "Surname")
        label(right_x, 150, "Suffix (optional)")
        self.fields["surname"] = self.make_entry(left_x, y1 + u(162), col_w, box_h, "Surname", size)
        self.fields["surname"].insert(0, record["surname"])
        self.fields["suffix"] = self.make_entry(right_x, y1 + u(162), col_w, box_h, "Jr., Sr., III", size)
        self.fields["suffix"].insert(0, record["suffix"])

        label(left_x, 210, "Address")
        self.fields["address"] = self.make_entry(left_x, y1 + u(222), full_w, box_h,
                                                 "Street, City, Province", size)
        self.fields["address"].insert(0, record["address"])

        label(left_x, 270, "Birthday")
        label(right_x + u(45), 270, "Sex")
        years = [str(year) for year in range(datetime.now().year - 18, datetime.now().year - 101, -1)]
        try:
            birthday = datetime.strptime(record["birthday"], "%m/%d/%Y")
            start_month = frontend.MONTHS[birthday.month - 1]
            start_day = str(birthday.day)
            start_year = str(birthday.year)
        except (ValueError, IndexError):
            start_month, start_day, start_year = "Month", "Day", "Year"
        self.fields["month"] = self.make_menu(left_x, y1 + u(282), u(145), box_h,
                                              frontend.MONTHS, start_month, size)
        self.fields["day"] = self.make_menu(left_x + u(150), y1 + u(282), u(70), box_h,
                                            frontend.DAYS, start_day, size)
        self.fields["year"] = self.make_menu(left_x + u(225), y1 + u(282), u(90), box_h,
                                             years, start_year, size)
        self.sex_var = ctk.StringVar(value=record["sex"])
        male = ctk.CTkRadioButton(self, text="Male", variable=self.sex_var, value="Male",
                                  font=self.widget_font(size))
        female = ctk.CTkRadioButton(self, text="Female", variable=self.sex_var, value="Female",
                                    font=self.widget_font(size))
        self.put_widget(male, right_x + u(45), y1 + u(288), u(110), u(26))
        self.put_widget(female, right_x + u(165), y1 + u(288), u(120), u(26))

        label(left_x, 336, "Phone Number")
        self.fields["phone"] = self.make_entry(left_x, y1 + u(348), full_w, box_h, "09XXXXXXXXX", size)
        self.fields["phone"].insert(0, record["phone_number"])

        label(left_x, 396, "Worker Photo (optional)")
        self.add_button((left_x, y1 + u(408), left_x + u(180), y1 + u(448)), "CHANGE PHOTO",
                        FIRE_ORANGE, self.choose_worker_photo, k, 10)
        current_photo = os.path.basename(record.get("photo_path", "")) or "Current photo will be kept"
        self.photo_name_item = self.create_text(
            int(left_x + u(198)), int(y1 + u(428)), text=current_photo, anchor="w",
            fill="#FFCC80", font=("Segoe UI", max(8, u(10))), width=u(360), tags="content")

        self.make_message(cx, y1 + u(458), full_w, u(10))
        self.add_button((left_x, y1 + u(478), left_x + full_w, y1 + u(524)), "SAVE CHANGES",
                        FIRE_RED, self.save_worker_information, k, 13)
        self.add_button((left_x, y1 + u(536), left_x + full_w, y1 + u(576)), "CANCEL",
                        FIRE_GRAY, lambda: self.set_mode("information"), k, 11)

    def save_worker_information(self):
        f = self.fields
        first = f["first"].get().strip()
        middle = f["middle"].get().strip()
        surname = f["surname"].get().strip()
        suffix = f["suffix"].get().strip()
        address = f["address"].get().strip()
        phone = f["phone"].get().strip()
        sex = self.sex_var.get()
        month_text, day_text, year_text = f["month"].get(), f["day"].get(), f["year"].get()

        if not all((first, middle, surname, address, phone)):
            self.show_message("Please complete all required fields.", BAD_COLOR)
            return
        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            self.show_message("Please select your complete birthday.", BAD_COLOR)
            return
        try:
            birthday = datetime(int(year_text), frontend.MONTHS.index(month_text) + 1, int(day_text))
        except (ValueError, IndexError):
            self.show_message("That birthday date does not exist. Please check the day.", BAD_COLOR)
            return
        if sex not in ("Male", "Female"):
            self.show_message("Please select Male or Female.", BAD_COLOR)
            return
        if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
            self.show_message("Please enter a valid phone number like 09123456789.", BAD_COLOR)
            return

        uid = self.worker["uid"]
        old_record = backend.get_full_worker(uid)
        if old_record is None:
            self.show_message("Your worker record could not be found.", BAD_COLOR)
            return
        old_photo_path = old_record.get("photo_path", "")
        new_photo_path = old_photo_path
        if self.worker_photo_path:
            try:
                new_photo_path = backend.store_worker_photo(uid, self.worker_photo_path)
            except OSError:
                new_photo_path = ""
            if not new_photo_path:
                self.show_message("Could not save the new photo. Please choose another image.", BAD_COLOR)
                return

        try:
            updated = backend.update_worker(
                uid, first, middle, surname, suffix, address, birthday.strftime("%m/%d/%Y"),
                sex, phone, new_photo_path if self.worker_photo_path else None)
        except OSError:
            updated = False
        if not updated:
            if self.worker_photo_path and new_photo_path != old_photo_path:
                backend.delete_worker_photo(new_photo_path)
            self.show_message("Could not save your changes. Please try again.", BAD_COLOR)
            return

        if self.worker_photo_path and old_photo_path and old_photo_path != new_photo_path:
            backend.delete_worker_photo(old_photo_path)
        updated_record = backend.get_full_worker(uid)
        if updated_record:
            self.worker["full_name"] = backend.make_name(updated_record)
        self.set_mode("information", "Your information was updated.")


# =====================================================
# THE MAIN WINDOW
# =====================================================
class App(ctk.CTk):
    """The one main window for the whole system."""

    def __init__(self):
        super().__init__()
        self.title(SYSTEM_NAME)
        self.geometry(f"{START_W}x{START_H}")
        self.minsize(950, 600)
        self._about_return_admin = False

        # Screen 1: the welcome screen. Login, Register, the Worker Menu and EVERY worker
        # screen live inside its animated glass card. There is only ONE worker menu.
        self.welcome = WelcomeScreen(self, self.go)
        self.welcome.pack(fill="both", expand=True)

        # Screen 2: the Admin screen (hidden until the Admin button is clicked)
        self.admin_screen, self.open_admin = frontend.build_admin_screen(self, self.show_welcome)

        self.after(100, self.maximize)

    def maximize(self):
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

    def go(self, where):
        """Runs when the Admin button is clicked."""
        if where == "admin":
            self.welcome.pack_forget()
            self.admin_screen.pack(fill="both", expand=True)
            self.open_admin()
        elif where == "about":
            self._about_return_admin = self.admin_screen.winfo_manager() == "pack"
            if self._about_return_admin:
                self.admin_screen.pack_forget()
            self.welcome.pack(fill="both", expand=True)
            self.welcome.set_mode("about")
        elif where == "about_back":
            if self._about_return_admin:
                self._about_return_admin = False
                self.welcome.pack_forget()
                self.admin_screen.pack(fill="both", expand=True)
                self.open_admin()
            else:
                self.welcome.set_mode("home")

    def show_welcome(self):
        """Comes back from the Admin screen to the first welcome card."""
        self.admin_screen.pack_forget()
        self.welcome.pack(fill="both", expand=True)
        self.welcome.reset_home()


if __name__ == "__main__":
    app = App()
    app.mainloop()
