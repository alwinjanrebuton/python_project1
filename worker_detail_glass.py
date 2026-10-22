# worker_detail_glass.py
# The GLASS version of the Admin's "Worker Details" page (what opens after clicking VIEW)
# and the "Edit Worker Information" page.
#
# It uses the same blurred background, glass panels and glass buttons as the Dashboard
# and the Workers list. All the saving and reading of data is still done by backend.py.
#
# frontend.py calls create_worker_detail_pages() once, inside build_admin_screen.
# Put this file in the same folder as frontend.py and backend.py.

from datetime import datetime

import customtkinter as ctk
from PIL import Image, ImageOps

import backend
import frontend as fe


def create_worker_detail_pages(content, all_pages, screen, show_page, go_back_to_list):
    """Builds the glass Details page and the glass Edit page.
    content         = the area on the right of the Admin sidebar
    all_pages       = the Admin's list of pages (so show_page can hide them)
    screen          = the Admin screen (the glass background needs it)
    show_page       = the Admin function that shows one page
    go_back_to_list = the Admin function that returns to the worker list
    It gives back show_worker_detail(uid), which the VIEW button uses."""

    state = {"uid": "", "confirming": False}      # which worker is open

    detail_page = fe.GlassCanvas(content, screen, lambda canvas, W, H: draw_detail(canvas, W, H))
    edit_page = fe.GlassCanvas(content, screen, lambda canvas, W, H: draw_edit(canvas, W, H))
    all_pages.append(detail_page)
    all_pages.append(edit_page)

    # =====================================================
    # DETAILS PAGE
    # =====================================================
    # These work like labels: .configure(text=..., text_color=...) writes on the glass
    id_label = fe.CanvasText()
    status_label = fe.CanvasText()
    message_label = fe.CanvasText()

    info_captions = ["Full Name", "Sex", "Birthday", "Phone Number", "Address", "Registration Date"]
    info_labels = [fe.CanvasText() for caption in info_captions]

    count_captions = ["Attendance records", "Absence reports", "Leave requests",
                      "Incident reports", "Duties assigned"]
    count_labels = [fe.CanvasText("0") for caption in count_captions]

    history_titles = ["Recent Attendance", "Recent Absence Reports", "Recent Leave Requests",
                      "Recent Incident Reports", "Recent Duties"]
    history_labels = [fe.CanvasText() for title in history_titles]

    # ----- the buttons (their width fits their text, so the text is never cut) -----
    button_font = ("Arial", 12, "bold")
    button_h = fe.fpx(12) + fe.px(30)

    def button_width(*texts):
        widest = 0
        for text in texts:
            widest = max(widest, fe.text_width(text, 12))
        return widest + fe.px(70)

    back_w = button_width("< BACK TO LIST")
    edit_w = button_width("EDIT INFORMATION")
    status_w = button_width("DEACTIVATE WORKER", "REACTIVATE WORKER", "CLICK AGAIN TO CONFIRM")

    back_button = fe.GlassButton(detail_page, text="< BACK TO LIST", width=back_w, height=button_h,
                                 font=button_font, fg_color=fe.EMBER_GRAY, command=go_back_to_list)
    edit_button = fe.GlassButton(detail_page, text="EDIT INFORMATION", width=edit_w, height=button_h,
                                 font=button_font, fg_color=fe.ORANGE,
                                 command=lambda: start_edit())
    status_button = fe.GlassButton(detail_page, text="", width=status_w, height=button_h,
                                   font=button_font, command=lambda: toggle_status())

    def draw_detail(canvas, W, H):
        """Paints the Details page. It runs every time the window size changes."""
        m = fe.px(30)
        title_y = fe.fpx(26) // 2 + fe.px(14)
        canvas.create_text(fe.px(36), title_y, text="Worker Details", anchor="w",
                           fill=fe.WHITE, font=("Arial", 26, "bold"))
        canvas.create_window(W - m - back_w, title_y - button_h // 2, window=back_button,
                             anchor="nw", width=back_w, height=button_h)

        y0 = title_y * 2 + fe.px(6)
        gap = fe.px(20)
        pad = fe.px(30)

        # ----- the top panels: worker information (left) and activity numbers (right) -----
        left_w = int((W - 2 * m - gap) * 0.58)
        row_h = fe.fpx(15) + fe.px(16)
        big = fe.fpx(34)
        small = fe.fpx(16)
        message_h = fe.fpx(14) * 2 + fe.px(8)

        panel_h = (pad + big + fe.px(6) + small + fe.px(18) + len(info_captions) * row_h +
                   fe.px(18) + button_h + fe.px(12) + message_h + pad)
        panel_h = min(panel_h, H - y0 - m - gap - fe.px(260))     # keep room for the history

        canvas.glass((m, y0, m + left_w, y0 + panel_h), 22, 140)
        canvas.glass((m + left_w + gap, y0, W - m, y0 + panel_h), 22, 140)

        # ----- left panel -----
        x = m + pad
        y = y0 + pad
        id_label.attach(canvas, x, y + big // 2, anchor="w", fill=fe.ORANGE,
                        font=("Arial", 34, "bold"))
        y = y + big + fe.px(6)
        status_label.attach(canvas, x, y + small // 2, anchor="w", fill=fe.WHITE,
                            font=("Arial", 16, "bold"))
        y = y + small + fe.px(18)

        caption_w = fe.text_width("Registration Date", 14) + fe.px(30)
        record_for_photo = backend.get_full_worker(state["uid"]) if state["uid"] else None
        photo_size = fe.px(480)
        photo_x = m + left_w - pad - photo_size
        photo_y = y0 + pad
        photo_path = backend.get_worker_photo_path(record_for_photo.get("photo_path", "")) if record_for_photo else ""
        value_w = max(120, left_w - 2 * pad - caption_w - photo_size - fe.px(18))
        if photo_path:
            try:
                with Image.open(photo_path) as source_photo:
                    profile_photo = ImageOps.fit(source_photo.convert("RGB"), (photo_size, photo_size))
                canvas.show_picture(photo_x, photo_y, profile_photo)
                canvas.create_rectangle(photo_x, photo_y, photo_x + photo_size, photo_y + photo_size,
                                        outline=fe.BORDER, width=fe.px(2))
            except Exception:
                canvas.create_text(photo_x + photo_size // 2, photo_y + photo_size // 2,
                                   text="Photo unavailable", fill=fe.TEXT_MUTED,
                                   font=("Arial", 11), width=photo_size)
        else:
            canvas.create_text(photo_x + photo_size // 2, photo_y + photo_size // 2,
                               text="No photo", fill=fe.TEXT_MUTED, font=("Arial", 11))
        for index in range(len(info_captions)):
            middle = y + row_h // 2
            canvas.create_text(x, middle, text=info_captions[index], anchor="w",
                               fill=fe.AMBER, font=("Arial", 14, "bold"))
            info_labels[index].attach(canvas, x + caption_w, middle, anchor="w", fill=fe.WHITE,
                                      font=("Arial", 15), width=value_w, justify="left")
            y = y + row_h

        y = y + fe.px(18)
        canvas.create_window(x, y, window=edit_button, anchor="nw", width=edit_w, height=button_h)
        canvas.create_window(x + edit_w + fe.px(14), y, window=status_button, anchor="nw",
                             width=status_w, height=button_h)
        message_label.attach(canvas, x, y + button_h + fe.px(12), anchor="nw", fill=fe.WHITE,
                             font=("Arial", 14, "bold"), width=left_w - 2 * pad, justify="left")

        # ----- right panel: the activity numbers -----
        right_x = m + left_w + gap + pad
        right_edge = W - m - pad
        y = y0 + pad
        canvas.create_text(right_x, y + fe.fpx(18) // 2, text="Activity Summary", anchor="w",
                           fill=fe.AMBER, font=("Arial", 18, "bold"))
        y = y + fe.fpx(18) + fe.px(22)
        count_row = row_h + fe.px(14)
        for index in range(len(count_captions)):
            middle = y + count_row // 2
            canvas.create_text(right_x, middle, text=count_captions[index], anchor="w",
                               fill=fe.WHITE, font=("Arial", 15))
            count_labels[index].attach(canvas, right_edge, middle, anchor="e", fill=fe.WHITE,
                                       font=("Arial", 20, "bold"))
            line_y = y + count_row - 1
            canvas.create_line(right_x, line_y, right_edge, line_y, fill="#5A3026")
            y = y + count_row

        # ----- bottom panel: the recent history in 5 columns -----
        top = y0 + panel_h + gap
        canvas.glass((m, top, W - m, H - m), 22, 130)
        canvas.create_text(m + pad, top + fe.fpx(18) // 2 + fe.px(18), text="Worker Activity / History",
                           anchor="w", fill=fe.AMBER, font=("Arial", 18, "bold"))

        column_w = (W - 2 * m - 2 * pad) // len(history_titles)
        column_top = top + fe.fpx(18) + fe.px(48)
        for index in range(len(history_titles)):
            column_x = m + pad + index * column_w
            canvas.create_text(column_x, column_top, text=history_titles[index], anchor="w",
                               fill=fe.WHITE, font=("Arial", 14, "bold"))
            history_labels[index].attach(canvas, column_x, column_top + fe.fpx(14),
                                         anchor="nw", fill=fe.TEXT, font=("Arial", 12),
                                         width=column_w - fe.px(24), justify="left")

    def fill_history(uid):
        """Fills the numbers and the 5 history lists."""
        history = backend.get_worker_history(uid)

        counts = [len(history["attendance"]), len(history["absences"]), len(history["leaves"]),
                  len(history["incidents"]), len(history["duties"])]
        for index in range(len(counts)):
            count_labels[index].configure(text=str(counts[index]))

        lines = []
        for record in history["attendance"][:5]:
            lines.append(f"{record['date']}   In: {record['time_in']}   "
                         f"Out: {fe.show_or_dash(record['time_out'])}   {record['status']}")
        history_labels[0].configure(text=fe.join_or_none(lines, "No attendance records yet."))

        lines = []
        for record in history["absences"][:5]:
            lines.append(f"{record['absence_date']}   {record['reason']}")
        history_labels[1].configure(text=fe.join_or_none(lines, "No absence reports yet."))

        lines = []
        for record in history["leaves"][:5]:
            lines.append(f"{record['leave_type']}:  {record['start_date']} to "
                         f"{record['end_date']}   -   {record['status']}")
        history_labels[2].configure(text=fe.join_or_none(lines, "No leave requests yet."))

        lines = []
        for record in history["incidents"][:5]:
            lines.append(f"INC-{int(record['incident_id']):04d}   {record['incident_type']}   -   "
                         f"{record['date_time']}   -   {record['status']}")
        history_labels[3].configure(text=fe.join_or_none(lines, "No incident reports yet."))

        lines = []
        for record in history["duties"][:5]:
            lines.append(f"{record['duty_date']}   {record['shift']} ({record['start_time']} - "
                         f"{record['end_time']})   -   {record['assignment']}")
        history_labels[4].configure(text=fe.join_or_none(lines, "No duties assigned yet."))

    def fill_detail():
        """Fills the Details page with the open worker's information."""
        uid = state["uid"]
        record = backend.get_full_worker(uid)
        if record is None:
            return

        id_label.configure(text=uid)

        if record["status"] == "Active":
            status_label.configure(text="Status: ACTIVE", text_color=fe.OK_GREEN)
            status_button.configure(text="DEACTIVATE WORKER", fg_color=fe.RED)
        else:
            status_label.configure(text="Status: INACTIVE", text_color=fe.BAD_RED)
            status_button.configure(text="REACTIVATE WORKER", fg_color=fe.GREEN_BTN)

        state["confirming"] = False

        values = [backend.make_name(record), record["sex"], record["birthday"],
                  record["phone_number"], record["address"], record["registration_date"]]
        for index in range(len(values)):
            info_labels[index].configure(text=fe.shorten(fe.show_or_dash(values[index]), 70))

        fill_history(uid)

    def show_worker_detail(uid):
        """Opens the Details page for one worker (the VIEW button calls this)."""
        record = backend.get_full_worker(uid)
        if record is None:
            return

        state["uid"] = uid
        message_label.configure(text="")
        fill_detail()
        show_page(detail_page)
        detail_page.redraw()

    def toggle_status():
        """Deactivates an Active worker (after a second click to confirm) or reactivates one."""
        uid = state["uid"]
        record = backend.get_full_worker(uid)
        if record is None:
            return

        if record["status"] == "Active":
            if not state["confirming"]:
                state["confirming"] = True
                status_button.configure(text="CLICK AGAIN TO CONFIRM")
                message_label.configure(
                    text="This worker will no longer be able to log in. All records are kept.",
                    text_color=fe.WARN_ORANGE)
                return

            backend.set_worker_status(uid, "Inactive")
            fill_detail()
            message_label.configure(text="Worker deactivated.", text_color=fe.BAD_RED)
        else:
            backend.set_worker_status(uid, "Active")
            fill_detail()
            message_label.configure(text="Worker reactivated.", text_color=fe.OK_GREEN)

    # =====================================================
    # EDIT PAGE
    # =====================================================
    edit_uid_label = fe.CanvasText()
    edit_message_label = fe.CanvasText()

    widget_font = fe.get_widget_font()

    def make_entry(placeholder):
        entry = ctk.CTkEntry(edit_page, placeholder_text=placeholder, font=widget_font)
        return entry

    def make_menu(values, start):
        menu = ctk.CTkOptionMenu(edit_page, values=values, font=widget_font,
                                 dropdown_font=widget_font)
        menu.set(start)
        return menu

    edit_first = make_entry("Enter first name")
    edit_middle = make_entry("Enter middle name")
    edit_surname = make_entry("Enter surname")
    edit_suffix = make_entry("Jr., Sr., III")
    edit_address = make_entry("Street, City, Province")
    edit_phone = make_entry("09XXXXXXXXX")

    current_year = datetime.now().year
    birthday_years = []
    for year in range(current_year - 16, current_year - 81, -1):      # newest year first
        birthday_years.append(str(year))

    edit_month = make_menu(fe.MONTHS, "Month")
    edit_day = make_menu(fe.DAYS, "Day")
    edit_year = make_menu(birthday_years, "Year")

    edit_sex = ctk.StringVar(value="")
    edit_male = ctk.CTkRadioButton(edit_page, text="Male", variable=edit_sex, value="Male",
                                   font=widget_font, bg_color=fe.BG_PANEL)
    edit_female = ctk.CTkRadioButton(edit_page, text="Female", variable=edit_sex, value="Female",
                                     font=widget_font, bg_color=fe.BG_PANEL)

    save_w = button_width("SAVE CHANGES")
    cancel_w = button_width("CANCEL")
    save_button = fe.GlassButton(edit_page, text="SAVE CHANGES", width=save_w, height=button_h,
                                 font=button_font, fg_color=fe.RED,
                                 command=lambda: save_changes())
    cancel_button = fe.GlassButton(edit_page, text="CANCEL", width=cancel_w, height=button_h,
                                   font=button_font, fg_color=fe.EMBER_GRAY,
                                   command=lambda: show_page(detail_page))

    def draw_edit(canvas, W, H):
        """Paints the Edit page: a glass panel with the form on it."""
        m = fe.px(30)
        title_y = fe.fpx(26) // 2 + fe.px(14)
        canvas.create_text(fe.px(36), title_y, text="Edit Worker Information", anchor="w",
                           fill=fe.WHITE, font=("Arial", 26, "bold"))
        y0 = title_y * 2 + fe.px(6)

        pad = fe.px(34)
        panel_w = min(W - 2 * m, 1000)
        left = (W - panel_w) // 2
        inner = panel_w - 2 * pad
        gap = fe.px(20)
        col_w = (inner - gap) // 2

        box_h = fe.ctl(34)
        label_h = fe.fpx(14) + fe.px(6)
        block = label_h + box_h + fe.px(16)
        header = fe.fpx(16) + fe.px(22)
        message_h = fe.fpx(14) * 2 + fe.px(8)

        panel_h = pad + header + 4 * block + message_h + button_h + pad
        canvas.glass((left, y0, left + panel_w, y0 + panel_h), 22, 140)

        x1 = left + pad                      # left column
        x2 = x1 + col_w + gap                # right column
        y = y0 + pad

        edit_uid_label.attach(canvas, x1, y + fe.fpx(16) // 2, anchor="w", fill=fe.ORANGE,
                              font=("Arial", 16, "bold"))
        y = y + header

        def label(x, text):
            canvas.create_text(x, y + label_h // 2, text=text, anchor="w", fill=fe.TEXT,
                               font=("Arial", 14, "bold"))

        def place(widget, x, width):
            canvas.create_window(x, y + label_h, window=widget, anchor="nw",
                                 width=width, height=box_h)

        # row 1: first name | middle name
        label(x1, "First Name")
        label(x2, "Middle Name")
        place(edit_first, x1, col_w)
        place(edit_middle, x2, col_w)
        y = y + block

        # row 2: surname | suffix
        label(x1, "Surname")
        label(x2, "Suffix (optional)")
        place(edit_surname, x1, col_w)
        place(edit_suffix, x2, col_w)
        y = y + block

        # row 3: address | phone number
        address_w = int(inner * 0.62) - gap // 2
        phone_w = inner - address_w - gap
        label(x1, "Address")
        label(x1 + address_w + gap, "Phone Number")
        place(edit_address, x1, address_w)
        place(edit_phone, x1 + address_w + gap, phone_w)
        y = y + block

        # row 4: birthday (3 dropdowns) | sex (2 radio buttons)
        month_w = int(col_w * 0.46)
        day_w = int(col_w * 0.22)
        year_w = col_w - month_w - day_w - 2 * fe.px(8)
        label(x1, "Birthday")
        label(x2, "Sex")
        place(edit_month, x1, month_w)
        place(edit_day, x1 + month_w + fe.px(8), day_w)
        place(edit_year, x1 + month_w + day_w + 2 * fe.px(8), year_w)
        radio_h = fe.ctl(26)
        canvas.create_window(x2, y + label_h + (box_h - radio_h) // 2, window=edit_male,
                             anchor="nw", width=fe.px(190), height=radio_h)
        canvas.create_window(x2 + fe.px(210), y + label_h + (box_h - radio_h) // 2,
                             window=edit_female, anchor="nw", width=fe.px(220), height=radio_h)
        y = y + block

        edit_message_label.attach(canvas, x1, y, anchor="nw", fill=fe.BAD_RED,
                                  font=("Arial", 14, "bold"), width=inner, justify="left")
        y = y + message_h

        canvas.create_window(x1, y, window=save_button, anchor="nw", width=save_w, height=button_h)
        canvas.create_window(x1 + save_w + fe.px(14), y, window=cancel_button, anchor="nw",
                             width=cancel_w, height=button_h)

    def set_entry_text(entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)

    def start_edit():
        """Opens the Edit page and fills it with the worker's current information."""
        uid = state["uid"]
        record = backend.get_full_worker(uid)
        if record is None:
            return

        edit_uid_label.configure(text=f"Worker ID:  {uid}   (cannot be changed)")

        set_entry_text(edit_first, record["first_name"])
        set_entry_text(edit_middle, record["middle_name"])
        set_entry_text(edit_surname, record["surname"])
        set_entry_text(edit_suffix, record["suffix"])
        set_entry_text(edit_address, record["address"])
        set_entry_text(edit_phone, record["phone_number"])
        edit_sex.set(record["sex"])

        try:
            birthday = datetime.strptime(record["birthday"], "%m/%d/%Y")
            edit_month.set(fe.MONTHS[birthday.month - 1])
            edit_day.set(str(birthday.day))
            edit_year.set(str(birthday.year))
        except ValueError:
            edit_month.set("Month")
            edit_day.set("Day")
            edit_year.set("Year")

        edit_message_label.configure(text="")
        show_page(edit_page)

    def save_changes():
        """Checks the Edit form, then saves the changes."""
        uid = state["uid"]

        first_name = edit_first.get().strip()
        middle_name = edit_middle.get().strip()
        surname = edit_surname.get().strip()
        suffix = edit_suffix.get().strip()
        address = edit_address.get().strip()
        phone = edit_phone.get().strip()
        sex = edit_sex.get()

        month_text = edit_month.get()
        day_text = edit_day.get()
        year_text = edit_year.get()

        def error(text):
            edit_message_label.configure(text=text, text_color=fe.BAD_RED)

        if (first_name == "" or middle_name == "" or surname == "" or
                address == "" or phone == ""):
            error("Please complete all required fields.")
            return

        if month_text == "Month" or day_text == "Day" or year_text == "Year":
            error("Please select the complete birthday (Month, Day, and Year).")
            return

        month_number = fe.MONTHS.index(month_text) + 1
        try:
            birthday = datetime(int(year_text), month_number, int(day_text))
        except ValueError:
            error("That birthday date does not exist. Please check the day.")
            return

        if sex == "":
            error("Please select Male or Female.")
            return

        if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
            error("Please enter a valid phone number like 09123456789.")
            return

        backend.update_worker(uid, first_name, middle_name, surname, suffix, address,
                              birthday.strftime("%m/%d/%Y"), sex, phone)

        show_worker_detail(uid)
        message_label.configure(text="Worker information updated successfully.",
                                text_color=fe.OK_GREEN)

    return show_worker_detail