# 
import asyncio
#import components.Bluetti.AC180 as AC180
import time
from datetime import datetime
import board
import busio
import adafruit_ina260
import adafruit_ina219
import componentClasses.MCP3008 as MCP3008 


# =========================================================================
# Initialize Adafruit Power Sensors
i2c = busio.I2C(board.SCL, board.SDA)

ina219 = adafruit_ina219.INA219(i2c_bus = i2c,addr =0x40)
ina260 = adafruit_ina260.INA260(i2c_bus = i2c,address = 0x44)
# =========================================================================


# ===========================================================================================================
# Initialize MCP & CT sensor
# MCP3008 code source: https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx

#create SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO,MOSI=board.MOSI)
#create the chip select
cs = digitalio.DigitalInOut(board.D5)
# create mcp object
mcp = MCP.MCP3008(spi,cs)

# create analog input channel
chan0 = AnalogIn(mcp, MCP.P0) #pin 0
#chan1 = AnalogIn(mcp, MCP.P1)

RESOLUTION = 2 ** 16 #the mcp3008 is 10 bit, but the Adafruit libary is 16 bit
SUPPLYVOLTAGE = 3.3
# ===========================================================================================================



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

async def main():
	ct = Current_Transformer()

	#myData = Data()

	while True:
		#myData.setIna219(component.ina219Get())
		await INA(5)
		#await AC180.getData(myMac)
		await ct.run(10)

		time.sleep(5)

		print(myData)

if __name__ == "__main__":
    asyncio.run(main())