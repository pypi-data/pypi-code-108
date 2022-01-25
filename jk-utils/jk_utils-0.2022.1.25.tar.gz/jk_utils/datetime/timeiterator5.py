

from .T5 import T5







def timeRange5(fromHour:T5, toHour:T5, includeRightBorder:bool = False, steps:int = 1):
	i = fromHour.clone()
	n = 0
	while i < toHour:
		if n % steps == 0:
			yield i.clone()
		i._absoluteTick += 1
		i._hour = i._absoluteTick // 12
		i._minuteTick = i._absoluteTick % 12
		i._minute = i._minuteTick * 5
		n += 1
	if i == toHour:
		if includeRightBorder:
			yield i.clone()
#





