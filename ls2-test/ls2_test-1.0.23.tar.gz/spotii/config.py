import time
import json
from operator import itemgetter
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import main_paras
from define import *

if sys.platform == 'linux':
    PROFILE_FOLDER = '/home/pi/app/spotii'
else:
    PROFILE_FOLDER = currentdir



##profile = {
##    'user': 'feng.gao@laipac.com',
##    'place': 'office',
##    'city': 'Markham',
##    'country': 'Canada',
##    'provider':	'Laipac'    
##    }



basic = {
    'language': DEFAULT_LANGUAGE,
    'time_zone':'',
    'test_mode': DEFAULT_TEST_MODE
    }


class Config():
    def __init__(self):
        print('working folder', PROFILE_FOLDER)
        self.languageList = os.listdir(os.path.join(currentdir, main_paras.defaultLanguageFolder))        
        self.profile_list = {
            'basic': basic,
            'person': [],
            }

        if time.daylight:
            offsetHour = time.altzone / 3600
        else:
            offsetHour = time.timezone / 3600
        self.profile_list['basic']['time_zone'] = 'Etc/GMT%+d' % offsetHour        

        try:
            with open(os.path.join(PROFILE_FOLDER,'profile.json'), 'r') as infile:
                
                self.profile_list = json.load(infile)
                if 'test_mode' not in self.profile_list['basic'].keys():
                    print('test_mode is missed')
                    self.profile_list['basic']['test_mode'] = DEFAULT_TEST_MODE
                if self.profile_list['basic']['language'] not in self.languageList:
                    self.profile_list['basic']['language'] = DEFAULT_LANGUAGE
        except Exception as e:            
            print('profile load exception:',e)

        print ('init Before: ', time.strftime('%X %x %Z'))
        os.environ['TZ'] = self.profile_list['basic']['time_zone']
        if sys.platform == 'linux':
            time.tzset()
        print ('init After: ', time.strftime('%X %x %Z'))
            
        
    def save(self):
        with open(os.path.join(PROFILE_FOLDER,'profile.json'), 'w+') as fp:
            json.dump(self.profile_list, fp, sort_keys=True, indent=4)
    def setCurrentLanguage(self,index):
        self.profile_list['basic']['language']=self.languageList[index]
        self.save()

    def getLanguageList(self):
        return self.languageList

    def getCurrentLanguage(self):
        return self.profile_list['basic']['language']

    def setDefaultTimeZone(self):
        if time.daylight:
            offsetHour = time.altzone / 3600
        else:
            offsetHour = time.timezone / 3600
        self.profile_list['basic']['time_zone'] = 'Etc/GMT%+d' % offsetHour        
        self.save()
        
    def setTimeZone(self, timeZone):
        self.profile_list['basic']['time_zone']=timeZone
        print ('Before: ', time.strftime('%X %x %Z'))
        os.environ['TZ'] = timeZone
        if sys.platform == 'linux':
            time.tzset()
        print ('After: ', time.strftime('%X %x %Z'))
        self.save()

    def getTimeZone(self):
        return self.profile_list['basic']['time_zone']

    def setTestMode(self, mode):
        self.profile_list['basic']['test_mode'] = mode
        self.save()

    def getTestMode(self):
        return self.profile_list['basic']['test_mode']
        
    def getProfile(self, user):
        profile = main_paras.empty.copy()
        for person in self.profile_list['person']:
            if user == person['user']:
                for key in profile:
                    if key in person.keys():
                        profile[key] = person[key]
                break;
        return profile

    def lastUser(self):
        if len(self.profile_list['person']) == 0:
            return ''
        return self.profile_list['person'][-1]['user']

    def saveUser(self,user):
        for i, person in enumerate(self.profile_list['person']):
            if user == person['user']:
                return;
        profile = main_paras.empty.copy()
        profile['user']=user
        self.profile_list['person'].append(profile)
        self.save()
    
    
    def setProfile(self, profile):
        delete_out = len(self.profile_list['person']) - MAX_PROFILES
        if delete_out>0:
            del self.profile_list['person'][0:delete_out]
        for i, person in enumerate(self.profile_list['person']):
            if profile['user'] == person['user']:
                del self.profile_list['person'][i]
                break;
        else:
            del self.profile_list['person'][0]
            
        self.profile_list['person'].append(profile)
        self.save()

    def clear(self):
        self.profile_list = {
            'basic': basic,
            'person': [],
            }
        self.save()

    def show(self):
        print(self.profile_list)
        
        
   



##    print(profile)
##    with open('profile.json', 'w') as fp:
##        json.dump(profile, fp, sort_keys=True, indent=4)
##    
##    with open('profile.json', 'r') as infile:
##        data = json.load(infile)
##    print('from file',data)
##          


    
if __name__ == "__main__":
    pass              
