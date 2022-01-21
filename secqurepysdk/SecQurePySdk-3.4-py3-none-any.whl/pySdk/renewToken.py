from email import header
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
        print(self.pubKey)
        print(self.keyId)
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
            token=requests.post("http://loclhost:5000/auth/renewTokens",headers=headers,json=data)
            
            print(token)
            print(token.status_code)
            print(token.json())
            return token;
        except :
             print("exception")
             return{}

            

        

         
            



        

