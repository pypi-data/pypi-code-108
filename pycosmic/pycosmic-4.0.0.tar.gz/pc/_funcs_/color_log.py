import colorama 


colorama.init(convert=True)



fore = colorama.Fore 
back = colorama.Back


colors = {"red":fore.RED,"black":fore.BLACK,"magenta":fore.MAGENTA,"blue":fore.BLUE,
"green":fore.GREEN,"yellow":fore.YELLOW,'cyan':fore.CYAN,'white':fore.WHITE}


class _print_:
	def __init__(self,value,color):
		self.value = value
		self.log(self.value,color)

	def log(self,value=None,color='red'):
		if value is not None and color in colors.keys():
			print(colors[color] + value )


		



