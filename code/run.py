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

sL, sR, bt = 18, 27, 22
in1, in2, en = 19, 16, 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(sL, GPIO.IN) # Sensor left
GPIO.setup(sR, GPIO.IN) # Sensor right
GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP) # button
GPIO.setup(in1, GPIO.OUT) # In 1
GPIO.setup(in2, GPIO.OUT) # In 2
GPIO.setup(en, GPIO.OUT) # En

motor = GPIO.PWM(en, 1000)
motor.start(0) 
servo = AngularServo(7, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025, pin_factory=pigpio_factory)

# Lines
lowerBL = np.array([96,72,11])
upperBL = np.array([122,255,181])
lowerOR = np.array([0,103,100])
upperOR = np.array([22,212,255])

# Blocks
lowerGR = np.array([51,154,57])
upperGR = np.array([77,255,255])
lowerRD = np.array([0,149,52])
upperRD = np.array([10,255,126])

def drive(speed = 0, angle = 102, direction = 0):
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
    sensorR = GPIO.input(sR) 

    # Sensor logic
    #if not sensorL and not sensorR: # 11
    #    drive(35, 135, 1) # Forward left
    if sensorL and not sensorR: # 01
        drive(35, 135, 1) # Forward left
    elif not sensorL and sensorR: # 10
        drive(35, 50, 1) # Forward right
    else:
        return False
    time.sleep(0.25)
    drive(30, 98, 0) # Forward left
    return True

def turnTimer(times, dArgs=[0, 102, 0]):
    timeS = time.time()
    while time.time() - timeS < times:
        # Turning
        drive(*dArgs)
            
        #if sensorDetect():
        #    break

def findContour(mask, times, setArea=1000, name='something'):
    x, y, w, h = 0, 0, 0, 0
    image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
    drive(0, 102, 1)  
    time.sleep(1)
    print('[INFO] Waiting for the button to be pressed')
    while GPIO.input(22): # Not pressed
        pass
    time.sleep(1)
    print('[INFO] GO!')
    while True:
        turned = False
        ret, frame = cam.get()
        if not ret:
            continue
        frame = cv2.flip(frame, -1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        maskBL = cv2.inRange(hsv, lowerBL, upperBL)
        maskGR = cv2.inRange(hsv, lowerGR, upperGR) 
        maskRD = cv2.inRange(hsv, lowerRD, upperRD) 
        
        bx, by, bw, bh = findContour(maskBL, 0, 2000, 'BL')
        gx, gy, gw, gh = findContour(maskGR, 0, 1000, 'GR')
        rx, ry, rw, rh = findContour(maskRD, 0, 1000, 'RD')
        
        if gx > 180 and gw > 50 and gh > 120: 
            drive(30, 135, 0)
            time.sleep(0.5)
            drive(35, 135, 1)
            time.sleep(0.5)
            drive(30, 100, 1)
            time.sleep(1)
            drive(35, 50, 1)
            time.sleep(0.35)
            drive(30, 100, 1)
            time.sleep(0.25)
            drive(30, 100, 0)
            time.sleep(0.25)
            
        elif rx < 480 and rw > 50 and rh > 120:
            drive(30, 50, 0)
            time.sleep(0.5)
            drive(35, 50, 1)
            time.sleep(0.5)
            drive(30, 100, 1)
            time.sleep(1)
            drive(35, 135, 1)
            time.sleep(0.35)
            drive(30, 100, 1)
            time.sleep(0.25)
            drive(30, 100, 0)
            time.sleep(0.25)

        if by > 265:
            turnTimer(0.5, [25, 135, 0])
            turnTimer(1.6, [35, 135, 1])
            turnTimer(0.5, [25, 98, 0])
        #sD = sensorDetect()
        #if not sD:
        drive(25, 98, 1)
        
        

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
        frame = cv2.flip(frame, -1)

        # Image processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        maskBL = cv2.inRange(hsv, lowerBL, upperBL)
        maskOR = cv2.inRange(hsv, lowerOR, upperOR) 
        #mask = cv2.bitwise_or(maskOR, maskBL)
        #frameBL = cv2.bitwise_and(frame, frame, mask=maskBL)
        #frameOR = cv2.bitwise_and(frame, frame, mask=maskOR)

        ## Contours ##
        
        # Find Blue
        bx, by, bw, bh = findContour(maskBL, 0, 2000, 'BL')

        # Find Orange
        #ox, oy, ow, oh = findContour(maskOR, 0, 100, 'OR')

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
except KeyboardInterrupt:
    pass
    #cv2.imwrite('a.jpg', frame)
except Exception as e:
    print(e)

#print(f'[INFO] Total time: {time.time() - timeSince:.2f}s')
drive(0, 102, 0) # Forward center
GPIO.cleanup()
cam.shutdown()