from tkinter import *
from tkinter.filedialog import askdirectory
import os
import shutil

class Commands():

	def __init__(self):
		self.dir_name = "."

	def get_path(self):
		self.dir_name = askdirectory()

	def create(self , packname, path):
		if not path :
			self.get_path()
		packname , run_name = packname.split(':')
		os.makedirs(f"{self.dir_name}/{packname}/{packname}")
		files=os.listdir(f"{os.path.dirname(__file__)}/dep")
		for fname in files:
			shutil.copy2(os.path.join(f"{os.path.dirname(__file__)}/dep",fname),f"{self.dir_name}/{packname}/" )
		with open(f"{self.dir_name}/{packname}/{packname}/__init__.py" ,"w+") as f :
				f.write(" ")				
		with open(f"{self.dir_name}/{packname}/{packname}/{run_name}.py" ,"w+") as f :
				f.write("#GETTING STARTED")				