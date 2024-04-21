# 
import asyncio
#import components.Bluetti.AC180 as AC180
import time
from pytz import timezone
from datetime import datetime
import board
import busio
import adafruit_ina260
import adafruit_ina219
#import digitalio
#import adafruit_mcp3xxx.mcp3008 as MCP
#from adafruit_mcp3xxx.analog_in import AnalogIn
import math
#from componentClasses.component import INA
from componentClasses.currentTransformer import Current_Transformer as CT 

# =========================================================================
# Initialize Adafruit Power Sensors
i2c = busio.I2C(board.SCL, board.SDA)

ina219 = adafruit_ina219.INA219(i2c_bus = i2c,addr =0x40)
ina260 = adafruit_ina260.INA260(i2c_bus = i2c,address = 0x44)
# =========================================================================

timezone = timezone('US/Eastern')

# frequency of logging in minutes
updateRate = 1

#async def getBluetti():

#async def getINA219():
myMac = 'DC:8A:6F:FD:79:66'

async def INA(freq):
	pv = {}
	rpi = {}

	while True:
		timestamp = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
		pv['current'] = ina260.current
		pv['voltage'] = ina260.voltage
		pv['power'] = ina260.power

		rpi['current'] = ina219.current
		rpi['voltage'] = ina219.bus_voltage
		rpi['power'] = ina219.power

		print(pv)
		print(rpi)
		await asyncio.sleep(freq)

async def log(freq):
	while True:
		print('logging!')
		await asyncio.sleep(freq)

async def main():
	ct = CT()

	#myData = Data()

	loop = asyncio.get_event_loop()
	loop.create_task(INA(5))
	loop.create_task(ct.run(10))
	loop.create_task(log(60))
	loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())