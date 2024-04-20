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
    GPIO.setup(gPin, GPIO.OUT)


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
    GPIO.cleanup()