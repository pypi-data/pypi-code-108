




class CmdLineParser(object):

	@staticmethod
	def parseCmdLine(text):

		IN_SPACE = 1
		IN_SPACE_EXPECTS_SPACE = 2
		IN_WORD = 3
		IN_WORD_NEXT_MASKED = 4
		IN_STR = 5
		IN_STR_NEXT_MASKED = 6

		ret = []
		mode = IN_SPACE
		buffer = []
		charNo = 0

		for c in text:
			charNo += 1

			if mode == IN_SPACE:
				if (c == " ") or (c == "\t"):
					continue
				elif c == "\"":
					mode = IN_STR
				else:
					buffer.append(c)
					mode = IN_WORD
			elif mode == IN_SPACE_EXPECTS_SPACE:
				if (c == " ") or (c == "\t"):
					mode = IN_SPACE
				else:
					raise Exception("Space character expected at position " + str(charNo) + ": " + c + " (" + str(ord(c)) + ")")
			elif mode == IN_WORD:
				if (c == " ") or (c == "\t"):
					ret.append("".join(buffer))
					buffer.clear()
					mode = IN_SPACE
				elif c == "\\":
					mode = IN_WORD_NEXT_MASKED
				elif c == "\"":
					raise Exception("Unexpected character at position " + str(charNo) + ": " + c + " (" + str(ord(c)) + ")")
				else:
					buffer.append(c)
			elif mode == IN_WORD_NEXT_MASKED:
				buffer.append(c)
				mode = IN_WORD
			elif mode == IN_STR:
				if c == "\"":
					ret.append("".join(buffer))
					buffer.clear()
					mode = IN_SPACE_EXPECTS_SPACE
				elif c == "\\":
					mode = IN_STR_NEXT_MASKED
				else:
					buffer.append(c)
			elif mode == IN_STR_NEXT_MASKED:
				buffer.append(c)
				mode = IN_STR
			else:
				raise Exception()

		if mode == IN_WORD:
			ret.append("".join(buffer))
		elif mode == IN_STR:
			raise Exception("Unterminated string at position " + str(charNo) + ": " + c + " (" + str(ord(c)) + ")")
		elif mode == IN_STR_NEXT_MASKED:
			raise Exception("Unterminated string at position " + str(charNo) + ": " + c + " (" + str(ord(c)) + ")")

		return ret
	#


#






