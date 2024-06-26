# Adafruit INA260 
# source: https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_ina260

i2c = busio.I2C(board.SCL, board.SDA)

#default addrss is 40
ina260 = adafruit_ina260.INA260(i2c_bus=i2c,address=0x44)

while True:
    print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
        % (ina260.current, ina260.voltage, ina260.power)
    )
    time.sleep(1)