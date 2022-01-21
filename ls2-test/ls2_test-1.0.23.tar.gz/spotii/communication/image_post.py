import json
import os
import requests
import threading
import time
import sys
sys.path.append('/home/pi/gxf/python/spotii')
from define import *

class PostImg(threading.Thread):
    def __init__(self, *args):             # self, imageFile, image-identifier, queue
        threading.Thread.__init__(self)
        self.imageFile = args[0]
        self.identifier= args[1]
        self.notifyQue = args[2]

#qForGui format: [device_index, retCode, QRcode, message]        
    def run(self):
        try:
            upload_url = "https://lookspot.peter-johnson.com.au/API/ImageAnalysis"
            headers = {'Authorization' : 'Basic TGFpcGFjOjc0NFFIS0J0SjZjRnhkbndDQ01y',
                            'Image-Identifier' : self.identifier,
                            'Content-Type' : 'image/png'}

            
            with open(self.imageFile,'rb') as f:
                data=f.read()
                
            r = requests.post(upload_url, headers=headers, data=data)
            #print (r.text)
            response=json.loads(r.text)
            
            if response["imageIdentifier"] != None:                            
                deviceIndex=ord(response["imageIdentifier"].split('_')[1]) - ord('0')
                retCode=response["retCode"]
                QRcode=response["imageIdentifier"].split('_')[0]
                message=response["message"]
                self.notifyQue.put([deviceIndex, retCode, QRcode, message])
                    
                os.remove(self.imageFile)
        except Exception as e:
            print("PostImgException: ",e)
    
def post(imageFile, notifyQue):
    if(type(imageFile)==str):
        identifier=imageFile.split('.')[0]
        identifier="_".join(identifier.split("_", 2)[:2])
        print(identifier)
        postImage=PostImg(IMG_PATH+imageFile, identifier, notifyQue)
        postImage.start()
