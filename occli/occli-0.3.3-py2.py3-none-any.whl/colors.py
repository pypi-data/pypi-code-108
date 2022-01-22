import sys

colors = True
platf = sys.platform # Detecting current OS
# If current OS is anything but linux, colors will not be displayed
if platf.lower().startswith(("os", "win", "darwin","ios")): 
    colors = False

if not colors:
	green = red = white = reset = ""

else:                                                 
    white = "\033[97m"
    red = "\033[91m"
    green = "\033[92m"
    reset = "\033[0m"