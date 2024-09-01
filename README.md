# A Holistic Approach Towards Smart Waste Management

In Australia, kerbside bin collection is managed by local councils, and proper waste sorting is critical to reducing contamination. This project aims to develop an intelligent system that uses a camera and motion detection to monitor and analyze waste disposal in kerbside bins (organic, recyclable, and general waste bins). The system automatically detects when waste is placed in a bin, identifies the type of waste, and determines if it is correctly sorted. Privacy concerns are addressed by blurring the surroundings in the recorded video.

## Features

- **Automatic Motion Detection:** The system activates recording when motion is detected near the bins.
- **Bin Identification:** Identifies the specific bin (organic, recyclable, or general waste) where the waste is placed.
- **Object Detection and Classification:** Detects and classifies waste items to ensure they are correctly sorted.
- **Privacy Protection:** Blurs surroundings in the video to protect individual privacy.
- **User Feedback:** Provides feedback on whether waste disposal was correct or if contamination was detected.

## System Components

- **Camera:** Positioned above the kerbside bins, records videos with minimal coverage of surroundings. Motion detection triggers the camera to start recording when movement is detected.
- **Jupyter Notebook:** Used for implementing object detection, bin identification, and privacy protection processes using Python libraries like OpenCV and TensorFlow.
