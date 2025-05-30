import argparse
import asyncio
import base64
from bleak import BleakError
#from io import TextIOWrapper
import json
import sys
import textwrap
import time
from typing import cast
from bluetti_mqtt.bluetooth import (
    check_addresses, scan_devices, BluetoothClient, ModbusError,
    ParseError, BadConnectionError
)
from bluetti_mqtt.core import (
    BluettiDevice, ReadHoldingRegisters, DeviceCommand
)

#use the discover.py script to find your MAC address if unknown
myDevice = 'C8:A0:09:CD:DA:61'

async def log_command(client: BluetoothClient, device: BluettiDevice, command: DeviceCommand):
    response_future = await client.perform(command)
    try:
        response = cast(bytes, await response_future)
        if isinstance(command, ReadHoldingRegisters):
            body = command.parse_response(response)
            parsed = device.parse(command.starting_address, body)
            return parsed #print(parsed.keys())
        #log_packet(log_file, response, command)
    except (BadConnectionError, BleakError, ModbusError, ParseError) as err:
        print(f'Got an error running command {command}: {err}')
        #log_invalid(log_file, err, command)


async def getData(address: str):
    myData={
    }

    devices = await check_addresses({address})
    if len(devices) == 0:
        sys.exit('Could not find the given device to connect to')
    device = devices[0]

    print(f'Connecting to {device.address}')
    client = BluetoothClient(device.address)
    asyncio.get_running_loop().create_task(client.run())

    # Wait for device connection
    while not client.is_ready:
        print('Waiting for connection...')
        await asyncio.sleep(1)
        continue

    # Poll device
    #while True:
    for command in device.logging_commands:
        commandResponse = await log_command(client, device, command)
        for k,v in commandResponse.items():
            print(k + ": " + str(v))
            myData[k]=v
    
    #print(myData)

async def main():

    myData = await getData(myDevice)

if __name__ == "__main__":
    asyncio.run(main())
