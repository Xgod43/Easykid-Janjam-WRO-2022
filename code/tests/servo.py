from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
from time import sleep

pigpio_factory = PiGPIOFactory()
servo =AngularServo(7, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025, pin_factory=pigpio_factory)
servo.angle = 90 #cen90 L50 R130
sleep(1)
