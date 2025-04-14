
# live_tracker.py

import cv2  # OpenCV for video capture and image processing
import time  # Time module for delays and timestamps
from datetime import datetime, timedelta  # For time-based scheduling
import pytz  # Handles timezone-aware datetime objects
from tracker_logic import process_frame  # Imports the object detection and tracking function
from airtable_push import push_to_airtable  # Function to send data to Airtable
from sdnotify import SystemdNotifier  # Allows communication with systemd watchdog

# --- Delayed Start Until 10:00 AM EST ---
eastern = pytz.timezone('America/New_York')
now = datetime.now(eastern)
ten_am = now.replace(hour=10, minute=0, second=0, microsecond=0)

# If it's before 10 AM, sleep until then
if now < ten_am:
    wait_seconds = (ten_am - now).total_seconds()
    print(f"[INFO] Waiting until 10:00 AM... sleeping for {int(wait_seconds)} seconds")
    time.sleep(wait_seconds)
else:
    print("[INFO] It's already past 10:00 AM — starting now.")

# --- Initialize systemd notifier for watchdog integration ---
notifier = SystemdNotifier()

# --- Parameter Initialization ---
frame_skip = 1  # Only process every nth frame (1 = every frame)
frame_count = 0  # Tracks the number of frames read
total_entered = 0  # Running total of people entered since last push
total_exited = 0  # Running total of people exited since last push
last_push_time = time.time()  # Time when data was last pushed to Airtable

print("[INFO] Starting live tracking...")
cap = cv2.VideoCapture(0)  # Open camera (device 0)

# If camera fails to open, terminate program
if not cap.isOpened():
    print("[ERROR] Cannot access camera.")
    exit()

# --- Main Loop: Frame Processing and Data Push ---
while True:
    ret, frame = cap.read()  # Read frame from camera
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    if frame_count % frame_skip == 0:
        # Perform guest detection and tracking
        entered, exited, updated_frame = process_frame(frame)
        total_entered += entered
        total_exited += exited

        # Push data to Airtable every 45 seconds
        current_time = time.time()
        if current_time - last_push_time >= 45:
            if total_entered > 0 or total_exited > 0:
                # Push only if there were new entries or exits
                push_to_airtable(total_entered, total_exited)
                total_entered = 0  # Reset counters after pushing
                total_exited = 0
            last_push_time = current_time
            notifier.notify("WATCHDOG=1")  # Send heartbeat to systemd watchdog

        # Optional debugging output to screen (comment for headless)
        cv2.imshow("Guest Tracker", updated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    frame_count += 1  # Increment frame counter

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
