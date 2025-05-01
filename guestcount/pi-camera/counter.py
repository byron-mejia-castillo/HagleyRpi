import sys
import time
import subprocess
from datetime import datetime, timedelta
from pytz import timezone
from ultralytics import YOLO
from picamera2 import Picamera2
from airtable import send_to_airtable

# Config
CX1, CX2 = 220, 280  # Center lines for counting
BX1, BX2 = 190, 290  # Buffer zones to avoid bounce noise
MIN_CONF = 0.25       # Increased confidence threshold to filter out false positives
FRAME_SIZE = (640, 480)
UPDATE_INTERVAL = 1200  # 20 minutes
EST = timezone('US/Eastern')

def get_cpu_temp():
    try:
        return float(subprocess.getoutput("vcgencmd measure_temp | cut -f2 -d'=' | cut -f1 -d\"'\""))
    except:
        return 0.0

def should_run():
    now = datetime.now(EST)
    return 10 <= now.hour < 22

def main():
    if not should_run():
        print("Outside operating hours (10 AM - 5 PM EST). Exiting cleanly.")
        sys.exit(0)

    # Initialize camera
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": FRAME_SIZE, "format": "RGB888"})
    picam2.configure(config)
    picam2.start()

    model = YOLO('yolov8n.pt')
    counts = {'in': 0, 'out': 0}
    last_update = time.time()
    last_positions = {}

    try:
        print("Starting counter [IN:0 OUT:0] - Next update in 20:00")
        while True:
            if not should_run():
                print("\nOperating hours ended (5 PM EST). Shutting down.")
                if counts['in'] > 0 or counts['out'] > 0:
                    send_to_airtable(counts['in'], counts['out'])
                sys.exit(0)

            start_time = time.time()
            frame = picam2.capture_array()[:, :, :3]

            results = model.track(frame, conf=MIN_CONF, imgsz=320, verbose=False)[0]
            fps = 1 / (time.time() - start_time)

            if results.boxes is not None and results.boxes.id is not None:
                boxes = results.boxes.xyxy.cpu().numpy()
                ids = results.boxes.id.cpu().numpy()

                for box, track_id in zip(boxes, ids):
                    x1, _, x2, _ = map(int, box)
                    current_x = (x1 + x2) // 2

                    last_x = last_positions.get(track_id)
                    if last_x is not None:
                        # Apply buffer zones around center lines
                        if last_x < CX1 and current_x >= CX1:
                            counts['in'] += 1
                        elif last_x > CX2 and current_x <= CX2:
                            counts['out'] += 1

                    last_positions[track_id] = current_x

            # Display stats
            time_left = max(0, UPDATE_INTERVAL - (time.time() - last_update))
            print(
                f"\rFPS:{fps:.1f} "
                f"Temp:{get_cpu_temp():.1f}C "
                f"IN:{counts['in']} "
                f"OUT:{counts['out']} "
                f"IDs:{len(last_positions)} "
                f"Next:{timedelta(seconds=int(time_left))}",
                end="", flush=True
            )

            if time.time() - last_update >= UPDATE_INTERVAL:
                send_to_airtable(counts['in'], counts['out'])
                counts = {'in': 0, 'out': 0}
                last_update = time.time()
                print(f"\rAirtable updated - Next in 20:00", end="")

            time.sleep(max(0, 0.1 - (time.time() - start_time)))

    except KeyboardInterrupt:
        if counts['in'] > 0 or counts['out'] > 0:
            send_to_airtable(counts['in'], counts['out'])
        print(f"\nFinal: IN:{counts['in']} OUT:{counts['out']}")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()

