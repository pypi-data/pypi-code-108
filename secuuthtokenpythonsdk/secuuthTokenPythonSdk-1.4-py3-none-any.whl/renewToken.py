import json
import requests

RENEWURL = "https://api.secuuth.io/auth/renewTokens"
class renewToken:
     def __init__(self,pubKey,refreshToken,keyId,userSubId):
        self.pubKey=pubKey
        self.refreshToken=refreshToken
        self.keyId=keyId
        self.userSubId=userSubId
    

    
     def renewToken(self):
         
         try: 
            token=requests.post(RENEWURL,
                    data=json.stringify({
                    "publicKey":self.pubKey,
                    "refreshToken":self.refreshToken,
                    "userSubId":self.userSubId,
                    "renewRefreshToken":False,
                    }),headers={ 
                    "Content-Type": "application/json",
                     "keyId":self.keyId
                    })
            return token;
         except:
            return{}

            

        

         
            



        

