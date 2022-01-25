

import sys
import math




_PROGRESS_PARAMS_BYTES = [
	(1, "{:.2f}B"),
	(1, "{:.1f}B"),
	(1, "{:.0f}B"),
	(1000, "{:.2f}K"),
	(1000, "{:.1f}K"),
	(1000, "{:.0f}K"),
	(1000*1000, "{:.2f}M"),
	(1000*1000, "{:.1f}M"),
	(1000*1000, "{:.0f}M"),
	(1000*1000*1000, "{:.2f}G"),
	(1000*1000*1000, "{:.1f}G"),
	(1000*1000*1000, "{:.0f}G"),
]



def formatTime(seconds:float, withMilliseconds:bool = False):
	timeSeconds = int(seconds) % 60
	timeMinutes = int(seconds / 60)
	timeHours = int(timeMinutes / 60)
	timeMinutes = timeMinutes % 60
	if withMilliseconds:
		timeMillis = math.floor((seconds - int(seconds))*1000)
		return "{:02d}:{:02d}:{:02d}.{:03d}".format(timeHours, timeMinutes, timeSeconds, timeMillis)
	else:
		return "{:02d}:{:02d}:{:02d}".format(timeHours, timeMinutes, timeSeconds)
#



def formatBytes(nBytes:float):
	index = len(str(int(nBytes))) - 1
	if index >= len(_PROGRESS_PARAMS_BYTES):
		divider, formatStr = _PROGRESS_PARAMS_BYTES[-1]
	else:
		divider, formatStr = _PROGRESS_PARAMS_BYTES[index]
	return formatStr.format(nBytes / divider)
#



def formatBytesPerSecond(nBytesPerSecond:float):
	index = len(str(int(nBytesPerSecond))) - 1
	if index >= len(_PROGRESS_PARAMS_BYTES):
		divider, formatStr = _PROGRESS_PARAMS_BYTES[-1]
	else:
		divider, formatStr = _PROGRESS_PARAMS_BYTES[index]
	formatStr += "/s"
	return formatStr.format(nBytesPerSecond / divider)
#



#
# Displays or updates a console progress bar
#
# This is a (heavily) modified version of:
# https://stackoverflow.com/questions/3160699/python-progress-bar
#
# @param		float dTime					The amount of seconds already passed.
# @param		int currentCapacity			The amount of data already read/written.
# @param		int maxCapacity				The maximum number of data to read or write.
#
def showCapacityProgress(dTime:float, currentCapacity:int, maxCapacity:int):
	assert isinstance(dTime, float)
	assert isinstance(currentCapacity, int)
	assert isinstance(maxCapacity, int)
	assert maxCapacity > 0

	currentProgress = currentCapacity / maxCapacity
	if (dTime >= 1) and (currentCapacity > 0):
		totalTimeSeconds = dTime/currentProgress
		sTotalTime = formatTime(totalTimeSeconds)
		sUsedTime = formatTime(dTime)
		sDataRate = formatBytesPerSecond(currentCapacity / maxCapacity)
	else:
		sUsedTime = "??:??:??"
		sTotalTime = "??:??:??"
		sDataRate = "????"

	barLength = 40 # Modify this to change the length of the progress bar
	status = ""
	"""
	if currentProgress < 0:
		currentProgress = 0
		status = "Halt...\r\n"
	"""
	if currentProgress >= 1:
		currentProgress = 1
		status = "Done...\r\n"
	block = int(round(barLength*currentProgress))
	text = "\rProgress: [{0}] {1:.1f}% {2}   {3} ETA {4} @ {5}        ".format( "#"*block + "-"*(barLength-block), currentProgress*100, status, sUsedTime, sTotalTime, sDataRate)
	sys.stdout.write(text)
	sys.stdout.flush()
#




























