import cv2
import numpy as np
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Function to detect motion in a specified region of interest (ROI)
def detect_motion(roi, first_frame, threshold=50):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    # Ensure the sizes match
    if gray.shape != first_frame.shape:
        gray = cv2.resize(gray, (first_frame.shape[1], first_frame.shape[0]))
    
    # Compute the absolute difference between the current frame and the background
    delta = cv2.absdiff(first_frame, gray)
    
    # Threshold the delta image to get the motion areas
    thresh = cv2.threshold(delta, threshold, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

# Function to parse bounding boxes from environment variables
def parse_bounding_box(env_var):
    try:
        x, y, w, h = map(int, os.getenv(env_var).split(','))
        return (x, y, w, h)
    except Exception as e:
        print(f"Error parsing {env_var}: {e}")
        return None

# Load bounding boxes from environment variables
bounding_boxes = [
    parse_bounding_box('LANDFILL_BOX'),
    parse_bounding_box('RECYCLABLE_BOX'),
    parse_bounding_box('ORGANIC_BOX')
]

# Filter out None values in case of errors
bounding_boxes = [box for box in bounding_boxes if box is not None]

# Define labels for the bins
bin_labels = ['Landfill', 'Recyclable', 'Organics']

# Maintain the first frames and previous contour counts across function calls
first_frames = None
previous_contour_counts = [0] * len(bounding_boxes)

def draw_bounding_boxes(frame):
    """Draw bounding boxes for all bins."""
    for (x, y, w, h) in bounding_boxes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Blue color for bounding boxes
    return frame

def process_frame(frame):
    global first_frames
    global previous_contour_counts
    
    # Uncomment the following line to always draw bounding boxes
    # frame = draw_bounding_boxes(frame)

    detected_bin = None
    if first_frames is None:

        # Preprocess the first frame for each bounding box
        first_frames = []
        i = 0
        for (x, y, w, h) in bounding_boxes:
            roi = frame[y:y+h, x:x+w]
            first_frame = cv2.GaussianBlur(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            first_frames.append(first_frame)

            # Save the first frame for inspection in the src_livestream directory
            cv2.imwrite(os.path.join('src_livestream', 'images', f'first_frame_{bin_labels[i]}.png'), roi)
            print(f"Saved first frame for {bin_labels[i]} to src_livestream/images/first_frame_{bin_labels[i]}.png")
            i += 1

        return frame  # Return the original frame on the first pass

    for i, (x, y, w, h) in enumerate(bounding_boxes):
        roi = frame[y:y+h, x:x+w]
        contours = detect_motion(roi, first_frames[i])

        # Print the contour count only if it changes
        if len(contours) != previous_contour_counts[i]:
            print(f"Contours detected in {bin_labels[i]}: {len(contours)}")
            previous_contour_counts[i] = len(contours)

        if len(contours) > 0:
            detected_bin = bin_labels[i]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'Waste detected in: {detected_bin}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            break

    return frame