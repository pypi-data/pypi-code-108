def checkstr(ost):
		if type(ost) == str:
			return True
		else: return False

def rev(ost):
	if checkstr(ost):
		revved = ost[::-1]
		return revved
	else: raise SyntaxError


def ascii_convert(ost):
	if checkstr(ost):
		rst = ""
		for char in ost:
			rst += ("-"+str(ord(char)))
		return rst.lstrip("-")
	else: raise SyntaxError

def caesarcipher(ost, key=1):
	if checkstr(ost):
		if type(key) == int:
			rst = ""
			for char in ost:
				rst += chr(ord(char) + key)
			return rst
		else: raise TypeError
	else: raise SyntaxError

def weirdcase(ost):
    if checkstr(ost):
        rst = ""
        l = list(ost.casefold())
        for i in range(len(l)):
            if i % 2 == 0:
                 rst += l[i].upper()
            else:
                rst += l[i].lower()
        return rst

def encode(ost, key=1):
	if checkstr(ost):
		if type(key) == int:
			rst = rev(ascii_convert(weirdcase(caesarcipher(ost, key))))
			return rst
		else: raise TypeError
	else: raise SyntaxError

def checkpalindrome(ost):
	if checkstr(ost):
		if list(ost) == list(rev(ost)):
			return True
		else: return False
