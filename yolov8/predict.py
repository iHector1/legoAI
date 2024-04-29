from ultralytics import YOLO
import cv2

model = YOLO("C:/Users/hecto/Documents/legoAI/yolov8/best.pt")  # load a model from a file

# Predict an image
img = cv2.imread("C:/Users/hecto/Documents/legoAI/yolov8/image.jpg")
results = model.predict(img)  # predict the image

cv2.imshow("Image", results.imgs[0])  # display the image