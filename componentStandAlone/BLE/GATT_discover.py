# import asyncio
# from bleak import BleakScanner, BleakClient

# # Replace with your BLE device's UUID
# TARGET_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"

# async def find_device_by_uuid():
#     devices = await BleakScanner.discover()
#     for device in devices:
#         if TARGET_UUID.lower() in device.metadata.get("uuids", []):
#             print(f"Found device: {device.name} ({device.address})")
#             return device.address  # Return the device address for connection
#     print("Device not found.")
#     return None

# async def list_services(device_address):
#     async with BleakClient(device_address) as client:
#         services = await client.get_services()
#         print(f"Connected to {device_address}\nServices:")
#         for service in services:
#             print(f"- {service.uuid}")
#             for char in service.characteristics:
#                 print(f"  Characteristic: {char.uuid} (Properties: {char.properties})")

# async def main():
#     device_address = await find_device_by_uuid()
#     if device_address:
#         await list_services(device_address)

# # Run the async functions
# asyncio.run(main())

##############################################
# ANOTHER VERSION AS ABOVE, BASICALLY THE SAME
##############################################

import asyncio
from bleak import BleakScanner, BleakClient

# Replace with your BLE device's UUID
TARGET_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"

async def find_device_by_uuid():
    devices = await BleakScanner.discover()
    for device in devices:
        if TARGET_UUID.lower() in (device.metadata.get("uuids") or []):
            print(f"Found device: {device.name} ({device.address})")
            return device.address  # Return the device address
    print("Device not found.")
    return None

async def list_services(device_address):
    async with BleakClient(device_address) as client:
        print(f"Connected to {device_address}")
        # Using `services` property instead of `get_services()`
        for service in client.services:
            print(f"- Service: {service.uuid}")
            for characteristic in service.characteristics:
                print(f"  Characteristic: {characteristic.uuid} (Properties: {characteristic.properties})")

async def main():
    device_address = await find_device_by_uuid()
    if device_address:
        await list_services(device_address)

# Run the async functions
asyncio.run(main())
