from ..enums.sensor_type import SensorType


class Sensor:
	name: str
	phasio_id: str
	type: SensorType

	def __init__(self, name: str, phasio_id: str, type: SensorType):
		self.name = name
		self.phasio_id = phasio_id
		self.type = type
