import numpy as np
import cv2

lowerGR = np.array([60,105,24])
upperGR = np.array([72,255,63])
lowerRD = np.array([0,128,49])
upperRD = np.array([10,255,97])
vs = cv2.VideoCapture(0)
_, frame = vs.read()
frame = cv2.flip(frame, -1)
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
maskGR = cv2.inRange(frame, lowerGR, upperGR) 
maskRD = cv2.inRange(frame, lowerRD, upperRD) 
mask = cv2.bitwise_or(maskGR, maskRD)
frame = cv2.bitwise_and(frame, frame, mask=mask)
image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
count = 0
for pic, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area < 1000:
        continue
    count += 1
    x, y, w, h = cv2.boundingRect(contour)
    
    print(f'X: {x}, Y: {y}, W: {w}, H: {h}, Area: {area}')
    frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
print(count)
cv2.imwrite('a.jpg', frame)
cv2.imwrite('b.jpg', maskGR)
cv2.imwrite('c.jpg', maskRD)
vs.release()
