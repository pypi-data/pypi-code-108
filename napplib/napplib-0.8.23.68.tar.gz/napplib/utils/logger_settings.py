# build-in imports
from sys 			import stderr
from dataclasses 	import dataclass

# external imports
from loguru 		import logger


@dataclass
class LoggerSettings:
	level	: str	= 'INFO'

	def __post_init__(self):
		logger.remove()
		logger.add(stderr, level=self.level)
