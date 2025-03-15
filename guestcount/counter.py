import time
import torch
import cv2
import numpy as np
from short import Sort
from camera import Camera
from airtable import send_to_airtable

print("[INFO] Initializing camera...")
camera = Camera()
print("[INFO] Camera initialized successfully.")

print("[INFO] Loading YOLOv5n model...")
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
print("[INFO] YOLOv5n model loaded successfully.")

print("[INFO] Initializing SORT tracker...")
tracker = Sort(max_age=100, min_hits=1, iou_threshold=0.05)
print("[INFO] SORT tracker initialized with max_age=100, min_hits=1, iou_threshold=0.05.")

frame_width = 640
cx1, cx2 = 250, 450  # Green line (enter), Red line (exit)
offset = 50
print(f"[INFO] Counting lines set at cx1={cx1} and cx2={cx2} with offset={offset}.")

counter_in, counter_out = set(), set()
total_entered, total_exited = 0, 0
guests_captured = 0  # Incremental count for new entries
exits_captured = 0   # Incremental count for new exits
last_positions = {}
last_airtable_update = time.time()  # Track last Airtable update

def process_frame(frame):
    global total_entered, total_exited, guests_captured, exits_captured, last_positions, last_airtable_update

    if frame.shape[-1] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

    results = model(frame)
    detections = results.pandas().xyxy[0]
    person_boxes = [[row['xmin'], row['ymin'], row['xmax'], row['ymax'], row['confidence']]
                    for _, row in detections.iterrows() if row['name'] == 'person' and row['confidence'] > 0.3]
    detections_array = np.array(person_boxes) if person_boxes else np.empty((0, 5))

    tracked_objects = tracker.update(detections_array)
    cv2.line(frame, (cx1, 0), (cx1, frame.shape[0]), (0, 255, 0), 2)
    cv2.line(frame, (cx2, 0), (cx2, frame.shape[0]), (0, 0, 255), 2)

    for track in tracked_objects:
        x1, y1, x2, y2, obj_id = track.astype(int)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID: {obj_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)

        if obj_id in last_positions:
            last_cx = last_positions[obj_id]
            if last_cx < cx1 and cx >= cx1:
                if obj_id not in counter_in:
                    counter_in.add(obj_id)
                    total_entered += 1
                    guests_captured += 1
                    print(f"[INFO] ID {obj_id} entered (crossed cx1={cx1}). Total entered: {total_entered}")
            elif last_cx > cx2 and cx <= cx2:
                if obj_id not in counter_out:
                    counter_out.add(obj_id)
                    total_exited += 1
                    exits_captured += 1
                    print(f"[INFO] ID {obj_id} exited (crossed cx2={cx2}). Total exited: {total_exited}")
        last_positions[obj_id] = cx

    cv2.putText(frame, f'Entered: {total_entered}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Exited: {total_exited}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    print(f"[STATUS] Current totals - Entered: {total_entered}, Exited: {total_exited}")

    current_time = time.time()
    if current_time - last_airtable_update >= 1200:  # 20 minutes
        print(f"[INFO] Sending 20-min update to Airtable. Guests captured: {guests_captured}, Exits captured: {exits_captured}")
        send_to_airtable(guests_captured, exits_captured)
        guests_captured = 0
        exits_captured = 0
        last_airtable_update = current_time

    return frame

if __name__ == "__main__":
    print("[INFO] Starting main loop...")
    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                print("[ERROR] Failed to capture frame.")
                break
            processed_frame = process_frame(frame)
            cv2.imshow("Side View Person Counter", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(f"[INFO] Exiting early... Final counts - Entered: {total_entered}, Exited: {total_exited}")
                send_to_airtable(guests_captured, exits_captured)
                break
            time.sleep(0.005)  # Small delay to control frame rate
    except KeyboardInterrupt:
        print(f"[INFO] Stopped by user. Final counts - Entered: {total_entered}, Exited: {total_exited}")
        send_to_airtable(guests_captured, exits_captured)
    finally:
        camera.close()
        cv2.destroyAllWindows()        
