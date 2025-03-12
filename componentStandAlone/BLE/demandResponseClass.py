class demandResponse():
	def __init__(self):
		self.name = name
		self.modes = ['DR','TOU']
		self.mode = self.modes[0]

	def getStatus(self):
		pass

	#disconnect loads
	def curtail(self):
		pass

	# connect loads to battery
	def replace(self):
		pass

	# schedule a load for another time
	def shift(self):
		pass

	#set an amount of power to flex eveningly for the duration of the event
	def flexPower(self, watts, duration):
		pass

	#set an amount of energy to flex during the event
	def flexEnergy(self, wattHours, duration)