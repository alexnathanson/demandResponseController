import asyncio
import time
from pytz import timezone
from datetime import datetime
import math
from componentClasses.components import DigitalLogger as DL
from componentClasses.components import INA
from componentClasses.currentTransformer import Current_Transformer as CT 
from componentClasses.powerstation import BluettiAC180 as AC180
import atexit
from mqtt_participant import EnergyController

timezone = timezone('US/Eastern')

myMac = 'DC:8A:6F:FD:79:66'

dl = DL()
ct = CT()

psMac = 'DC:8A:6F:FD:79:66'
ps = AC180(psMac)

ina219 = INA('INA219')
ina260 = INA('INA260')

mqtt = EnergyController()

async def actuate(freq):
	lastmsg = 0

	while True:
		print('actuating!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
		if 'msg_timestamp' in mqtt.data.keys() and mqtt.data['msg_timestamp'] != lastmsg:
			lastmsg = mqtt.data['msg_timestamp']
			print('switching state!')
			dl.switchState()
		else:
			print('not switching state')
		await asyncio.sleep(freq)

# this packages up all the data for MQTT publishing
async def log(freq):
	allData = {

	}

	while True:
		print('*******************************************')
		print('logging!')

		allData['CT'] = ct.data # current
		allData['Power Station'] = ps.data #battery %, power, etc
		allData['RPi'] = ina219.data # current, voltage, power
		allData['PV'] = ina260.data # current, voltage, power
		allData['R1'] = dl.state #

		print(allData)
		print('*******************************************')

		mqtt.publish(packageData(allData))
		await asyncio.sleep(freq)

def packageData(data):

	pData = {}

	pData['battery'] = data['Power Station']['total_battery_percent']
	pData['ac_out'] = data['Power Station']['ac_output_power']
	pData['ac_in'] = data['Power Station']['ac_input_power']
	pData['dc_out'] = data['Power Station']['dc_output_power']
	pData['dc_in'] = data['Power Station']['dc_input_power']
	pData['r1'] = data['R1']
	pData['pv'] = data['PV']['power W']
	pData['rpi']=data['RPi']['power W']
	pData['load'] = data['CT'] * 120 #convert CT Irms to W

	return pData
	
async def main():
	mqtt.start()

	t1 = asyncio.create_task(ina219.run(5))
	t2 = asyncio.create_task(ina260.run(5))
	t3 = asyncio.create_task(ct.run(10))
	t4 = asyncio.create_task(log(60))
	t5 = asyncio.create_task(actuate(30))
	t6 = asyncio.create_task(ps.run(60))
	#t7 = asyncio.create_task(mqtt.start())
	

	await t1
	await t2
	await t3
	await t4
	await t5
	await t6
	#await t7

@atexit.register
def cleanup():
	dl.cleanup()
	print('Goodby')

if __name__ == "__main__":
    asyncio.run(main())