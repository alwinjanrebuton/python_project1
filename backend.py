# backend.py
# This file stores ALL the data in plain TEXT files (it does not use SQLite).
# It is the merge of the old database.py and report_data.py.
# The frontend.py and main.py files use this file to talk to the data.
#
# How it works:
#   - Each table is one text file inside the "data" folder (employees.txt, attendance.txt, ...)
#   - One record per line
#   - The fields in a line are separated by the | character
#   - Example line in employees.txt:
#       1|UID-4821|Juan|Santos|Dela Cruz||05/20/2000|Male|09123456789|Active|10/09/2026

import os                            # os helps us work with folders and file paths
import random                        # random helps us make random numbers (for the Worker ID)

import hashlib
import hmac
import re
import secrets
import shutil
from datetime import datetime, timedelta    # for dates, and for "yesterday"

# ---------- Where the text files will be saved ----------
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")

# This character separates the fields in a line.
SEPARATOR = "|"

# ---------- The tables: the name of each one and the order of its fields ----------
# The FIRST field of every table is its ID number.
TABLES = {
    "employees": [
        "employee_id", "worker_uid", "first_name", "middle_name", "surname", "suffix",
        "address", "birthday", "sex", "phone_number", "status", "registration_date", "photo_path"
    ],
    "attendance": [
        "attendance_id", "worker_uid", "date", "time_in", "time_out", "status"
    ],
    "absences": [
        "absence_id", "worker_uid", "absence_date", "reason", "explanation", "date_filed"
    ],
    "duty_schedule": [
        "duty_id", "worker_uid", "duty_date", "shift", "start_time", "end_time",
        "assignment", "status", "worker_report", "verification_status", "completion_status"
    ],
    "leaves": [
        "leave_id", "worker_uid", "leave_type", "start_date", "end_date", "reason",
        "status", "date_filed"
    ],
    "incidents": [
        "incident_id", "worker_uid", "date_time", "incident_type", "location",
        "personnel_involved", "description", "actions_taken", "additional_info",
        "status", "date_reported"
    ],
}


# =====================================================
# BASIC TOOLS: read and write the text files
# =====================================================
def clean_text(value):
    """Makes a value safe to put in a text file line.
    A | would break the line apart, and a new line would break it into two lines."""
    text = str(value)
    text = text.replace("|", "/")        # a | typed by the user becomes a /
    text = text.replace("\r", "")
    text = text.replace("\n", "<br>")    # a new line becomes <br>
    return text


def restore_text(text):
    """Does the opposite of clean_text for new lines: <br> becomes a new line again."""
    return text.replace("<br>", "\n")


def get_file_path(table_name):
    """Gives the full path of a table's text file."""
    return os.path.join(DATA_FOLDER, table_name + ".txt")


def create_tables():
    """Makes the data folder and any text file that does not exist yet."""
    os.makedirs(DATA_FOLDER, exist_ok=True)

    for table_name in TABLES:
        path = get_file_path(table_name)
        if not os.path.exists(path):
            # "w" means write. Opening a file this way makes a new empty file.
            with open(path, "w", encoding="utf-8") as file:
                pass

    migrate_uids()      # <-- add this line: old IDs like UID-4673 become 4673


def make_line(table_name, record):
    """Turns one record (a dictionary) into one line of text."""
    parts = []
    for field in TABLES[table_name]:
        parts.append(clean_text(record.get(field, "")))
    return SEPARATOR.join(parts)


def read_records(table_name):
    """Reads a text file and gives back a list of records.
    Each record is a dictionary like {"worker_uid": "UID-1234", "first_name": "Juan", ...}"""
    fields = TABLES[table_name]
    path = get_file_path(table_name)
    records = []

    if not os.path.exists(path):
        return records

    # "with open(...)" opens the file and closes it again by itself when we finish.
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip("\n")
            if line == "":
                continue                      # skip empty lines

            parts = line.split(SEPARATOR)
            # Older employee rows predate profile photos, so their photo_path is empty.
            if table_name == "employees" and len(parts) == len(fields) - 1:
                parts.append("")
            elif table_name == "duty_schedule" and len(parts) == len(fields) - 3:
                parts.extend(["", "", ""])
            if len(parts) != len(fields):
                continue                      # skip a damaged line

            record = {}
            for position in range(len(fields)):
                record[fields[position]] = restore_text(parts[position])
            records.append(record)

    return records


def write_records(table_name, records):
    """Replaces the whole text file with the records in the list."""
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(get_file_path(table_name), "w", encoding="utf-8") as file:
        for record in records:
            file.write(make_line(table_name, record) + "\n")


def add_record(table_name, record):
    """Adds ONE new line at the end of the text file ("a" means append)."""
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(get_file_path(table_name), "a", encoding="utf-8") as file:
        file.write(make_line(table_name, record) + "\n")


def next_id(table_name):
    """Gives the next ID number for a table: the biggest number used so far, plus 1."""
    id_field = TABLES[table_name][0]
    biggest = 0

    for record in read_records(table_name):
        try:
            number = int(record[id_field])
        except ValueError:
            continue
        if number > biggest:
            biggest = number

    return biggest + 1


# ---------- Worker ID generator ----------
def uid_exists(uid):
    """Checks if a Worker ID is already used. Returns True or False."""
    for record in read_records("employees"):
        if record["worker_uid"] == uid:
            return True
    return False


def generate_unique_uid():
    """Makes a random 4-digit Worker ID like 1234 that nobody else has."""
    while True:    # keep trying until we find an unused ID
        number = random.randint(0, 9999)      # a random number from 0 to 9999
        new_uid = f"{number:04d}"             # :04d makes it 4 digits, like 0042

        if not uid_exists(new_uid):           # if nobody has it yet...
            return new_uid                    # ...give it back and stop


def migrate_uids():
    """One-time cleanup: changes old IDs like UID-4673 into 4673 in every file.
    It is safe to run again. IDs that are already numbers are not touched."""
    for table_name, fields in TABLES.items():
        if "worker_uid" not in fields:
            continue

        records = read_records(table_name)
        changed = False
        for record in records:
            if record["worker_uid"].upper().startswith("UID-"):
                record["worker_uid"] = record["worker_uid"][4:]
                changed = True

        if changed:
            write_records(table_name, records)


# ---------- Save a new worker ----------
def save_worker(uid, first_name, middle_name, surname, suffix,
                address, birthday, sex, phone, photo_path=""):
    """Saves a new worker in the employees file. Returns True if saved, False if not."""

    # A Worker ID can never be used twice
    if uid_exists(uid):
        return False

    record = {
        "employee_id": next_id("employees"),
        "worker_uid": uid,
        "first_name": first_name,
        "middle_name": middle_name,
        "surname": surname,
        "suffix": suffix,
        "address": address,
        "birthday": birthday,
        "sex": sex,
        "phone_number": phone,
        "status": "Active",
        "registration_date": datetime.now().strftime("%m/%d/%Y"),    # like 10/09/2026
        "photo_path": photo_path,
    }
    add_record("employees", record)
    return True


# ---------- Worker profile photos ----------
WORKER_PHOTO_FOLDER = os.path.join(DATA_FOLDER, "worker_photos")
WORKER_PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

def store_worker_photo(uid, source_path):
    """Copies a selected image into the app data folder and returns its relative path."""
    extension = os.path.splitext(source_path)[1].lower()
    if extension not in WORKER_PHOTO_EXTENSIONS or not os.path.isfile(source_path):
        return ""
    os.makedirs(WORKER_PHOTO_FOLDER, exist_ok=True)
    filename = uid + extension
    destination = os.path.join(WORKER_PHOTO_FOLDER, filename)
    shutil.copy2(source_path, destination)
    return os.path.join("worker_photos", filename).replace(os.sep, "/")

def get_worker_photo_path(photo_path):
    """Resolves a saved photo path safely; returns an empty string when unavailable."""
    if not photo_path:
        return ""
    root_path = os.path.abspath(DATA_FOLDER)
    full_path = os.path.abspath(os.path.join(root_path, photo_path))
    try:
        if os.path.commonpath((root_path, full_path)) != root_path:
            return ""
    except ValueError:
        return ""
    return full_path if os.path.isfile(full_path) else ""

def delete_worker_photo(photo_path):
    """Removes a stored photo when its worker record could not be saved."""
    full_path = get_worker_photo_path(photo_path)
    if full_path:
        try:
            os.remove(full_path)
        except OSError:
            pass


# ---------- Find a worker by Worker ID ----------
def get_worker(uid):
    """Looks for a worker with this Worker ID.
    Gives back (worker_uid, first_name, middle_name, surname, suffix, status),
    or None if there is no such worker."""
    for record in read_records("employees"):
        if record["worker_uid"] == uid:
            return (record["worker_uid"], record["first_name"], record["middle_name"],
                    record["surname"], record["suffix"], record["status"])
    return None


# ---------- Attendance ----------
def get_attendance_today(uid, date_text):
    """Looks for this worker's attendance on this date.
    Gives back (time_in, status), or None if they have not recorded attendance yet."""
    for record in read_records("attendance"):
        if record["worker_uid"] == uid and record["date"] == date_text:
            return (record["time_in"], record["status"])
    return None


def save_time_in(uid, date_text, time_in, status):
    """Saves a new attendance record (time out stays empty for now)."""
    record = {
        "attendance_id": next_id("attendance"),
        "worker_uid": uid,
        "date": date_text,
        "time_in": time_in,
        "time_out": "",
        "status": status,
    }
    add_record("attendance", record)


# ---------- Absence ----------
def absence_exists(uid, absence_date):
    """Checks if this worker already filed an absence for this date.
    Returns True or False."""
    for record in read_records("absences"):
        if record["worker_uid"] == uid and record["absence_date"] == absence_date:
            return True
    return False


def save_absence(uid, absence_date, reason, explanation, date_filed):
    """Saves a new absence report."""
    record = {
        "absence_id": next_id("absences"),
        "worker_uid": uid,
        "absence_date": absence_date,
        "reason": reason,
        "explanation": explanation,
        "date_filed": date_filed,
    }
    add_record("absences", record)


# ---------- Leave ----------
def leave_exists(uid, start_date, end_date):
    """Checks if this worker already sent a leave request with the same dates.
    A Rejected request does not count, so the worker can try again.
    Returns True or False."""
    for record in read_records("leaves"):
        if (record["worker_uid"] == uid and record["start_date"] == start_date
                and record["end_date"] == end_date and record["status"] != "Rejected"):
            return True
    return False


def save_leave(uid, leave_type, start_date, end_date, reason, date_filed):
    """Saves a new leave request. Its status starts as Pending."""
    record = {
        "leave_id": next_id("leaves"),
        "worker_uid": uid,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": "Pending",
        "date_filed": date_filed,
    }
    add_record("leaves", record)


def get_worker_leaves(uid):
    """Gets this worker's last 5 leave requests (newest first).
    Each one is (leave_type, start_date, end_date, status)."""
    results = []

    # The newest records are at the END of the file, so we go through the list backwards.
    for record in reversed(read_records("leaves")):
        if record["worker_uid"] == uid:
            results.append((record["leave_type"], record["start_date"],
                            record["end_date"], record["status"]))

    return results[:5]      # [:5] keeps only the first 5


# ---------- Incident reports ----------
def save_incident(uid, date_time, incident_type, location, personnel,
                  description, actions, additional, date_reported):
    """Saves a new incident report (its status starts as Open).
    Gives back the new incident number (1, 2, 3...). We show it as INC-0001."""
    new_id = next_id("incidents")

    record = {
        "incident_id": new_id,
        "worker_uid": uid,
        "date_time": date_time,
        "incident_type": incident_type,
        "location": location,
        "personnel_involved": personnel,
        "description": description,
        "actions_taken": actions,
        "additional_info": additional,
        "status": "Open",
        "date_reported": date_reported,
    }
    add_record("incidents", record)
    return new_id


def get_worker_incidents(uid):
    """Gets this worker's last 5 incident reports (newest first).
    Deleted reports are hidden.
    Each one is (incident_id, incident_type, date_time, status)."""
    results = []

    for record in reversed(read_records("incidents")):
        if record["worker_uid"] == uid and record["status"] != "Deleted":
            results.append((int(record["incident_id"]), record["incident_type"],
                            record["date_time"], record["status"]))

    return results[:5]


# ---------- Duty / Shift ----------
# The three shifts and their times. The Worker screens and the
# Admin screens both use this same list.
SHIFT_TIMES = {
    "Morning": ("6:00 AM", "2:00 PM"),
    "Afternoon": ("2:00 PM", "10:00 PM"),
    "Night": ("10:00 PM", "6:00 AM"),
}


def save_duty(uid, duty_date, shift, assignment):
    """Assigns a shift to a worker for one date.
    If that worker already has a duty on that date, the old one is replaced."""
    new_id = next_id("duty_schedule")

    # Keep every duty EXCEPT the old one for the same worker and date
    kept = []
    for record in read_records("duty_schedule"):
        if record["worker_uid"] == uid and record["duty_date"] == duty_date:
            continue
        kept.append(record)

    kept.append({
        "duty_id": new_id,
        "worker_uid": uid,
        "duty_date": duty_date,
        "shift": shift,
        "start_time": SHIFT_TIMES[shift][0],
        "end_time": SHIFT_TIMES[shift][1],
        "assignment": assignment,
        "status": "Scheduled",
        "worker_report": "",
        "verification_status": "",
        "completion_status": "",
    })

    write_records("duty_schedule", kept)


def get_worker_duty_records(uid):
    """Gets this worker's full duty records, newest duty date first."""
    records = [record for record in read_records("duty_schedule")
               if record["worker_uid"] == uid]
    def duty_date(record):
        try:
            return datetime.strptime(record["duty_date"], "%m/%d/%Y").date()
        except ValueError:
            return datetime.min.date()
    records.sort(key=duty_date, reverse=True)
    return records

def submit_duty_report(uid, duty_id, report):
    """Lets a worker report Done or Not yet for their own current/past assignment."""
    if report not in ("Done", "Not yet"):
        return False
    today = datetime.now().date()
    records = read_records("duty_schedule")
    found = False
    for record in records:
        if record["duty_id"] != str(duty_id) or record["worker_uid"] != uid:
            continue
        try:
            duty_day = datetime.strptime(record["duty_date"], "%m/%d/%Y").date()
        except ValueError:
            return False
        if duty_day > today:
            return False
        record["worker_report"] = report
        record["verification_status"] = "Pending"
        record["completion_status"] = ""
        found = True
        break
    if found:
        write_records("duty_schedule", records)
    return found

def verify_duty_report(duty_id, decision):
    """Admin accepts the worker report (check) or marks the duty unfinished (X)."""
    if decision not in ("verify", "unfinish"):
        return False
    records = read_records("duty_schedule")
    found = False
    for record in records:
        if record["duty_id"] != str(duty_id):
            continue
        if record.get("verification_status") != "Pending" or not record.get("worker_report"):
            return False
        if decision == "verify":
            record["completion_status"] = ("Done" if record["worker_report"] == "Done"
                                           else "Unfinish")
            record["verification_status"] = "Verified"
        else:
            record["completion_status"] = "Unfinish"
            record["verification_status"] = "Rejected"
        found = True
        break
    if found:
        write_records("duty_schedule", records)
    return found

def get_worker_duties(uid):
    """Gets ALL of this worker's duties.
    Each one is (duty_date, shift, start_time, end_time, assignment)."""
    results = []

    for record in read_records("duty_schedule"):
        if record["worker_uid"] == uid:
            results.append((record["duty_date"], record["shift"], record["start_time"],
                            record["end_time"], record["assignment"]))

    return results


# ---------- Numbers for the Admin Dashboard ----------
def count_workers():
    """How many workers are Active."""
    total = 0
    for record in read_records("employees"):
        if record["status"] == "Active":
            total = total + 1
    return total


def count_present(date_text):
    """How many attendance records exist for this date."""
    total = 0
    for record in read_records("attendance"):
        if record["date"] == date_text:
            total = total + 1
    return total


def count_absent(date_text):
    """How many absence reports were filed for this date."""
    total = 0
    for record in read_records("absences"):
        if record["absence_date"] == date_text:
            total = total + 1
    return total


def count_on_leave(today_date):
    """How many Approved leaves include today's date.
    The dates are saved as text, so we turn them into real dates to compare them."""
    total = 0
    for record in read_records("leaves"):
        if record["status"] != "Approved":
            continue
        start = datetime.strptime(record["start_date"], "%m/%d/%Y").date()
        end = datetime.strptime(record["end_date"], "%m/%d/%Y").date()
        if start <= today_date <= end:       # today is between start and end
            total = total + 1
    return total


def count_pending_leaves():
    """How many leave requests are still waiting for the Admin's decision."""
    total = 0
    for record in read_records("leaves"):
        if record["status"] == "Pending":
            total = total + 1
    return total


def get_current_shift(now):
    """Finds which shift is happening right now.
    Gives back (shift name, the date that duty was saved under).
    A Night shift after midnight belongs to YESTERDAY's date."""
    hour = now.hour

    if 6 <= hour < 14:
        shift = "Morning"
        duty_day = now
    elif 14 <= hour < 22:
        shift = "Afternoon"
        duty_day = now
    else:
        shift = "Night"
        if hour < 6:                              # after midnight
            duty_day = now - timedelta(days=1)    # the duty started yesterday
        else:
            duty_day = now

    return shift, duty_day.strftime("%m/%d/%Y")


def count_on_duty_now(now):
    """How many workers are scheduled for the shift happening right now."""
    shift, duty_date_text = get_current_shift(now)

    total = 0
    for record in read_records("duty_schedule"):
        if record["duty_date"] == duty_date_text and record["shift"] == shift:
            total = total + 1
    return total


def get_recent_incidents(how_many):
    """Gets the newest incident reports from ALL workers. Deleted reports are hidden.
    Each one is (incident_id, incident_type, date_time, worker_uid, status)."""
    results = []

    for record in reversed(read_records("incidents")):
        if record["status"] == "Deleted":
            continue
        results.append((int(record["incident_id"]), record["incident_type"],
                        record["date_time"], record["worker_uid"], record["status"]))

    return results[:how_many]


# ---------- Worker Management (for the Admin) ----------
def get_all_workers():
    """Gives back every worker (a list of records), Active and Inactive."""
    return read_records("employees")


def get_full_worker(uid):
    """Gives back the complete record of one worker, or None if there is no such worker."""
    for record in read_records("employees"):
        if record["worker_uid"] == uid:
            return record
    return None


def search_workers(search_text):
    """Finds the workers that match what the Admin typed.
    It looks at the Worker ID, the name, and the phone number.
    Every word typed must be found somewhere, so "juan cruz" works too."""
    words = search_text.lower().split()      # split() cuts the text into words
    results = []

    for record in read_records("employees"):
        everything = (record["worker_uid"] + " " + record["first_name"] + " " +
                      record["middle_name"] + " " + record["surname"] + " " +
                      record["suffix"] + " " + record["phone_number"]).lower()

        found_all = True
        for word in words:
            if word not in everything:
                found_all = False

        if found_all:
            results.append(record)

    return results


def update_worker(uid, first_name, middle_name, surname, suffix,
                  address, birthday, sex, phone, photo_path=None):
    """Changes a worker's information. The Worker ID and status stay the same.
    Returns True if the worker was found and changed, False if not."""
    records = read_records("employees")
    found = False

    for record in records:
        if record["worker_uid"] == uid:
            record["first_name"] = first_name
            record["middle_name"] = middle_name
            record["surname"] = surname
            record["suffix"] = suffix
            record["address"] = address
            record["birthday"] = birthday
            record["sex"] = sex
            record["phone_number"] = phone
            if photo_path is not None:
                record["photo_path"] = photo_path
            found = True

    if found:
        write_records("employees", records)    # save the changed list back to the file

    return found


def set_worker_status(uid, new_status):
    """Changes a worker's status to Active or Inactive. Nothing is deleted.
    Returns True if the worker was found and changed, False if not."""
    records = read_records("employees")
    found = False

    for record in records:
        if record["worker_uid"] == uid:
            record["status"] = new_status
            found = True

    if found:
        write_records("employees", records)

    return found


def get_worker_history(uid):
    """Gathers everything this worker has done (newest first).
    Gives back a dictionary with five lists of records. Deleted incident reports are hidden."""
    history = {
        "attendance": [],
        "absences": [],
        "leaves": [],
        "incidents": [],
        "duties": [],
    }

    for record in reversed(read_records("attendance")):
        if record["worker_uid"] == uid:
            history["attendance"].append(record)

    for record in reversed(read_records("absences")):
        if record["worker_uid"] == uid:
            history["absences"].append(record)

    for record in reversed(read_records("leaves")):
        if record["worker_uid"] == uid:
            history["leaves"].append(record)

    for record in reversed(read_records("incidents")):
        if record["worker_uid"] == uid and record["status"] != "Deleted":
            history["incidents"].append(record)

    for record in reversed(read_records("duty_schedule")):
        if record["worker_uid"] == uid:
            history["duties"].append(record)

    return history


# ---------- Attendance records (for the Admin) and Time Out ----------
def make_name(worker_record):
    """Joins first name, middle name, surname, and suffix. Empty parts are skipped."""
    parts = [worker_record["first_name"], worker_record["middle_name"],
             worker_record["surname"], worker_record["suffix"]]
    name = ""
    for part in parts:
        if part != "":
            if name != "":
                name = name + " "
            name = name + part
    return name


def get_attendance_record(uid, date_text):
    """Looks for this worker's attendance on this date.
    Gives back (time_in, time_out, status), or None if there is no record."""
    for record in read_records("attendance"):
        if record["worker_uid"] == uid and record["date"] == date_text:
            return (record["time_in"], record["time_out"], record["status"])
    return None


def save_time_out(uid, date_text, time_out):
    """Saves the Time Out in this worker's attendance record for this date.
    Returns True if the record was found and changed, False if not."""
    records = read_records("attendance")
    found = False

    for record in records:
        if record["worker_uid"] == uid and record["date"] == date_text:
            record["time_out"] = time_out
            found = True

    if found:
        write_records("attendance", records)

    return found


def get_attendance_records(first_date, last_date, search_text, status_filter):
    """Finds attendance records for the Admin (newest first).
    first_date and last_date are real dates, or None to include all dates.
    search_text looks at the Worker ID and the name.
    status_filter is "All Statuses" or one status.
    Each record also gets a "full_name" so the Admin can see who it is."""

    # Make a list of every worker's name, so we can show names next to the IDs
    names = {}
    for worker in read_records("employees"):
        names[worker["worker_uid"]] = make_name(worker)

    words = search_text.lower().split()
    results = []

    for record in reversed(read_records("attendance")):
        # Check the date
        if first_date is not None:
            try:
                record_day = datetime.strptime(record["date"], "%m/%d/%Y").date()
            except ValueError:
                continue
            if record_day < first_date or record_day > last_date:
                continue

        # Check the status
        if status_filter != "All Statuses" and record["status"] != status_filter:
            continue

        # Check the search words (every word must be found in the ID or the name)
        full_name = names.get(record["worker_uid"], "(unknown worker)")
        everything = (record["worker_uid"] + " " + full_name).lower()

        found_all = True
        for word in words:
            if word not in everything:
                found_all = False
        if not found_all:
            continue

        record["full_name"] = full_name
        results.append(record)

    return results


def update_attendance_status(attendance_id, new_status):
    """Changes the status of one attendance record.
    Returns True if the record was found and changed, False if not."""
    records = read_records("attendance")
    found = False

    for record in records:
        if record["attendance_id"] == str(attendance_id):
            record["status"] = new_status
            found = True

    if found:
        write_records("attendance", records)

    return found


# ---------- Leave and Absence management (for the Admin) ----------
def get_leave_requests(status_filter, search_text):
    """Finds leave requests for the Admin (newest first).
    status_filter is "All Statuses" or one status (Pending, Approved, Rejected).
    search_text looks at the Worker ID and the name.
    Each record also gets a "full_name" so the Admin can see who it is."""

    # Make a list of every worker's name, so we can show names next to the IDs
    names = {}
    for worker in read_records("employees"):
        names[worker["worker_uid"]] = make_name(worker)

    words = search_text.lower().split()
    results = []

    for record in reversed(read_records("leaves")):
        # Check the status
        if status_filter != "All Statuses" and record["status"] != status_filter:
            continue

        # Check the search words (every word must be found in the ID or the name)
        full_name = names.get(record["worker_uid"], "(unknown worker)")
        everything = (record["worker_uid"] + " " + full_name).lower()

        found_all = True
        for word in words:
            if word not in everything:
                found_all = False
        if not found_all:
            continue

        record["full_name"] = full_name
        results.append(record)

    return results


def update_leave_status(leave_id, new_status):
    """Changes the status of one leave request (Pending, Approved, or Rejected).
    Returns True if the request was found and changed, False if not."""
    records = read_records("leaves")
    found = False

    for record in records:
        if record["leave_id"] == str(leave_id):
            record["status"] = new_status
            found = True

    if found:
        write_records("leaves", records)

    return found


def get_absence_reports(first_date, last_date, search_text):
    """Finds absence reports for the Admin (newest first).
    first_date and last_date are real dates, or None to include all dates.
    search_text looks at the Worker ID and the name.
    Each record also gets a "full_name"."""

    names = {}
    for worker in read_records("employees"):
        names[worker["worker_uid"]] = make_name(worker)

    words = search_text.lower().split()
    results = []

    for record in reversed(read_records("absences")):
        # Check the date
        if first_date is not None:
            try:
                record_day = datetime.strptime(record["absence_date"], "%m/%d/%Y").date()
            except ValueError:
                continue
            if record_day < first_date or record_day > last_date:
                continue

        # Check the search words
        full_name = names.get(record["worker_uid"], "(unknown worker)")
        everything = (record["worker_uid"] + " " + full_name).lower()

        found_all = True
        for word in words:
            if word not in everything:
                found_all = False
        if not found_all:
            continue

        record["full_name"] = full_name
        results.append(record)

    return results


# ---------- Incident management (for the Admin) ----------
def get_incident_list(type_filter, status_filter, search_text):
    """Finds incident reports for the Admin (newest first).
    type_filter is "All Types" or one incident type.
    status_filter is "All Statuses" (which hides Deleted reports) or one status.
    search_text looks at the incident number, the worker, the type, the location,
    and the description.
    Each record also gets a "full_name" (who reported it) and an "incident_number"."""

    # Make a list of every worker's name, so we can show names next to the IDs
    names = {}
    for worker in read_records("employees"):
        names[worker["worker_uid"]] = make_name(worker)

    words = search_text.lower().split()
    results = []

    for record in reversed(read_records("incidents")):
        # Check the status. "All Statuses" does not include Deleted reports.
        if status_filter == "All Statuses":
            if record["status"] == "Deleted":
                continue
        elif record["status"] != status_filter:
            continue

        # Check the type
        if type_filter != "All Types" and record["incident_type"] != type_filter:
            continue

        # Check the search words (every word must be found somewhere)
        full_name = names.get(record["worker_uid"], "(unknown worker)")
        incident_number = f"INC-{int(record['incident_id']):04d}"      # 1 becomes INC-0001
        everything = (incident_number + " " + record["worker_uid"] + " " + full_name + " " +
                      record["incident_type"] + " " + record["location"] + " " +
                      record["description"]).lower()

        found_all = True
        for word in words:
            if word not in everything:
                found_all = False
        if not found_all:
            continue

        record["full_name"] = full_name
        record["incident_number"] = incident_number
        results.append(record)

    return results


def get_incident(incident_id):
    """Gives back one complete incident report (with "full_name" and "incident_number"),
    or None if there is no such report."""
    for record in read_records("incidents"):
        if record["incident_id"] == str(incident_id):
            worker = get_full_worker(record["worker_uid"])
            if worker is None:
                record["full_name"] = "(unknown worker)"
            else:
                record["full_name"] = make_name(worker)
            record["incident_number"] = f"INC-{int(record['incident_id']):04d}"
            return record
    return None


def update_incident(incident_id, incident_type, date_time, location, personnel,
                    description, actions, additional, status):
    """Changes an incident report. The incident number, the reporter, and the date
    reported stay the same. Returns True if the report was found and changed."""
    records = read_records("incidents")
    found = False

    for record in records:
        if record["incident_id"] == str(incident_id):
            record["incident_type"] = incident_type
            record["date_time"] = date_time
            record["location"] = location
            record["personnel_involved"] = personnel
            record["description"] = description
            record["actions_taken"] = actions
            record["additional_info"] = additional
            record["status"] = status
            found = True

    if found:
        write_records("incidents", records)

    return found


def set_incident_status(incident_id, new_status):
    """Changes only the status of one incident report.
    We use it to delete a report (status "Deleted") and to restore it.
    Returns True if the report was found and changed."""
    records = read_records("incidents")
    found = False

    for record in records:
        if record["incident_id"] == str(incident_id):
            record["status"] = new_status
            found = True

    if found:
        write_records("incidents", records)

    return found


# =====================================================
# REPORTS (this used to be report_data.py)
# =====================================================
def text_to_date(text):
    """Turns text like 10/09/2026 into a real date.
    Gives back None if the text is not a real date."""
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except ValueError:
        return None


def in_range(day, first_date, last_date):
    """True if the day is between the first and the last date.
    If first_date is None, every day is accepted."""
    if first_date is None:
        return True
    return first_date <= day <= last_date


def worker_matches(uid, full_name, words):
    """True if every search word is found in the Worker ID or the name.
    If there are no words, everyone matches."""
    everything = (uid + " " + full_name).lower()
    for word in words:
        if word not in everything:
            return False
    return True


def dash_if_empty(value):
    """Gives a dash for an empty value, so empty things look tidy."""
    if value == "":
        return "-"
    return value


def get_report(report_name, first_date, last_date, search_text):
    """Builds one report for the Admin.
    first_date and last_date are real dates (or None for all dates).
    search_text (optional) looks at the Worker ID and the name.
    Gives back three things: (headers, rows, summary)
      headers = the column titles
      rows    = a list of rows, each row is a list of text
      summary = one line of totals"""

    # Make a list of every worker's name, so we can show names next to the IDs
    names = {}
    for worker in read_records("employees"):
        names[worker["worker_uid"]] = make_name(worker)

    words = search_text.lower().split()

    headers = []
    found = []          # pairs of (sort key, row). We sort them at the end.
    summary = ""

    # ---------------- Daily Attendance ----------------
    if report_name == "Daily Attendance":
        headers = ["Date", "Worker ID", "Name", "Time In", "Time Out", "Status"]
        counts = {}

        for record in read_records("attendance"):
            day = text_to_date(record["date"])
            if day is None or not in_range(day, first_date, last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            if not worker_matches(uid, full_name, words):
                continue

            counts[record["status"]] = counts.get(record["status"], 0) + 1
            found.append((day, [record["date"], uid, full_name,
                                dash_if_empty(record["time_in"]),
                                dash_if_empty(record["time_out"]),
                                record["status"]]))

        summary = f"Total attendance records: {len(found)}"
        for status in ["Present", "Late", "Absent", "On Leave", "Official Duty"]:
            if counts.get(status, 0) > 0:
                summary = summary + f"     {status}: {counts[status]}"

    # ---------------- Duty Schedule ----------------
    elif report_name == "Duty Schedule":
        headers = ["Date", "Worker ID", "Name", "Shift", "Time", "Assignment"]
        counts = {}

        for record in read_records("duty_schedule"):
            day = text_to_date(record["duty_date"])
            if day is None or not in_range(day, first_date, last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            if not worker_matches(uid, full_name, words):
                continue

            counts[record["shift"]] = counts.get(record["shift"], 0) + 1
            found.append((day, [record["duty_date"], uid, full_name, record["shift"],
                                record["start_time"] + " - " + record["end_time"],
                                record["assignment"]]))

        summary = f"Total duties: {len(found)}"
        for shift in ["Morning", "Afternoon", "Night"]:
            if counts.get(shift, 0) > 0:
                summary = summary + f"     {shift}: {counts[shift]}"

    # ---------------- Absence Records ----------------
    elif report_name == "Absence Records":
        headers = ["Date", "Worker ID", "Name", "Reason", "Explanation", "Filed"]

        for record in read_records("absences"):
            day = text_to_date(record["absence_date"])
            if day is None or not in_range(day, first_date, last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            if not worker_matches(uid, full_name, words):
                continue

            found.append((day, [record["absence_date"], uid, full_name, record["reason"],
                                dash_if_empty(record["explanation"]), record["date_filed"]]))

        summary = f"Total absence reports: {len(found)}"

    # ---------------- Leave Records ----------------
    elif report_name == "Leave Records":
        headers = ["Worker ID", "Name", "Leave Type", "Start Date", "End Date",
                   "Reason", "Status", "Filed"]
        counts = {}

        for record in read_records("leaves"):
            start = text_to_date(record["start_date"])
            end = text_to_date(record["end_date"])
            if start is None or end is None:
                continue

            # A leave is included if it overlaps the period
            if first_date is not None and (start > last_date or end < first_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            if not worker_matches(uid, full_name, words):
                continue

            counts[record["status"]] = counts.get(record["status"], 0) + 1
            found.append((start, [uid, full_name, record["leave_type"], record["start_date"],
                                  record["end_date"], dash_if_empty(record["reason"]),
                                  record["status"], record["date_filed"]]))

        summary = f"Total leave requests: {len(found)}"
        for status in ["Pending", "Approved", "Rejected"]:
            if counts.get(status, 0) > 0:
                summary = summary + f"     {status}: {counts[status]}"

    # ---------------- Incident Reports ----------------
    elif report_name == "Incident Reports":
        headers = ["Incident ID", "Date / Time", "Type", "Location", "Reported By", "Status"]
        counts = {}

        for record in read_records("incidents"):
            if record["status"] == "Deleted":
                continue

            try:
                moment = datetime.strptime(record["date_time"], "%m/%d/%Y %I:%M %p")
            except ValueError:
                continue
            if not in_range(moment.date(), first_date, last_date):
                continue

            uid = record["worker_uid"]
            full_name = names.get(uid, "(unknown worker)")
            if not worker_matches(uid, full_name, words):
                continue

            incident_number = f"INC-{int(record['incident_id']):04d}"      # 1 becomes INC-0001
            counts[record["status"]] = counts.get(record["status"], 0) + 1
            found.append((moment, [incident_number, record["date_time"], record["incident_type"],
                                   record["location"], uid + " " + full_name, record["status"]]))

        summary = f"Total incident reports: {len(found)}"
        for status in ["Open", "Under Review", "Closed"]:
            if counts.get(status, 0) > 0:
                summary = summary + f"     {status}: {counts[status]}"

    # ---------------- Worker Activity History ----------------
    elif report_name == "Worker Activity History":
        headers = ["Worker ID", "Name", "Status", "Attendance", "Absences",
                   "Leaves", "Incidents", "Duties"]

        # Count each worker's records in the period (one list at a time)
        attendance_counts = {}
        for record in read_records("attendance"):
            day = text_to_date(record["date"])
            if day is None or not in_range(day, first_date, last_date):
                continue
            uid = record["worker_uid"]
            attendance_counts[uid] = attendance_counts.get(uid, 0) + 1

        absence_counts = {}
        for record in read_records("absences"):
            day = text_to_date(record["absence_date"])
            if day is None or not in_range(day, first_date, last_date):
                continue
            uid = record["worker_uid"]
            absence_counts[uid] = absence_counts.get(uid, 0) + 1

        leave_counts = {}
        for record in read_records("leaves"):
            start = text_to_date(record["start_date"])
            end = text_to_date(record["end_date"])
            if start is None or end is None:
                continue
            if first_date is not None and (start > last_date or end < first_date):
                continue
            uid = record["worker_uid"]
            leave_counts[uid] = leave_counts.get(uid, 0) + 1

        incident_counts = {}
        for record in read_records("incidents"):
            if record["status"] == "Deleted":
                continue
            try:
                moment = datetime.strptime(record["date_time"], "%m/%d/%Y %I:%M %p")
            except ValueError:
                continue
            if not in_range(moment.date(), first_date, last_date):
                continue
            uid = record["worker_uid"]
            incident_counts[uid] = incident_counts.get(uid, 0) + 1

        duty_counts = {}
        for record in read_records("duty_schedule"):
            day = text_to_date(record["duty_date"])
            if day is None or not in_range(day, first_date, last_date):
                continue
            uid = record["worker_uid"]
            duty_counts[uid] = duty_counts.get(uid, 0) + 1

        # One row for each worker
        for worker in read_records("employees"):
            uid = worker["worker_uid"]
            full_name = names[uid]
            if not worker_matches(uid, full_name, words):
                continue

            found.append((uid, [uid, full_name, worker["status"],
                                str(attendance_counts.get(uid, 0)),
                                str(absence_counts.get(uid, 0)),
                                str(leave_counts.get(uid, 0)),
                                str(incident_counts.get(uid, 0)),
                                str(duty_counts.get(uid, 0))]))

        summary = f"Workers listed: {len(found)}"

    # Put the rows in order (oldest first), then take the rows out of the pairs
    found.sort()

    rows = []
    for item in found:
        rows.append(item[1])

    return headers, rows, summary



# ---------- App settings (plain text, no SQLite) ----------
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.txt")
DEFAULT_SETTINGS = {
    "auto_refresh": "on",
    "refresh_seconds": "5",
    "notifications": "on",
}

def load_settings():
    """Loads small app settings from a plain text file."""
    settings = DEFAULT_SETTINGS.copy()
    if not os.path.exists(SETTINGS_FILE):
        return settings
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip("\n")
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key in settings:
                    settings[key] = value
    except OSError:
        pass
    return settings

def save_settings(settings):
    """Saves app settings as key=value lines."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    clean = DEFAULT_SETTINGS.copy()
    clean.update({key: str(value) for key, value in settings.items() if key in clean})
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        for key, value in clean.items():
            file.write(f"{key}={clean_text(value)}\n")
    return True

def get_setting(key, default=None):
    return load_settings().get(key, default)

def backup_data(destination_folder=None):
    """Copies the text-file data folder into a timestamped backup folder."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if destination_folder is None:
        destination_folder = os.path.join(BASE_FOLDER, "backups")
    os.makedirs(destination_folder, exist_ok=True)
    target = os.path.join(destination_folder, "fire_station_backup_" + stamp)
    os.makedirs(target, exist_ok=True)
    for name in os.listdir(DATA_FOLDER):
        source = os.path.join(DATA_FOLDER, name)
        if os.path.isfile(source):
            shutil.copy2(source, os.path.join(target, name))
    return target

def export_all_csv(destination_folder=None):
    """Exports every text-file table to a matching CSV file."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if destination_folder is None:
        destination_folder = os.path.join(BASE_FOLDER, "reports", "full_export_" + stamp)
    os.makedirs(destination_folder, exist_ok=True)
    import csv
    exported = []
    for table_name, fields in TABLES.items():
        path = os.path.join(destination_folder, table_name + ".csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for record in read_records(table_name):
                writer.writerow({field: restore_text(record.get(field, "")) for field in fields})
        exported.append(path)
    return destination_folder, exported

# ---------- Test area ----------
# This part runs ONLY when you run backend.py directly.
if __name__ == "__main__":
    create_tables()
    print("Text files are ready!")
    print("Saved in:", DATA_FOLDER)

    # Show each text file and how many records it has
    print("Files in the data folder:")
    for table_name in TABLES:
        print(" -", table_name + ".txt:", len(read_records(table_name)), "record(s)")

    # Test the Worker ID generator
    print("Sample Worker IDs:")
    for i in range(3):
        print(" -", generate_unique_uid())

# ---------- Admin account (one-time local registration) ----------
ADMIN_ACCOUNT_FILE = os.path.join(DATA_FOLDER, "admin_account.txt")

def has_admin_account():
    """Returns True once an admin account has been registered."""
    return os.path.isfile(ADMIN_ACCOUNT_FILE)

def create_admin_account(username, password):
    """Creates the first admin account; passwords are stored as salted hashes."""
    if not re.fullmatch(r"[a-z0-9]{1,10}", username or ""):
        return False
    if not re.fullmatch(r"[A-Za-z0-9]{1,5}", password or ""):
        return False
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if has_admin_account():
        return False
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
    with open(ADMIN_ACCOUNT_FILE, "x", encoding="utf-8") as file:
        file.write(username + "\n" + salt.hex() + "\n" + digest.hex() + "\n")
    return True

def verify_admin_account(username, password):
    """Checks an admin username and password against the saved password hash."""
    if not username or not password or not has_admin_account():
        return False
    try:
        with open(ADMIN_ACCOUNT_FILE, "r", encoding="utf-8") as file:
            saved_username, salt_hex, digest_hex = [line.rstrip("\n") for line in file.readlines()[:3]]
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (OSError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
    return hmac.compare_digest(username, saved_username) and hmac.compare_digest(actual, expected)
