
import json
import traceback
import requests

RENEWURL = "https://api.secuuth.io/auth/renewTokens"
class renewToken:
     def __init__(self,pubKey,refreshToken,keyId,userSubId):
        self.pubKey=pubKey
        self.refreshToken=refreshToken
        self.keyId=keyId
        self.userSubId=userSubId
    

    
     def renewToken(self):
        print("TOKENS")
        data={
                    "publicKey":self.pubKey,
                    "refreshToken":self.refreshToken,
                    "userSubId":self.userSubId,
                    "renewRefreshToken":False,
            }
        headers={ 
                    "Content-Type": "application/json",
                     "keyId":self.keyId,
                }
         
        try: 
            token=requests.post(RENEWURL,headers=headers,data=json.dumps(data))
            return token.json();
        except Exception:
            return {}

            

        

         
            



        

