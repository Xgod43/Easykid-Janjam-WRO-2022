import RPi.GPIO as GPIO
from driver import CAR_Driver
import time

driver = CAR_Driver()
GPIO.setmode(GPIO.BCM)   
GPIO.setup(18, GPIO.IN)  
GPIO.setup(27, GPIO.IN) 

try: 
    driver.buzzer(100)
    time.sleep(0.5)
    while True:
        sensorL = GPIO.input(18)    
        sensorR = GPIO.input(27)  

        if not sensorL and not sensorR: # 11
            driver.carmotor(192, 0)
            time.sleep(0.1)
        elif sensorL and not sensorR: # 01
            driver.carmotor(192, 0)
            time.sleep(0.1)
        elif not sensorL and sensorR: # 10
            driver.carmotor(192, 255)
            time.sleep(0.1)
        else:
            driver.carmotor(192, 128)
            time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()