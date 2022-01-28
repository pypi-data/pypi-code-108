import gdown
from keras.models import model_from_json
import json
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

#model.h5
url1 = 'https://drive.google.com/uc?id=129jCE5-dWVOHIVgcw4L_g1NhGAsyCu8-'
output1 = 'model.h5'
gdown.download(url1, output1, quiet=False)
print("\nWeights retrieved")

#model.json
url2 = 'https://drive.google.com/uc?id=1KAUpIPXI1W5TlZmed1LJwyZNgG1ggStR'
output2 = 'model.json'
gdown.download(url2, output2, quiet=False)
print("\nFile (json) retrieved")

from keras.models import model_from_json
try:
  json_file = open('model.json', 'r')
except:
  json_file = open('/content/model.json', 'r')

loaded_model_json = json_file.read()
json_file.close()
loaded_jarvis = model_from_json(loaded_model_json)
loaded_jarvis.load_weights("model.h5")


def real_time_prediction(image_path):
  image_org = cv2.imread(image_path)

  image_grey = cv2.cvtColor(image_org.copy(), cv2.COLOR_BGR2GRAY)

  ret, thresh = cv2.threshold(image_grey.copy(), 247, 255, cv2.THRESH_BINARY_INV)

  contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  dimensions = image_org.shape
  image_new = np.zeros([dimensions[0],dimensions[1],3])
  image_new.fill(255)
  l=[]
  for c in contours:
    if(cv2.contourArea(c)<200):
      continue
    x,y,w,h = cv2.boundingRect(c)
    font_scale=float((h-3)/30)
    l.append(font_scale)  
  for c in contours:
    if(cv2.contourArea(c) < 200):
      continue
    x,y,w,h = cv2.boundingRect(c)
    font_scale=(min(l)+max(l))/2
    cv2.rectangle(thresh, (x,y), (x+w,y+h), color=(255,0,0), thickness=2)
    digit = thresh[y:y+h, x:x+w]
    resized_digit = cv2.resize(digit, (18,18))
    padded_digit = np.pad(resized_digit, (5,5), "constant", constant_values=0)
    changed = np.array(padded_digit)
    prediction = loaded_jarvis.predict(padded_digit.reshape(1,28,28,1))
    cv2.putText(image_new,str(np.argmax(prediction)),(int(x-w*0.1),int(y+h*0.95)),cv2.FONT_HERSHEY_COMPLEX,font_scale,(0,-100,0),2)  
  print("\n--> UPLOADED IMAGE IN HAND WRITTEN FORMAT")
  plt.imshow(image_org)
  plt.show()
  print("\n\n--> PREDICTED IMAGE IN DIGITAL FORMAT")
  plt.imshow(image_new)
  plt.show()
flag=1
while(flag==1):
  real_time_prediction(input("Give image_path : "))

  print("To continue press 1")
  print("To exit press 0")
  flag=int(input())