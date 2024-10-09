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

## Curl Commands

### Command to list all the attached devices

```sh
curl.exe -H "Authorization: Bearer <Access Token>" `
     "https://smartdevicemanagement.googleapis.com/v1/enterprises/<Project-ID>/devices"
```

### Command to generate access token

```sh
curl.exe -X POST https://oauth2.googleapis.com/token `
-H "Content-Type: application/x-www-form-urlencoded" `
-d "client_id=CLIENT_ID" `
-d "client_secret=CLIENT_SECRET" `
-d "code=AUTHORIZATION_CODE" `
-d "grant_type=authorization_code" `
-d "redirect_uri=REDIRECT_URI"
```

### Potentially useful dataset

| **SNo** | **Dataset**                                                                                                                                                                                         | **Format**                                                                            |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 1       | [Classification Model for Waste Materials in Residential Areas Dataset](https://universe.roboflow.com/thesis-project-sacr3/classification-model-for-waste-materials-in-residential-areas/dataset/4) | **TXT**(YOLOv5, YOLOv7, YOLOv8, YOLOv9, YOLOv11), **XML**(Pascal VOC), **JSON**(COCO) |
| 2       | [Waste Segergation Dataset](https://universe.roboflow.com/chinmay-vinarkar/waste-segergation/dataset/17)                                                                                            | **TXT**(YOLOv5, YOLOv7, YOLOv8, YOLOv9, YOLOv11), **XML**(Pascal VOC), **JSON**(COCO) |
| 3       | [Zero Waste Dataset](https://universe.roboflow.com/modern-academy-for-engineering/zero-waste-lomnz/dataset/9)                                                                                       | **TXT**(YOLOv5, YOLOv7, YOLOv8, YOLOv9, YOLOv11), **XML**(Pascal VOC), **JSON**(COCO) |

### YOLOv5 Algorithm Execution

```bash
python train.py \
  --img 640 \
  --batch 32 \
  --epochs 20 \
  --data /home/sachinj/yolo_version5/txt/data.yaml \
  --weights yolov5s.pt \
  --hyp data/hyps/hyp.custom.yaml
```

### YOLOv7 Algorithm Execution

```bash
python train.py \
  --img 640 \
  --batch 32 \
  --epochs 20 \
  --data /home/sachinj/yolo_version7/txt/data.yaml \
  --weights yolov7.pt \
  --hyp data/hyp.custom.yaml \
  --workers 8
```

### YOLOv8 Algorithm Execution

```bash
CUDA_VISIBLE_DEVICES=0,1 yolo train data=/home/sachinj/yolo_version5/txt/data.yaml model=yolov8s.pt batch=64 epochs=20 imgsz=640 lr0=0.005 lrf=0.1 momentum=0.9 weight_decay=0.0005 device=0,1
```

### YOLOv9 Algorithm Execution

```bash
torchrun --nproc_per_node=1 train_dual.py --img 640 --batch 48 --epochs 20 --data /home/sachinj/yolo_version9/txt/data.yaml --weights yolov9-s-converted.pt --hyp /home/sachinj/yolo_version9/yolov9/data/hyps/hyp.custom.yaml --cfg models/detect/yolov9-s.yaml --device 0 --workers 8
```