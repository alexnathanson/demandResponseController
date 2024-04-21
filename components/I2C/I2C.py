# Adafruit INA260
# source: https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

'''
Default Address for Adafruit's INA260 is 40
If these pins are soldered the address is as follows:
A0 = 1000001 = 41
A1 = 1000100 = 44 = 0x2C
A0 & A1 = 1000101 =45 
INA260 datasheet w/ Address Table: https://www.ti.com/lit/ds/symlink/ina260.pdf 
'''

import time
import board
import busio
import adafruit_ina260
#from adafruit_bus_device.i2c_device import I2CDevice

#i2c = busio.I2C(board.SCL, board.SDA)
#print(dir(i2c))
#ina260 = adafruit_ina260.INA260(i2c,0x2C)
#ina260 = I2CDevice(i2c,0x2C)
'''
print(dir(ina260.i2c_device))
print("Device Address:")
print(ina260.i2c_device.device_address)
'''

# scan all I2C Devices
# source: https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/i2c-devices
REGISTERS = (0, 256) # Range of registers to read from
REGISTER_SIZE = 2 #Number of bytes to read from each register

# Initialize
i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass

def ina260_device(i,adr):
    return adafruit_ina260.INA260(i, adr)


print('scanning I2C devices...')
devices = i2c.scan()
while len(devices) < 1:
    print('scnaning I2C devices...')
    devices = i2c.scan()

for d in devices:
    print(hex(d))
    ina260 = ina260_device(i2c,hex(d))

while len(devices) >= 1:
    print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
        % (ina260.current, ina260.voltage, ina260.power)
    )
    time.sleep(2)
