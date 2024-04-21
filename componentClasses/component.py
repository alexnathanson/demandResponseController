class Component:
	def __init__(self, name):
		self.name = name

	def data(self):
		pass

class INA(Component):
	def __init__(self, name='ina219'):
		super().__init__(name) 
		self.name = 'name'
		self.recent = {'voltage':None, 'current':None,'power':None}
