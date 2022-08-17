from xml.dom.expatbuilder import parseString
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
import RPi.GPIO as GPIO

from camera import camera
import numpy as np
import threading
import time
import cv2

cam = camera()
pigpio_factory = PiGPIOFactory()

sL,sC, sR, bt = 10,25, 9, 24
in1, in2, en = 19, 16, 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(sL, GPIO.IN) # Sensor left
GPIO.setup(sC, GPIO.IN) # Sensor cen
GPIO.setup(sR, GPIO.IN) # Sensor right
GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP) # button
GPIO.setup(in1, GPIO.OUT) # In 1
GPIO.setup(in2, GPIO.OUT) # In 2
GPIO.setup(en, GPIO.OUT) # En

motor = GPIO.PWM(en, 1000)
motor.start(0) 
servo = AngularServo(7, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025, pin_factory=pigpio_factory)

# Lines
lowerBL = np.array([108,169,48])
upperBL = np.array([117,255,140])
lowerOR = np.array([0,142,121])
upperOR = np.array([12,255,255])

# Blocks
lowerGR = np.array([0,255,58])
upperGR = np.array([179,255,255])
lowerRD = np.array([142,172,0])
upperRD = np.array([179,255,255])

def drive(speed = 0, angle = 90, direction = 0):
    if speed == 0 or direction == 0: # No movement
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        time.sleep(0.5)

    if speed > 100:
        speed = 100
    elif speed < 0:
        speed = 0

    if angle > 135:
        angle = 135
    elif angle < 45:
        angle = 45

    motor.ChangeDutyCycle(speed)
    servo.angle = angle
    if direction > 0: # Forward
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
    elif direction < 0: # Backward
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)

def sensorDetect():
    # Sensor inputs
    sensorL = GPIO.input(sL) 
    sensorC = GPIO.input(sC)   
    sensorR = GPIO.input(sR) 

    if not sensorL and not sensorC and not sensorR: # 111
        turnTimer(0.6, [20, 120, -1]) # left
    elif not sensorL and  sensorC and sensorR: # 100
        drive(25, 130, 1) # right
    elif sensorL and  sensorC and not sensorR: # 001
        drive(25, 50, 1) # left
    else:
        return False
    time.sleep(0.05)
    drive(40, 88, 1)
    return True

def turnTimer(times, dArgs=[0, 102, 0]):
    timeS = time.time()
    while time.time() - timeS < times:
        # Turning
        drive(*dArgs)
            
        #if sensorDetect():
        #    break

def findContour(mask, setArea=1000, name='something'):
    x, y, w, h = 0, 0, 0, 0
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour) 
        if area >= setArea:
            x, y, w, h = cv2.boundingRect(contour)
            print(f'~~~\nFound {name}!\nX: {x}, Y: {y}, W: {w}, H: {h}, Area: {area}\n~~~')
            break
    
    return x, y, w, h

def block():
    vs = threading.Thread(target=cam.update, daemon=True)
    vs.start()
    drive(0, 88, 1)  
    time.sleep(1)
    #
    # cv2.imwrite('test.jpg',frame)
    print('[INFO] Waiting for the button to be pressed')
    while GPIO.input(bt): # Not pressed
        pass
    time.sleep(0.5)
    print('[INFO] GO!')
    drive(0, 88, 0)
    numLine = 0
    while True:
        if numLine == 12:
            break
        ret, frame = cam.get()
        cv2.imwrite('test.jpg',frame)
        if not ret:
            continue
        
    
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        crop = hsv[:, 300:340]
        maskBL = cv2.inRange(crop, lowerBL, upperBL)
        maskOR = cv2.inRange(hsv, lowerOR, upperOR)
        maskGR = cv2.inRange(hsv, lowerGR, upperGR) 
        maskRD = cv2.inRange(hsv, lowerRD, upperRD) 
        
        bx, by, bw, bh = findContour(maskBL, 200, 'BL')
        ox, oy, ow, oh = findContour(maskOR, 100, 'OR')
        gx, gy, gw, gh = findContour(maskGR, 500, 'GR')
        rx, ry, rw, rh = findContour(maskRD, 500, 'RD')
        #cv2.imwrite('a.jpg', cv2.rectangle(maskGR, (gx, gy), (gx+gw, gy+gh), (0, 0 ,255), 2))    


        # if by > 210 and oy > 180 : # Lane In
        #     turnTimer(2, [20, 90, 0])
        #     turnTimer(0.2, [20, 90, 1])
        #     turnTimer(0.5, [20, 140, 1])
        #     turnTimer(1, [20, 50, 1])
        #     turnTimer(2, [20, 90, 0])
        #     numLine += 1
            
        if by > 320 : # Lane Mid  Lane Out
            turnTimer(0, [20, 88, 0])
            while True:
                turnTimer(0.8, [30, 68, 1])
                break
            time.sleep(0.01)
            numLine += 1


        elif gw > 30 and gh > 68 and gx < 420 : #green
            turnTimer(0.2, [20, 90, 0])
            turnTimer(0.8, [22, 112, -1])
            turnTimer(0.6, [22, 85, 1])
            turnTimer(0.4, [20, 115, 1])
            turnTimer(0.8, [20, 90, 0])

            
            
 
        elif not sensorDetect():
            drive(20, 88, 1)
            time.sleep(0.01)

    tS = time.time()
    while time.time() - tS < 2:
        if not sensorDetect():
            drive(30, 90, 1)
            time.sleep(0.01)


        
        

def main():
    vs = threading.Thread(target=cam.update, daemon=True)
    vs.start()
    drive(0, 102, 1)  
    time.sleep(1)
    print('[INFO] Waiting for the button to be pressed')
    while GPIO.input(22): # Not pressed
        pass
    time.sleep(1)
    print('[INFO] GO!')
    startTime = time.time()
    while time.time() - startTime < 300:
        # Acquire a frame from the camera
        ret, frame = cam.get()
        if not ret:
            continue
        #frame = cv2.flip(frame, -1)

        # Image processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        maskBL = cv2.inRange(hsv, lowerBL, upperBL)
        maskOR = cv2.inRange(hsv, lowerOR, upperOR) 
        #mask = cv2.bitwise_or(maskOR, maskBL)
        #frameBL = cv2.bitwise_and(frame, frame, mask=maskBL)
        #frameOR = cv2.bitwise_and(frame, frame, mask=maskOR)

        ## Contours ##
        
        # Find Blue
        bx, by, bw, bh = findContour(maskBL, 2000, 'BL')

        # Find Orange
        #ox, oy, ow, oh = findContour(maskOR, 100, 'OR')

        if by > 265:
            turnTimer(0.5, [25, 135, 0])
            turnTimer(1.6, [35, 135, 1])
            turnTimer(0.5, [25, 98, 0])
        sD = sensorDetect()
        if not sD:
            drive(25, 98, 1)

    return startTime

try:
    #timeSince = main()
    block()
    
    # while True: 
    #     sensorDetect()
except KeyboardInterrupt:
    pass
    #cv2.imwrite('a.jpg', frame)
except Exception as e:
    print(e)

#print(f'[INFO] Total time: {time.time() - timeSince:.2f}s')
drive(0, 90, 0) # Forward center
GPIO.cleanup()
cam.shutdown()