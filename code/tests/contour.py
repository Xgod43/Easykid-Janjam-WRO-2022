import numpy as np
import cv2
vs = cv2.VideoCapture(0)
_, frame = vs.read()
frame = cv2.flip(frame, -1)
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#frame = cv2.circle(frame, (50, 120), 8, (0, 0, 255), -1) # 1
#frame = cv2.circle(frame, (590, 120), 8, (0, 0, 255), -1) # 2
#frame = cv2.circle(frame, (640, 480), 8, (0, 0, 255), -1) # 3
#frame = cv2.circle(frame, (0, 480), 8, (0, 0, 255), -1) # 4
lowerBL = np.array([90,72,10])
upperBL = np.array([130,255,180])
lowerOR = np.array([0,105,65])
upperOR = np.array([22,215,180])
maskOR = cv2.inRange(frame, lowerOR, upperOR) 
maskBL = cv2.inRange(frame, lowerBL, upperBL) 
mask = cv2.bitwise_or(maskOR, maskBL)
frame = cv2.bitwise_and(frame, frame, mask=mask)
image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
count = 0
for pic, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area < 100:
        continue
    count += 1
    x, y, w, h = cv2.boundingRect(contour)
     
    print(f'X: {x}, Y: {y}, W: {w}, H: {h}')
    frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
print(count)
cv2.imwrite('A.jpg', frame)
cv2.imwrite('B.jpg', maskOR)
cv2.imwrite('C.jpg', maskBL)
vs.release()
