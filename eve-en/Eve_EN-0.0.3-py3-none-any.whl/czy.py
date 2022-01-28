def czy(string, slowa):
	return [element for element in slowa if element in string.lower()]

def cls():
    import os
    os.system("cls")
