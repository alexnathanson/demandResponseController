# 
from components import Component
import asyncio

# frequency of logging in minutes
updateRate = 1

#async def getBluetti():

#async def getINA219():

async def main():
	component = Component()
	while True:
		await component.ina219Get()
		asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())