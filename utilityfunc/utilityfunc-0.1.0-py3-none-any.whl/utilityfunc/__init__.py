__version__ = '0.1.0'
class utilityfunc():
	def hackerspeak(hackertext):
		"""
		Converts regular text into hackerspeak- example below.
		utilityfunc.hacker('the quick brown fox jumped over the lazy dog')
		Prints "TH3_QU1CK_BR0WN_F0X_JUMP3D_0V3R_TH3_L4ZY_D0G"
		"""
		hackertext= hackertext.upper()
		hackertext= hackertext.replace('A','4')
		hackertext= hackertext.replace('I','1')
		hackertext= hackertext.replace('E','3')
		hackertext= hackertext.replace(' ','_')
		hackertext = hackertext.replace('O','0')
		print(hackertext)

########################################

	def textstyle(text,color):
		"""
		Prints text in a specific color- example below
		utilityfunc.textstyle('hello!','red')
		Prints "hello!" but in red
		Other colors are-
		"black"
		"red"
		"green"
		"yellow"
		"blue"			
		"purple"
		"turquoise"
		"white"
		"gray"
		"peach"
		"lime"
		"gold"
		"skyblue" 
		"magenta" 
		"cyan"
		"""
		
		colordict= {
			"black": "\033[0;30m",
			"red": "\033[0;31m",
			"green": "\033[0;32m",
			"yellow": "\033[0;33m",
			"blue": "\033[0;34m",
			"purple": "\033[0;35m",
			"turquoise": "\033[0;36m",
			"white": "\033[0;37m",
			"gray": "\033[0;90m",
			"peach": "\033[0;91m",
			"lime": "\033[0;92m",
			"gold": "\033[0;93m",
			"skyblue": "\033[0;94m",
			"magenta": "\033[0;95m",
			"cyan": "\033[0;96m"
		}
		if color not in colordict:
			raise NameError('Color "'+color+'" not found')
		colorinuse = colordict[color]
		print(colorinuse+text)

########################################
	def newlines(lines):
		"""
		Creates 'lines' amount of black lines
		Good for formatting and increasing readability
		Example:
		utilityfunc.newlines(4)
		This prints 4 blank lines
		"""
		for i in range(lines):
			print()

#######################################
	def filewrite(fname,ftext,newline=True):
		"""
		
		Appends text to a .txt file, creates file if it does not exist. Example:
		utilityfunc.filewrite('mytxtfile.txt','This is the text I am adding to a file',True)
		This would append 'This is the text I am adding to a file' to the file.
		You can set the last argument (True) to false if you do not want to create a new line. Defaults to True
		"""
		import os
		exists = os.path.exists(fname)
		if exists == False:
			file = open(fname,'w')
		else:
			file = open(fname, 'a')
		if newline and exists:
			file.write('\n')
		file.write(ftext)
		file.close()
	
######################################
	def fileread(fname):
		"""
		Prints .txt file text line-by-line
		Example:
		utilityfunc.fileread('mytxtfile.txt')
		Returns contents of file
		"""
		import os
		if os.path.exists(fname) == False:
			raise FileNotFoundError('File "'+fname+'" does not exist')
		else:
			file = open(fname,'r')
		for line in file:
			print(line,end="")
		file.close()