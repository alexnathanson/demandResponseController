# 
from components import Component
import asyncio
import components.Bluetti.AC180

# frequency of logging in minutes
updateRate = 1

#async def getBluetti():

#async def getINA219():
myMac = 'DC:8A:6F:FD:79:66'

async def main():
	component = Component(myMac)


	while True:
		await component.ina219Get()
		await getData(myDevice)
		time.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())