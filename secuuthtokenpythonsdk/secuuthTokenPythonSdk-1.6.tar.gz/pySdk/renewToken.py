import json
import requests

RENEWURL = "http://loclhost:5000/auth/renewTokens"
class renewToken:
     def __init__(self,pubKey,refreshToken,keyId,userSubId):
        self.pubKey=pubKey
        self.refreshToken=refreshToken
        self.keyId=keyId
        self.userSubId=userSubId
    

    
     def renewToken(self):
         print("TOKENS")
         
         try: 
            token=requests.post(RENEWURL,
                    data={
                    "publicKey":self.pubKey,
                    "refreshToken":self.refreshToken,
                    "userSubId":self.userSubId,
                    "renewRefreshToken":False,
                    },headers={ 
                    "Content-Type": "application/json",
                     "keyId":self.keyId
                    })
            
            print(token)
            return token;
         except :
             print("exception")
             return{}

            

        

         
            



        

