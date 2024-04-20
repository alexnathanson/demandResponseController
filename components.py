# A class for managing all components
import board
import busio
import adafruit_ina219
import adafruit_ina260
import asyncio

class Component:
	def __init__(self, ina260=False, ina219=False, dl=False, kasa=False, ct=False):
		self.digitalloggers = dl
		self.kasa = kasa
		self.ct = ct
		self.i2c = busio.I2C(board.SCL,board.SDA)
		self.ina219 = adafruit_ina219.INA219(self.i2c)
		self.ina260 = adafruit_ina260.INA260(self.i2c)


	async def ina219Get(self):
		print("Bus Voltage: {} V".format(self.ina219.bus_voltage))
		print("Shunt Voltage: {} mV".format(self.ina219.shunt_voltage / 1000))
		print("Current: {} mA".format(self.ina219.current))
		print("Power: {} W".format(self.ina219.power))


	async def ina260Get(self):
		print(
	        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
	        % (self.ina260.current, self.ina260.voltage, self.ina260.power)
	    )