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
         
         try: 
            token=requests.post(RENEWURL,
                    data=json.loads({
                    "publicKey":self.pubKey,
                    "refreshToken":self.refreshToken,
                    "userSubId":self.userSubId,
                    "renewRefreshToken":False,
                    }),headers=json.loads({ 
                    "Content-Type": "application/json",
                     "keyId":self.keyId
                    }))
            return token;
         except:
            return{}

            

        

         
            



        

