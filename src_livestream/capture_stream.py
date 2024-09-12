import cv2
import numpy as np
from mss import mss
import time
from bin_detection_stream import process_frame  # Import the function to process frames
import screeninfo

# Close all previous OpenCV windows
cv2.destroyAllWindows()

# Define the screen region to capture based on your provided coordinates and size
monitor = {"top": 236, "left": 24, "width": 1439, "height": 807}

# Initialize mss for screen capture
sct = mss()

def capture_and_save_image():
    print("Switch to Google Chrome. Capturing image in 5 seconds...")
    time.sleep(5)
    
    # Capture the screen
    screenshot = sct.grab(monitor)
    img = np.array(screenshot)

    # Convert to a format OpenCV can use (from BGRA to BGR)
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # Save the captured frame as an image
    image_path = "captured_frame.png"
    cv2.imwrite(image_path, frame)
    print(f"Image saved to {image_path}")

    # Optionally, display the captured frame
    cv2.imshow("Captured Frame", frame)
    cv2.waitKey(0)  # Wait until a key is pressed
    cv2.destroyAllWindows()

def capture_stream():
    window_name = "Live Stream Capture"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Allow window resizing

    # Get screen dimensions
    screen = screeninfo.get_monitors()[0]
    screen_width, screen_height = screen.width, screen.height

    # Set the window size to match the screen's dimensions
    cv2.resizeWindow(window_name, screen_width, screen_height)

    # Introduce a delay to ensure the initial frame is correctly captured
    print("Waiting for 5 seconds to capture the initial frame...")
    time.sleep(5)

    try:
        while True:

            # Capture the screen
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)

            # Convert to a format OpenCV can use (from BGRA to BGR)
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Process the captured frame
            processed_frame = process_frame(frame)

            # Display the processed frame
            cv2.imshow(window_name, processed_frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Release resources and close all windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Uncomment the line below to capture and save an image
    # capture_and_save_image()

    # Uncomment the line below to start the livestream with motion detection
    capture_stream()
