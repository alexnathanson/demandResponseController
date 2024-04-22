import asyncio
import time
from pytz import timezone
from datetime import datetime
import math
from componentClasses.component import DigitalLogger as DL
from componentClasses.component import INA
from componentClasses.currentTransformer import Current_Transformer as CT 
from componentClasses.powerstation import BluettiAC180 as AC180

timezone = timezone('US/Eastern')

myMac = 'DC:8A:6F:FD:79:66'

dl = DL()
ct = CT()

psMac = 'DC:8A:6F:FD:79:66'
ps = AC180(psMac)

ina219 = INA('INA219')
ina260 = INA('INA260')

async def actuate(freq):
	
	while True:
		dl.switchState()
		await asyncio.sleep(freq)

# this packages up all the data for MQTT publishing
async def log(freq):
	data = {

	}

	while True:
		print('*******************************************')
		print('logging!')

		data['CT'] = ct.data
		data['Power Station'] = ps.data
		data['RPi'] = ina219.getData
		data['PV'] = ina260.getData
		data['R1'] = dl.state

		print(data)
		print('*******************************************')

		await asyncio.sleep(freq)

async def main():

	

	t1a = asyncio.create_task(ina219.run(5))
	t1b = asyncio.create_task(ina260.run(5))
	t2 = asyncio.create_task(ct.run(10))
	t3 = asyncio.create_task(log(60))
	t4 = asyncio.create_task(actuate(10))
	t5 = asyncio.create_task(ps.run(60))

	await t1a
	await t1b
	await t2
	await t3
	await t4
	await t5

if __name__ == "__main__":
    asyncio.run(main())