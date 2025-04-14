
# tracker_logic.py

import cv2  # OpenCV for drawing and frame manipulation
import numpy as np  # Numpy for handling arrays of detections
from ultralytics import YOLO  # YOLO model for person detection
from ultralytics.utils import LOGGER  # Logger to suppress YOLO output
LOGGER.setLevel("ERROR")  # Suppress YOLO logging for cleaner output

from short import Sort  # SORT tracker for tracking object IDs
from collections import deque  # Deque for maintaining object movement history
import time  # Time for cooldown handling and timestamps

# --- Model and Tracker Initialization ---
model = YOLO("yolov8n.pt")  # Load a YOLOv8 Nano model
tracker = Sort(max_age=100, min_hits=1, iou_threshold=0.05)  # Initialize SORT tracker with config

# --- Tracking Zone Boundaries and Parameters ---
cx1, cx2 = 240, 400  # Vertical lines on screen used for entry/exit detection
cooldown_time = 2  # Cooldown (seconds) to prevent double-counting the same ID
offset = 20  # Pixel offset from boundary to ensure meaningful crossing
history_length = 3  # How many past positions to track for movement analysis

# --- Tracking State ---
position_history = {}  # Holds previous x-coordinates of objects by ID
id_last_cross_time = {}  # Timestamp of last count for each ID to apply cooldown

# --- Total Counters ---
total_entered = 0  # Running total of entries
total_exited = 0  # Running total of exits

# --- Main Frame Processing Function ---
def process_frame(frame):
    global position_history, id_last_cross_time
    global total_entered, total_exited

    frame_entered = 0  # Entries for this frame
    frame_exited = 0  # Exits for this frame

    # --- Run YOLO Detection ---
    results = model(frame)[0]  # Get detection results from YOLO
    person_boxes = []

    for box in results.boxes:
        cls = int(box.cls[0])  # Get class ID
        if cls == 0 and box.conf[0] > 0.3:  # Only keep high-confidence person detections
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box corners
            conf = float(box.conf[0])
            person_boxes.append([x1, y1, x2, y2, conf])

    # --- Track Using SORT ---
    detections_array = np.array(person_boxes) if person_boxes else np.empty((0, 5))
    tracked_objects = tracker.update(detections_array)  # Get tracked object IDs

    for track in tracked_objects:
        x1, y1, x2, y2, obj_id = track.astype(int)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Center of bounding box

        # Filter out detections too high or low in the frame
        if cy < 100 or cy > 400:
            continue

        # Initialize position history for new IDs
        if obj_id not in position_history:
            position_history[obj_id] = deque(maxlen=history_length)

        position_history[obj_id].append(cx)  # Add current x-position to history

        if len(position_history[obj_id]) >= 2:
            prev_cx = position_history[obj_id][0]
            curr_cx = position_history[obj_id][-1]
            current_time = time.time()

            moving_right = curr_cx > prev_cx
            moving_left = curr_cx < prev_cx

            # Entry Detection
            if prev_cx < (cx1 - offset) and curr_cx >= (cx1 + offset) and moving_right:
                if obj_id not in id_last_cross_time or (current_time - id_last_cross_time[obj_id] > cooldown_time):
                    total_entered += 1
                    frame_entered += 1
                    id_last_cross_time[obj_id] = current_time
                    print(f"[ENTERED] ID {obj_id} at {int(current_time)}")

            # Exit Detection
            elif prev_cx > (cx2 + offset) and curr_cx <= (cx2 - offset) and moving_left:
                if obj_id not in id_last_cross_time or (current_time - id_last_cross_time[obj_id] > cooldown_time):
                    total_exited += 1
                    frame_exited += 1
                    id_last_cross_time[obj_id] = current_time
                    print(f"[EXITED] ID {obj_id} at {int(current_time)}")

        # Draw bounding box and info on the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID: {obj_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)

    # Draw static entry and exit lines
    cv2.line(frame, (cx1, 0), (cx1, frame.shape[0]), (0, 255, 0), 2)  # Entry line
    cv2.line(frame, (cx2, 0), (cx2, frame.shape[0]), (0, 0, 255), 2)  # Exit line

    # Draw count labels
    cv2.putText(frame, f'Total Entered: {total_entered}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Total Exited: {total_exited}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame_entered, frame_exited, frame  # Return per-frame counts and visual frame
