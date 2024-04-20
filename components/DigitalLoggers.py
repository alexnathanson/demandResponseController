# Digital Loggers Relay

'''
Circuit

L___    ____G
    \_/*
     |
     R
     |
'''

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

gPin = 23

try:
    print('Setting up...')
    GPIO.setup(gPin, GPIO.OUT)

    print("Running...")
    GPIO.output(gPin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(gPin, GPIO.LOW)
    time.sleep(2)
    GPIO.output(gPin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(gPin, GPIO.LOW)

except:
    print("Error")

finally:
    print('Cleaning up')
    GPIO.cleanup()