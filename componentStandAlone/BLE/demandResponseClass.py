class demandResponse():
	def __init__(self, promise: float):
		self.name = name
		self.modes = ['DR','TOU']
		self.mode = self.modes[0]
		self.promise = promise #kW
		self.eventlength = 4
		self.baseline = 0
		self.performance = 0
		self.reliability = 0
		self.predictability = 0
		self.isEvent = False # flag to indiciate if event is going on
		self.isEventUpcoming = False
		self.timeToEvent = 0 # countdown hours until event

	#reports the power at each point in the system
	def getStatus(self):
		pass

	#set an amount of power to flex eveningly for the duration of the event
	def flexPower(self, watts, duration):
		pass

	#set an amount of energy to flex during the event
	def flexEnergy(self, wattHours, duration)
		pass

	#replacement
	def replace(self)
		pass

	def curtail(self)
		pass

	def shift(self)

	#charge battery from the grid
	def gridCharge()
		if not self.isEvent:
			pass