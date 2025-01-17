import asyncio
import time
from pytz import timezone
from datetime import datetime, date
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
import pandas as pd

timezone = timezone('US/Eastern')

#start time for experiment is also the name of the file
expStart = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print('Starting experiment at ' + expStart)

run = 1 # experiment run count
firstRun = True

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

async def actuate(freq):
	#check battery %
	try:
		state = -1
		if ps.data == 100: #turn off charging from grid power
			state = 0
			if firstRun == False:
				run = run + 1 #starts at 100%, goes to 20%
				if run >= 4:
					exit(1) #shut down after 3 full runs
		elif ps.data <= 98: #turn on charging from grid power
			state = 1
			firstRun = False
			
		if state != -1:
			print('setting state to ' + str(state))
			dl.setState(state)
	except Exception as e:
		print(e)
		print('actuating error')

	await asyncio.sleep(freq)

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
	print("packaging data...")
	try:
		pData = {}

		pData['time'] = [datetime.now()]
		pData['run'] = [run]
		pData['battery'] = [data['Power Station']['total_battery_percent']]
		pData['ac_out'] = [data['Power Station']['ac_output_power']]
		pData['ac_in'] = [data['Power Station']['ac_input_power']]
		pData['dc_out'] = [data['Power Station']['dc_output_power']]
		pData['dc_in'] = [data['Power Station']['dc_input_power']]
		pData['r1'] = [data['R1']]
		if ina260 != False:
			pData['pv'] = [data['PV']['power W']]
		else:
			pData['pv'] = [False]
		if ina219 != False:
			pData['rpi']=[data['RPi']['power W']]
		else:
			pData['rpi']= [False]
		pData['load'] = [data['CT']['current A'] * 120] #convert CT Irms to W

		#dict to dataframe
		pData = pd.DataFrame.from_dict(pData)
	except:
		print('packaging problems')
		pData = pd.DataFrame()

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
    print("writing data at " + datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
    fileName = 'experiment/outputs/exp1_'+ expStart +'.csv'

    try:
        with open(fileName) as csvfile:
            df = pd.read_csv(fileName)
            df = pd.concat([df,newDf], ignore_index = True)
            #df = df.append(newDf, ignore_index = True)
            df.to_csv(fileName, sep=',',index=False)
    except Exception as e:
        print(e)
        newDf.to_csv(fileName, sep=',',index=False)

@atexit.register
def cleanup():
	dl.cleanup()
	print('Goodby')

if __name__ == "__main__":
    asyncio.run(main())