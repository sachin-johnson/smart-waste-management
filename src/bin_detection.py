import cv2
import os

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

# Open video capture
video_path = './video/bin_detection_7.mp4'
cap = cv2.VideoCapture(video_path)

# Read the first frame as the background for motion detection
ret, frame = cap.read()
if not ret:
    print(os.path.abspath(video_path))
    print("Failed to read video")
    cap.release()
    exit()

# Define bounding boxes for each bin
bounding_boxes = [
    (470, 0, 324, 450),  # Landfill bin
    (820, 0, 350, 450),  # Recyclable bin
    (1188, 0, 317, 450)  # Organic bin
]

# Preprocess the first frame for each bounding box
first_frames = []
for (x, y, w, h) in bounding_boxes:
    roi = frame[y:y+h, x:x+w]
    first_frame = cv2.GaussianBlur(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    first_frames.append(first_frame)

# Define labels for the bins
bin_labels = ['Landfill', 'Recyclable', 'Organics']

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    detected_bin = None
    for i, (x, y, w, h) in enumerate(bounding_boxes):
        roi = frame[y:y+h, x:x+w]
        contours = detect_motion(roi, first_frames[i])
        
        if len(contours) > 0:
            detected_bin = bin_labels[i]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'Waste detected in: {detected_bin}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            break
    
    # Display the frame
    cv2.imshow('Bin Detection', frame)
    
    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()