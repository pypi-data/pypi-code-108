from tkinter import *

class window:
	def up(e):
		display.move(spr,0,-20)
	def down(e):
		display.move(spr,0,20)
	def left(e):
		display.move(spr,-20,0)
	def right(e):
		display.move(spr,20,0)
	def __init__(self,title,hw):
		self.title = title
		self.root = Tk()
		self.root.title(self.title)
		self.root.geometry(hw.replace(':','x'))
		self.root.bind('<Up>',window.up)
		self.root.bind('<Down>',window.down)
		self.root.bind('<Left>',window.left)
		self.root.bind('<Right>',window.right)
	def tweak(self,title,hw):
		self.title = title
		self.root.title(self.title)
		self.root.geometry(hw.replace(':','x'))
	def run(self):
		self.root.mainloop()
class screen:
	def __init__(self,hw,bg):
		self.height = hw.split(':')[0]
		self.width = hw.split(':')[1]
		self.bg = bg
		global display
		display = Canvas(height=self.height,width=self.width,bg=self.bg)
		display.pack()
	def tweak(self,hw):
		self.height = hw.split(':')[0]
		self.width =  hw.split(':')[1]
class obj:
    def skin(self,img):
        self.img = PhotoImage(file=img)
    def add(self,hw):
    	global spr
    	spr = display.create_image(hw.split(':')[0],hw.split(':')[1],image=self.img)
