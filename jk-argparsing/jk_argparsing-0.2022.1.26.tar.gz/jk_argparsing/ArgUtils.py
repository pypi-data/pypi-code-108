


import re



class ArgUtils(object):

	@staticmethod
	def wrapWords(text, width) -> list:
		assert isinstance(text, str)
		assert isinstance(width, int)

		data = []

		tokens = re.split(r"[ \t\r\n]+", text)
		for n in range(len(tokens) - 1, 0, -1):
			if len(tokens[n].strip()) == 0:
				del tokens[n]

		sb = ""
		for i in range(0, len(tokens)):
			sb += tokens[i]
			if (len(sb) == width) or ((i < len(tokens) - 1) and (len(sb) + len(tokens[i + 1]) + 1 > width)):
				data.append(sb)
				sb = ""
			else:
				sb += ' '
		s = sb.strip()
		if len(s) > 0:
			data.append(s)

		return data
	#

	@staticmethod
	def createEmptyString(length):
		sb = ""
		while len(sb) < length:
			sb += " "
		return sb
	#

	@staticmethod
	def writePrefixedWrappingText(firstLine, text, width, outputList):
		if firstLine is None:
			firstLine = ""

		widthLeft = width - len(firstLine)
		spaces = ArgUtils.createEmptyString(len(firstLine))

		bFirst = True
		for line in ArgUtils.wrapWords(text, widthLeft):
			if bFirst:
				outputList.append(firstLine + line)
				bFirst = False
			else:
				outputList.append(spaces + line)
	#

#




