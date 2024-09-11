# from torch.cuda import is_available
# import os
# import cv2
# from ultralytics import YOLO
# from supervision import LabelAnnotator, Detections, BoxCornerAnnotator, Color

# class PersonDetection:
#     def __init__(self, capture_index, email_notification):
#         self.capture_index = capture_index
#         self.currentIntruderDetected = 0
#         self.email_notification = email_notification

#         # Load the model
#         self.model = YOLO("./weights/yolov8n.pt")

#         # Instanciate Supervision Annotators
#         self.box_annotator = BoxCornerAnnotator(color=Color.from_hex("#ff0000"),
#                                                 thickness=6,
#                                                 corner_length=30)
#         self.label_annotator = LabelAnnotator(color=Color.from_hex("#ff0000"),
#                                               text_color=Color.from_hex("#fff"))

#         self.device = 'cuda:0' if is_available() else 'cpu'

#     def predict(self, img):

#         # Detect and track object using YOLOv8 model
#         result = self.model.track(img, persist=True, device=self.device)[0]

#         # Convert result to Supervision Detection object
#         detections = Detections.from_ultralytics(result)

#         # In Yolov8 model, objects with class_id 0 refer to a person. So, we should filter objects detected to only consider person
#         detections = detections[detections.class_id == 0]

#         return detections


#     def plot_bboxes(self, detections: Detections, img):

#         labels = [f"Intruder #{track_id}" for track_id in detections.tracker_id if len(detections.tracker_id) > 0]

#         # Add the box to the image
#         annotated_image = self.box_annotator.annotate(
#             scene=img,
#             detections=detections
#             )

#         # Add the label to the image
#         annotated_image = self.label_annotator.annotate(
#             scene=annotated_image,
#             detections=detections,
#             labels=labels
#         )

#         return annotated_image


#     def __call__(self):
#         cap = cv2.VideoCapture(self.capture_index)
#         if not cap.isOpened():
#             raise AssertionError
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
#         frame_count = 0

#         try:
#             while True:
#                 ret, img = cap.read()
#                 if not ret:
#                     print("Failed to grab frame")
#                     break


#                 results = self.predict(img)
#                 if results:
#                     img = self.plot_bboxes(results, img)


#                     if len(results.class_id) > self.currentIntruderDetected: # We will send notication only when new person is detected

#                         # Let's crop each person detected and save it into images folder
#                         for xyxy, track_id in zip(results.xyxy,results.tracker_id):
#                             intruImg = img[int(xyxy[1]-25):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])]
#                             cv2.imwrite(f"./images/intruder_{track_id}.jpg",intruImg)

#                         # Send notification
#                         self.email_notification.send_email(len(results.class_id))

#                         # Then notification sent, we must delete all previous saved images
#                         delete_files("./images/")

#                         self.currentIntruderDetected = len(results.class_id)
#                 else:
#                     self.currentIntruderDetected = 0

#                 cv2.imshow('Intruder Detection', img)
#                 frame_count += 1

#                 if cv2.waitKey(1) == 27:  # ESC key to break
#                     break
#         finally:
#             cap.release()
#             cv2.destroyAllWindows()
#             self.email_notification.quit()


# # Function to delete file
# def delete_files(path):
#     files = os.listdir(path)

#     for file in files:
#         os.remove(os.path.join(path,file))

from torch.cuda import is_available
import os
import cv2
from ultralytics import YOLO
from supervision import LabelAnnotator, Detections, BoxCornerAnnotator, Color
import sqlite3
from datetime import datetime

class PersonDetection:
    def __init__(self, capture_index, email_notification):
        self.capture_index = capture_index
        self.currentIntruderDetected = 0
        self.email_notification = email_notification

        # Load the model
        self.model = YOLO("./weights/yolov8n.pt")

        # Instanciate Supervision Annotators
        self.box_annotator = BoxCornerAnnotator(color=Color.from_hex("#ff0000"),
                                                thickness=6,
                                                corner_length=30)
        self.label_annotator = LabelAnnotator(color=Color.from_hex("#ff0000"),
                                              text_color=Color.from_hex("#fff"))

        self.device = 'cuda:0' if is_available() else 'cpu'

        # Connect to (or create) the SQLite database
        self.conn = sqlite3.connect('intruder_log.db')
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intruders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                timestamp TEXT,
                image BLOB
            )
        ''')
        self.conn.commit()

    def save_intruder_to_db(self, track_id, intruder_image):
        cursor = self.conn.cursor()
        
        # Convert image to binary format
        _, img_encoded = cv2.imencode('.jpg', intruder_image)
        img_binary = img_encoded.tobytes()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO intruders (track_id, timestamp, image) 
            VALUES (?, ?, ?)
        ''', (track_id, timestamp, img_binary))

        self.conn.commit()

    def predict(self, img):
        # Detect and track object using YOLOv8 model
        result = self.model.track(img, persist=True, device=self.device)[0]

        # Convert result to Supervision Detection object
        detections = Detections.from_ultralytics(result)

        # In Yolov8 model, objects with class_id 0 refer to a person. So, we should filter objects detected to only consider person
        detections = detections[detections.class_id == 0]

        return detections

    def plot_bboxes(self, detections: Detections, img):
        if detections.tracker_id is None:
            tracker_ids = ['Unknown'] * len(detections.class_id)
        else:
            tracker_ids = detections.tracker_id

        labels = [f"Intruder #{track_id}" for track_id in tracker_ids]

        # Add the box to the image
        annotated_image = self.box_annotator.annotate(
            scene=img,
            detections=detections
        )

        # Add the label to the image
        annotated_image = self.label_annotator.annotate(
            scene=annotated_image,
            detections=detections,
            labels=labels
        )

        return annotated_image

    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        if not cap.isOpened():
            raise AssertionError
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
        frame_count = 0

        try:
            while True:
                ret, img = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                results = self.predict(img)
                if results:
                    img = self.plot_bboxes(results, img)

                    if len(results.class_id) > self.currentIntruderDetected: # We will send notification only when new person is detected

                        # Let's crop each person detected and save it into images folder
                        for xyxy, track_id in zip(results.xyxy, results.tracker_id or []):
                            intruImg = img[int(xyxy[1]-25):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])]
                            cv2.imwrite(f"./images/intruder_{track_id}.jpg",intruImg)
                            self.save_intruder_to_db(track_id, intruImg)

                        # Send notification
                        self.email_notification.send_email(len(results.class_id))

                        # Then notification sent, we must delete all previous saved images
                        delete_files("./images/")

                        self.currentIntruderDetected = len(results.class_id)
                else:
                    self.currentIntruderDetected = 0

                cv2.imshow('Intruder Detection', img)
                frame_count += 1

                if cv2.waitKey(1) == 27:  # ESC key to break
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.email_notification.quit()
            self.conn.close()

# Function to delete file
def delete_files(path):
    files = os.listdir(path)
    for file in files:
        os.remove(os.path.join(path,file))
