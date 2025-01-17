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

runNum = 0 # experiment run count

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

#this assumes the battery starts at 100% when the program is run
async def actuate(freq):
	global runNum #starts at 0
	oneInc = False #one increment per run

	#check battery %
	while True:
		print(runNum)
		try:
			state = -1
			 #turn off charging from grid power if battery is full
			if ps.data['total_battery_percent'] == 100:
				state = 0
				#if its not the first run
				if oneInc == False:
					runNum = runNum + 1 #starts at 100%, goes to 20%
					oneInc = True;
					if runNum >= 4:
						exit(0) #shut down after 3 full runs
			# turn on charging from grid power if below threshold,
			# and keep on until 100%
			elif ps.data['total_battery_percent'] <= 99: 
				state = 1 
				oneInc = False

			if state != -1:
				dl.setState(state)
		except Exception as e:
			print(e)

		await asyncio.sleep(freq)

# this packages up all the data
# freq determines how often data should be logged
async def log(freq):
	allData = {
	}

	while True:
		#collect all the data
		allData['CT'] = ct.data # current
		allData['Power Station'] = ps.data #battery %, power, etc

		if ina219 != False:
			allData['RPi'] = ina219.data # current, voltage, power
		if ina260 != False:
			allData['PV'] = ina260.data # current, voltage, power
		allData['Relay'] = dl.state #

		#print(allData)

		#mqtt.publish(packageData(allData))
		writeData(packageData(allData))
		await asyncio.sleep(freq)

def packageData(data):
	print('packaging data...')
	try:
		pData = {}

		pData['time'] = [datetime.now()]
		pData['runNum'] = [runNum]
		pData['battery'] = [data['Power Station']['total_battery_percent']]
		pData['ac_out'] = [data['Power Station']['ac_output_power']]
		pData['ac_in'] = [data['Power Station']['ac_input_power']]
		pData['dc_out'] = [data['Power Station']['dc_output_power']]
		pData['dc_in'] = [data['Power Station']['dc_input_power']]
		pData['relay'] = [data['Relay']]
		if ina260 != False:
			pData['pv'] = [data['PV']['power W']]
		else:
			pData['pv'] = [False]
		if ina219 != False:
			pData['rpi']=[data['RPi']['power W']]
		else:
			pData['rpi']= [False]
		pData['ct'] = [data['CT']['current A'] * 120] #convert CT Irms to W

		print(pData)
		#dict to dataframe
		pData = pd.DataFrame.from_dict(pData)
	except Exception as e:
		print(e)
		pData = pd.DataFrame()

	return pData

async def main():
	frequency = 30
	#if these are at a higher frequency they should be averaged
	#instead of spitting out so much data
	if ina219 != False:
		t1 = asyncio.create_task(ina219.run(frequency))
	if ina260 != False:
		t2 = asyncio.create_task(ina260.run(frequency))

	t3 = asyncio.create_task(ct.run(frequency))
	t4 = asyncio.create_task(log(frequency)) #writes or sends data
	t5 = asyncio.create_task(actuate(frequency))
	t6 = asyncio.create_task(ps.run(frequency))
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
    fileName = 'experiment/outputs/exp1_'+ expStart +'.csv'
    print("writing data to " + fileName)
    
    try:
        with open(fileName) as csvfile:
            df = pd.read_csv(fileName)
            df = pd.concat([df,newDf], ignore_index = True)
            #df = df.append(newDf, ignore_index = True)
            df.to_csv(fileName, sep=',',index=False)
    except:
        #print(e)
        newDf.to_csv(fileName, sep=',',index=False)
    print('done writing')

@atexit.register
def cleanup():
	dl.cleanup()
	print('Goodby')

if __name__ == "__main__":
    asyncio.run(main())