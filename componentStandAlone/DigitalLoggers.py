# Digital Loggers Relay

'''
This can work without the NPN transistor by connecting one terminal directly to the GPIO pin and the other to ground,
but its probably best to have a transistor.

Circuit
R = 1.2K Ohms
T = 2N2222, BC546B, or similar

V+___L+

L-___    ____G
     \_/*
      |
      R
      |
    GPIO 23 (pin 16)
'''

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
gPin = 23

try:
    print('Setting up...')
    GPIO.setup(gPin, GPIO.OUT)

    print("Running...")
    print("HIGH")
    GPIO.output(gPin, GPIO.HIGH)
    time.sleep(2)
    print("LOW")
    GPIO.output(gPin, GPIO.LOW)
    time.sleep(2)
    print("HIGH")
    GPIO.output(gPin, GPIO.HIGH)
    time.sleep(2)
    print("LOW")
    GPIO.output(gPin, GPIO.LOW)
except:
    print("Error")
finally:
    print('Cleaning up.')
    GPIO.cleanup()