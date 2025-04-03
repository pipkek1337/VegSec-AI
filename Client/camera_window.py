import tkinter as tk
from tkinter import messagebox
import cv2
import os
from PIL import Image, ImageTk
import threading
from datetime import datetime


class CameraWindow(tk.Toplevel):
    def __init__(self, parent, on_capture_callback):
        super().__init__(parent)
        self.title("Camera Capture")
        self.geometry("640x520")

        # Create a directory for captured images if it doesn't exist
        self.capture_dir = os.path.join(os.path.dirname(__file__), "captured_images")
        os.makedirs(self.capture_dir, exist_ok=True)

        # Camera and capture setup
        self.capture = cv2.VideoCapture(0)  # Use default camera
        self.on_capture_callback = on_capture_callback

        # Video feed label
        self.video_label = tk.Label(self)
        self.video_label.pack(padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=5)

        # Capture button
        self.capture_button = tk.Button(
            self, text="Capture Photo", command=self.start_capture
        )
        self.capture_button.pack(pady=10)

        # Cancel button
        self.cancel_button = tk.Button(
            self, text="Cancel", command=self.destroy
        )
        self.cancel_button.pack(pady=10)

        # Start video feed
        self.is_running = True
        self.video_thread = threading.Thread(target=self.update_video_feed)
        self.video_thread.daemon = True
        self.video_thread.start()

    def update_video_feed(self):
        while self.is_running:
            ret, frame = self.capture.read()
            if ret:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image and PhotoImage
                pil_img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=pil_img)

                # Update label in main thread
                self.after(0, self._update_video_label, photo)

            # Small delay to prevent CPU overuse
            cv2.waitKey(15)

    def _update_video_label(self, photo):
        try:
            self.video_label.config(image=photo)
            self.video_label.image = photo
        except:
            pass

    def start_capture(self):
        # Disable capture button to prevent multiple clicks
        self.capture_button.config(state=tk.DISABLED)

        # Update status
        self.status_label.config(text="Capturing photo...", fg="blue")

        # Start capture in a separate thread
        capture_thread = threading.Thread(target=self._capture_photo)
        capture_thread.daemon = True
        capture_thread.start()

    def _capture_photo(self):
        try:
            # Slight delay to show status
            import time
            time.sleep(1)

            # Capture frame
            ret, frame = self.capture.read()
            if ret:
                # Generate unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.capture_dir, f"captured_image_{timestamp}.jpg")

                # Save image (keep original BGR format for OpenCV)
                cv2.imwrite(filename, frame)

                # Update UI in main thread
                self.after(0, self._finalize_capture, filename)
            else:
                # Update UI in main thread if capture fails
                self.after(0, self._capture_failed)
        except Exception as e:
            # Update UI in main thread if any error occurs
            self.after(0, self._capture_failed, str(e))

    def _finalize_capture(self, filename):
        # Call parent's method to display and process the image
        self.on_capture_callback(filename)

        # Close camera window
        self.destroy()

    def _capture_failed(self, error_msg="Capture failed"):
        # Re-enable capture button
        self.capture_button.config(state=tk.NORMAL)

        # Show error
        self.status_label.config(text=error_msg, fg="red")

    def destroy(self):
        # Stop video feed and release camera
        self.is_running = False
        if hasattr(self, 'capture'):
            self.capture.release()
        super().destroy()