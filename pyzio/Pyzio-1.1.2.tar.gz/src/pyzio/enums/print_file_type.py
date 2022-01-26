from enum import Enum


class PrintFileType(str, Enum):
	GCODE = 'GCODE'
	OPENJZ = 'OPENJZ'
