# A class for managing all components
import board
import busio
import adafruit_ina219

class Component:
	def __init__(self, ina260=False, ina219=False, dl=False, kasa=False, ct=False):
		self.digitalloggers = digitalloggers
		self.kasa = kasa
		self.ct = ct
		self.i2c = busio.I2C(board.SCL,board.SDA)
		self.ina219 = adafruit_ina219.INA219(i2c)
		self.ina260 = adafruit_ina260.INA260(i2c)


	def ina219Get():
		print("Bus Voltage: {} V".format(ina219.bus_voltage))
		print("Shunt Voltage: {} mV".format(ina219.shunt_voltage / 1000))
		print("Current: {} mA".format(ina219.current))
		print("Power: {} W".format(ina219.power))


	def ina260Get():
		print(
	        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
	        % (ina260.current, ina260.voltage, ina260.power)
	    )