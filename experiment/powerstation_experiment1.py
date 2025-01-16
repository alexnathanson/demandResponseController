import asyncio
import time
from pytz import timezone
from datetime import datetime
import math
import sys
sys.path.append('..')
from demandResponseController.componentClasses.components import DigitalLogger as DL
from demandResponseController.componentClasses.components import INA
from demandResponseController.componentClasses.currentTransformer import Current_Transformer as CT 
from demandResponseController.componentClasses.powerstation import BluettiAC180 as AC180
import atexit
# from mqtt_participant import EnergyController
import csv
import os

timezone = timezone('US/Eastern')

myMac = 'DC:8A:6F:FD:79:66'

dl = DL()
ct = CT()

psMac = 'DC:8A:6F:FD:79:66'
ps = AC180(psMac)

try:
	ina219 = INA('INA219')
except:
	print('INA219 device not found')
	ina219 = False

try:
	ina260 = INA('INA260')
except:
	print('INA260 device not found')
	ina260 = False

async def actuate(state):

	print('setting state to ' + state)
	dl.setState(state)

# this packages up all the data
# freq determines how often data should be logged
async def log(freq):
	allData = {
	}

	while True:

		allData['CT'] = ct.data # current
		allData['Power Station'] = ps.data #battery %, power, etc

		if ina219 != False:
			allData['RPi'] = ina219.data # current, voltage, power
		if ina260 != False:
			allData['PV'] = ina260.data # current, voltage, power
		allData['R1'] = dl.state #

		#print(allData)

		#mqtt.publish(packageData(allData))
		writeData(packageData(allData))
		await asyncio.sleep(freq)

def packageData(data):

	pData = {}

	pData['battery'] = data['Power Station']['total_battery_percent']
	pData['ac_out'] = data['Power Station']['ac_output_power']
	pData['ac_in'] = data['Power Station']['ac_input_power']
	pData['dc_out'] = data['Power Station']['dc_output_power']
	pData['dc_in'] = data['Power Station']['dc_input_power']
	pData['r1'] = data['R1']
	if ina260 != False:
		pData['pv'] = data['PV']['power W']
	else:
		pData['pv'] = False
	if ina219 != False:
		pData['rpi']=data['RPi']['power W']
	else:
		pData['rpi']= False
	pData['load'] = data['CT']['current A'] * 120 #convert CT Irms to W
	return pData

async def main():

	if ina219 != False:
		t1 = asyncio.create_task(ina219.run(5))

	if ina260 != False:
		t2 = asyncio.create_task(ina260.run(5))

	t3 = asyncio.create_task(ct.run(10))
	t4 = asyncio.create_task(log(60)) #writes or sends data
	t5 = asyncio.create_task(actuate(30))
	t6 = asyncio.create_task(ps.run(60))
	#t7 = asyncio.create_task(mqtt.start())
	
	if ina219 != False:
		await t1
	if ina260 != False:
		await t2
	await t3
	await t4
	await t5
	await t6
	#await t7

def writeData(newDf):
    # create a new file daily to save data
    # or append if the file already exists
    fileName = 'outputs/exp1_'+str(datetime.date.today())+'.csv'

    try:
        with open(fileName) as csvfile:
            df = pd.read_csv(fileName)
            df = pd.concat([df,newDf], ignore_index = True)
            #df = df.append(newDf, ignore_index = True)
            df.to_csv(fileName, sep=',',index=False)
    except Exception as e:
        print(e)
        newDF.to_csv(fileName, sep=',',index=False)

@atexit.register
def cleanup():
	dl.cleanup()
	print('Goodby')

if __name__ == "__main__":
    asyncio.run(main())