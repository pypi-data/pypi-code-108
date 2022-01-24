import cv2 
import matplotlib.pyplot as plt 


class Detect:
	def __init__(self,image):
		self.cc = None 
		self.img  = cv2.imread(image)
		self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
		self.rgb = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)

	def start(self,minSize=(20,20),border_width=5):
		model = cv2.CascadeClassifier(self.cc)
		found  =  model.detectMultiScale(self.gray,minSize=(20,20))

		if len(found)!= 0:
			for (x,y,height,width) in found:
				cv2.rectangle(self.rgb,(x,y),(x+height,y+width),(0,255,0),border_width)

	def show(self,img):
		plt.imshow(img)
		plt.show()

	def setCascade(self,my_cascade=None,cascade=None):
		if cascade is  None:
			cc = my_cascade
		else:
			cc = cv2.data.haarcascades + cascade

		self.cc = cc 

	def help(self):
		help(Detect)

		print(''' 
			from detect import Detect 


            model = Detect(image="C:/logs/image.jpg")
            model.setCascade(my_cascade="C://logs/stop_data.xml")
            model.start(border_width=5)
            model.show(model.rgb)

		''')



	

