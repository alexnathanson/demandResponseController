class Component:
	def __init__(self, name):
		self.name = name

	def data(self):
		pass

# class INA(Component):
# 	def __init__(self, name='ina219'):
# 		super().__init__(name) 
# 		self.name = 'name'
# 		self.recent = {'voltage':None, 'current':None,'power':None}


import RPi.GPIO as GPIO
class DigitalLogger():
	def __init__(self, pin = 23):
		self.pin = 23
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)

	def setState(self,state):
		if state == HIGH
			GPIO.output(self.pin, GPIO.HIGH)
		elif state == LOW
			GPIO.output(self.pin, GPIO.LOW)
			GPIO.cleanup()

	# returns 1 if on and 0 if off
	def getState(self):
		return GPIO.input(self.pin)

	def switchState(self):
		if self.getState():
		self.setState(LOW)
	else:
		self.setState(HIGH)