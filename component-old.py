# A class for managing all components
import board
import busio
import adafruit_ina219
import adafruit_ina260
import asyncio
from bluetti_mqtt.bluetooth import (
    check_addresses, scan_devices, BluetoothClient, ModbusError,
    ParseError, BadConnectionError)
import datetime

class Data:
	def __init__(self, ina260=False, ina219=False, dl=False, kasa=False, ct=False,):
		self.timestamp = datetime.datetime.now().timestamp()
		self.bluetti_name = None
		self.bluetti_DC_in = None
		self.bluetti_DC_out = None
		self.bluetti_AC_in = None
		self.bluetti_AC_out = None
		self.ina219_voltage = 0
		self.ina219_current = 0
		self.ina219_power = 0

	def setIna219(self, data):
		self.ina219_voltage = data.voltage
		self.ina219_current = data.current
		self.ina219_power = data.power

class Component:
	def __init__(self, ina260=False, ina219=False, dl=False, kasa=False, ct=False, mac=False):
		self.digitalloggers = dl
		self.kasa = kasa
		self.ct = ct
		self.i2c = busio.I2C(board.SCL,board.SDA)
		self.ina219 = adafruit_ina219.INA219(self.i2c)
		#self.ina260 = adafruit_ina260.INA260(self.i2c)
		self.mac = mac

	async def ina219Get(self):
		# print("Bus Voltage: {} V".format(self.ina219.bus_voltage))
		# print("Shunt Voltage: {} mV".format(self.ina219.shunt_voltage / 1000))
		# print("Current: {} mA".format(self.ina219.current))
		# print("Power: {} W".format(self.ina219.power))
		data = {
			"voltage":self.ina219.bus_voltage,
			"current":self.ina219.current,
			"power":self.ina219.power
		}
		return data

	async def ina260Get(self):
		print(
	        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
	        % (self.ina260.current, self.ina260.voltage, self.ina260.power)
	    )

	# async def getData(self):
	#     myData={
	#     }

	#     devices = await check_addresses({self.mac})
	#     if len(devices) == 0:
	#         sys.exit('Could not find the given device to connect to')
	#     device = devices[0]

	#     print(f'Connecting to {device.address}')
	#     client = BluetoothClient(device.address)
	#     asyncio.get_running_loop().create_task(client.run())

	#     # Wait for device connection
	#     while not client.is_ready:
	#         print('Waiting for connection...')
	#         await asyncio.sleep(1)
	#         continue

	#     # Poll device
	#     #while True:
	#     for command in device.logging_commands:
	#         commandResponse = await log_command(client, device, command)
	#         for k,v in commandResponse.items():
	#             print(k + ": " + str(v))
	#             myData[k]=v