from picamera2 import Picamera2
import cv2

class Camera:
    def __init__(self):
        try:
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
            self.picam2.configure(config)
            self.picam2.start()
            print("PiCamera initialized successfully.")
        except Exception as e:
            print(f"Error initializing PiCamera: {e}")
            self.picam2 = None  

    def capture_frame(self):
        if self.picam2 is None:
            print("Camera not initialized. Returning empty frame.")
            return None  
        
        frame = self.picam2.captuare_array()
        return frame 

    def close(self):
        """Properly stops the camera."""
        if self.picam2:
            self.picam2.stop()
            print("Camera stopped.")

