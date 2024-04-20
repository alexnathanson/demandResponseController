# 
from component import Component, Data
import asyncio
import components.Bluetti.AC180 as AC180
import time

# frequency of logging in minutes
updateRate = 1

#async def getBluetti():

#async def getINA219():
myMac = 'DC:8A:6F:FD:79:66'

async def main():
	myData = Data()

	component = Component(myMac)


	while True:
		myData.setIna219(component.ina219Get())

		await AC180.getData(myMac)
		time.sleep(5)

		print(myData)

if __name__ == "__main__":
    asyncio.run(main())