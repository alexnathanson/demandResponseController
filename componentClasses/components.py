import asyncio
import board
import busio
import adafruit_ina260
import adafruit_ina219
class INA():
	def __init__(self, name):
		self.name = name
		self.data = {}
		self.i2c = busio.I2C(board.SCL, board.SDA)
		if self.name == "INA219":
			self.sensor = adafruit_ina219.INA219(i2c_bus = self.i2c,addr =0x40)
		elif self.name == "INA260":
			self.sensor = adafruit_ina260.INA260(i2c_bus = self.i2c,address = 0x44)

	def getData(self):
		#timestamp = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
		self.data['current mA'] = round(self.sensor.current,3)
		self.data['power W'] = round(self.sensor.power,3)

		if self.name == "INA260":
			self.data['voltage V'] = round(self.sensor.voltage,3)
		elif self.name == "INA219":
			self.data['voltage V'] = round(self.sensor.bus_voltage, 3)

	async def run(self, freq=10):
		while True:
			self.getData()
			#print(self.data)
			await asyncio.sleep(freq)


import RPi.GPIO as GPIO
class DigitalLogger():
	def __init__(self, pin = 23):
		self.pin = 23
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)
		self.state = 0

	def setState(self,state):
		if state:
			self.state = 1
			GPIO.output(self.pin, GPIO.HIGH)
		else:
			self.state = 0
			GPIO.output(self.pin, GPIO.LOW)
	
	def cleanup(self):
		GPIO.output(self.pin, GPIO.LOW)
		GPIO.cleanup()

	# returns 1 if on and 0 if off
	def getState(self):
		self.state = GPIO.input(self.pin)
		return self.state

	def switchState(self):
		if self.getState():
			self.setState(False)
		else:
			self.setState(True)