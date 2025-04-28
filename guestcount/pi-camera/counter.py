import sys
import time
import subprocess
from datetime import datetime, timedelta
from pytz import timezone
from ultralytics import YOLO
from picamera2 import Picamera2
from airtable import send_to_airtable

# Config
CX1, CX2 = 220, 280 #the are the boundary lines to detect people entering and exiting
BX1, BX2 = 190,290 # these are buffer zones
MIN_CONF = 0.3 # pi must have above 50% confidence to count an object as a person
FRAME_SIZE = (640, 480) # using this resolution to balance performance and detection accuracy
UPDATE_INTERVAL = 1200  # 20 minutes, 1200 seconds
EST = timezone('US/Eastern') # from pytz

def get_cpu_temp():
    try:
        return float(subprocess.getoutput("vcgencmd measure_temp | cut -f2 -d'=' | cut -f1 -d\"'\""))
    except:
        return 0.0

def should_run():
    """Check if current time is between 10 AM and 5 PM EST."""
    now = datetime.now(EST)
    return 10 <= now.hour < 17  # Simplified check

def main():
    # Initial operating hours check
    if not should_run():
        print("Outside operating hours (10 AM - 5 PM EST). Exiting cleanly.")
        sys.exit(0)

    # Initialize hardware
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": FRAME_SIZE, "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    
    model = YOLO('yolov5nu.pt') # this is a lighter version of yolov5 which helps the pi run smoother.
    counts = {'in': 0, 'out': 0}
    last_update = time.time()
    last_position = None

    try:
        print("Starting counter [IN:0 OUT:0] - Next update in 20:00")
        while True:
            # Continuous operating hours check
            if not should_run():
                print("\nOperating hours ended (5 PM EST). Shutting down.")
                if counts['in'] > 0 or counts['out'] > 0:
                    send_to_airtable(counts['in'], counts['out'])
                sys.exit(0)  # Clean exit
            start_time = time.time()
            frame = picam2.capture_array()[:, :, :3]
            
            # Detection
            results = model.track(frame, conf=MIN_CONF, imgsz=320, verbose=False)[0] #uses boT SORT tracking algorithm, its able to maintain the ID's of the objects using motion features
            fps = 1 / (time.time() - start_time)
            
            if results.boxes is not None and results.boxes.id is not None:
                boxes = results.boxes.xyxy.cpu().numpy()
                ids = results.boxes.id.cpu().numpy()
                
                for box, track_id in zip(boxes, ids):
                    x1, _, x2, _ = map(int, box)
                    current_x = (x1 + x2) // 2

                    if track_id in last_positions:
                        last_x = last_positions[track_id]
                        if last_x < BX1 and current_x >= BX1:
                            pass
                        elif last_x > BX2 and current_x <= BX2:
                            pass
                        if last_x < CX1 and current_x >= CX1:
                            counts['in'] += 1
                        elif last_x > CX2 and current_x <= CX2:
                            counts['out'] += 1

                    last_positions[track_id] = current_x

            
            # Single-line logging
            time_left = max(0, UPDATE_INTERVAL - (time.time() - last_update))
            print(
                f"\rFPS:{fps:.1f} "
                f"Temp:{get_cpu_temp():.1f}C "
                f"IN:{counts['in']} "
                f"OUT:{counts['out']} "
                f"Pos:{last_position or '-'} "
                f"Next:{timedelta(seconds=int(time_left))}",
                end="", flush=True
            )
            
            # 20-minute Airtable update
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
