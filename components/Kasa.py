# TP Link Kasa Smart Plug

'''
documentation:
https://python-kasa.readthedocs.io/en/latest/index.html
'''

#source: https://python-kasa.readthedocs.io/en/latest/smartdevice.html
import asyncio
from kasa import SmartPlug, Discover, Credentials


async def main():
	await found_devices = asyncio.run(Discover.discover())

	print([dev.alias for dev in found_devices])
    # p = SmartPlug("127.0.0.1")

    # await p.update()  # Request the update
    # print(p.alias)  # Print out the alias
    # print(p.emeter_realtime)  # Print out current emeter status

    # await p.turn_off()  # Turn the device off

if __name__ == "__main__":
    asyncio.run(main())