import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from threading import Thread
import serial
import cv2
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import helper modules (to be implemented separately)
from rfid_handler import read_rfid       # Function to read RFID tags
from face_detector import detect_face   # Function to detect face presence
from logger import log_event            # Function to log events to SQLite
from email_sender import send_email     # Function to send email notifications

# Global state
active_students = set()  # Track student IDs currently inside
last_scan_times = {}     # Track last scan time for each tag to catch duplicates

# Initialize or connect to SQLite database
try:
    conn = sqlite3.connect('school_gate.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gate_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            event TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
except Exception as e:
    print(f"Error initializing database: {e}")

def log_event_db(student_id, event_type):
    """
    Log entry/exit event into the SQLite database.
    """
    try:
        cursor.execute(
            "INSERT INTO gate_log (student_id, event) VALUES (?, ?)",
            (student_id, event_type)
        )
        conn.commit()
    except Exception as e:
        print(f"Error writing to DB: {e}")

def process_tag(tag, status_label, log_text, active_listbox):
    """
    Handle an RFID tag scan: detect face, log event, update GUI, and send email.
    """
    import time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Handle duplicate scans (ignore if same tag scanned within 5 seconds)
    now = time.time()
    if tag in last_scan_times and (now - last_scan_times[tag] < 5):
        status_label.config(text=f"Duplicate scan for {tag} ignored.", fg="red")
        return
    last_scan_times[tag] = now

    # Determine if this is an entry or exit event
    if tag in active_students:
        event_type = 'exit'
    else:
        event_type = 'entry'

    # Use the webcam to detect a face
    try:
        face_present = detect_face()  # Should return True if a face is detected
    except Exception as e:
        status_label.config(text=f"Face detection error: {e}", fg="red")
        return

    if not face_present:
        status_label.config(
            text=f"No face detected for {tag}. Please try again.",
            fg="red"
        )
        log_text.insert(tk.END, f"{timestamp} - No face detected for {tag}.\n")
        log_text.yview(tk.END)
        return

    # Face confirmed, proceed with logging the event
    if event_type == 'entry':
        active_students.add(tag)
        status_label.config(text=f"{tag} entered at {timestamp}", fg="green")
        log_text.insert(tk.END, f"{timestamp} - {tag} ENTRY\n")
    else:
        active_students.remove(tag)
        status_label.config(text=f"{tag} exited at {timestamp}", fg="green")
        log_text.insert(tk.END, f"{timestamp} - {tag} EXIT\n")
    log_text.yview(tk.END)

    # Update the active students list in the GUI
    active_listbox.delete(0, tk.END)
    for student in sorted(active_students):
        active_listbox.insert(tk.END, student)

    # Log the event to the database
    try:
        log_event_db(tag, event_type)
    except Exception as e:
        status_label.config(text=f"DB error: {e}", fg="red")

    # Send email notification
    try:
        send_email(tag, event_type, timestamp)
    except Exception as e:
        status_label.config(text=f"Email error: {e}", fg="red")

def rfid_polling(ser, queue):
    """
    Background thread: continuously read RFID tags and enqueue them.
    """
    import time
    while True:
        try:
            if ser:
                tag = ser.readline().decode().strip()
                if tag:
                    queue.put(tag)
            else:
                # No serial port connected; sleep to prevent busy looping
                time.sleep(0.1)
        except Exception as e:
            print(f"RFID read error: {e}")
            break

def main():
    # Set up the main GUI window
    root = tk.Tk()
    root.title("School Gate Monitoring")

    # Status label at the top
    status_label = tk.Label(
        root,
        text="Waiting for scan...",
        font=("Arial", 12)
    )
    status_label.pack(pady=5)

    # Main frame containing the log and active students list
    main_frame = tk.Frame(root)
    main_frame.pack(fill='both', expand=True)

    # Log display: a scrollable text widget
    log_text = scrolledtext.ScrolledText(
        main_frame,
        width=60, height=20,
        state='normal'
    )
    log_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    # Active students list on the right
    active_frame = tk.Frame(main_frame)
    active_frame.pack(side='right', fill='y', padx=5, pady=5)
    tk.Label(active_frame, text="Active Students:").pack()
    active_listbox = tk.Listbox(active_frame, width=30, height=20)
    active_listbox.pack(side='left', fill='y')

    # Scrollbar for the active listbox
    scrollbar = tk.Scrollbar(active_frame, orient='vertical')
    scrollbar.config(command=active_listbox.yview)
    scrollbar.pack(side='right', fill='y')
    active_listbox.config(yscrollcommand=scrollbar.set)

    # Try to open the serial port for the RFID reader
    try:
        ser = serial.Serial('COM3', 9600, timeout=0.1)
    except Exception as e:
        ser = None
        print(f"Serial port error: {e}")

    # Start a background thread to poll RFID tags
    import queue
    tag_queue = queue.Queue()
    polling_thread = Thread(
        target=rfid_polling,
        args=(ser, tag_queue),
        daemon=True
    )
    polling_thread.start()

    # Periodically check the queue for new RFID scans
    def check_queue():
        try:
            tag = tag_queue.get_nowait()
        except Exception:
            pass
        else:
            process_tag(tag, status_label, log_text, active_listbox)
        root.after(100, check_queue)

    root.after(100, check_queue)
    root.mainloop()

if __name__ == "__main__":
    main()
