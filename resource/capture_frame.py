import cv2
import os

# Open video capture
cap = cv2.VideoCapture('./video/bin_detection.mp4')

# Read the first frame
ret, frame = cap.read()
if ret:
    # Save the frame as an image in the 'resource/frame' directory
    frame_path = './resource/frame/frame_for_bounding_box.jpg'
    cv2.imwrite(frame_path, frame)
    print(f"Frame saved as '{os.path.abspath(frame_path)}'")
else:
    print("Failed to read video")

# Release video capture
cap.release()
