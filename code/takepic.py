import numpy as np
import cv2

lowerOR = np.array([0,105,65])
upperOR = np.array([22,215,180])
lowerBL = np.array([90,72,10])
upperBL = np.array([130,255,180])

vs = cv2.VideoCapture(0)
_, frame = vs.read()
frame = cv2.flip(frame, -1)

# Contour detection
'''
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lowerOR, upperOR)
image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
count = 0
for pic, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area < 5000:
        continue
    count += 1
    print(area)
    x, y, w, h = cv2.boundingRect(contour)
    frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
print(count)
'''
cv2.imwrite("a.jpg", frame)
vs.release()
