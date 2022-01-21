import json

class Information():
    def __init__(self):
        pass
    def load(self):
        pass
    def save(self):
        pass
  

detail = {'user':'',
          'place':'',
          'city': '',
          'country':'',
          'provider':'',
          'email_1':'',
          'email_2':'',
          'first_name':'',
          'last_name':'',
          }
person= {
    'user_0':detail
    }

basic = {
    'language': 'English'
    }

profile = {
    'basic': basic,
    'person': person,
    }


          


    
if __name__ == "__main__":
    print(profile)
    with open('profile.json', 'w') as fp:
        json.dump(profile, fp, sort_keys=True, indent=4)
    
    with open('profile.json', 'r') as infile:
        data = json.load(infile)
    print('from file',data)
              
