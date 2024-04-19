#source https://github.com/warhammerkid/bluetti_mqtt/blob/main/bluetti_mqtt/discovery_cli.py

import asyncio
from bleak import BleakError, BleakScanner

async def scan_devices():
    print('Scanning....')
    devices = await BleakScanner.discover()
    if len(devices) == 0:
        print('0 devices found - something probably went wrong')
    else:
        for d in devices:
            print(f'Found {d.name}: address {d.address}')

def main():
    asyncio.run(scan_devices())

if __name__ == "__main__":
    main()
