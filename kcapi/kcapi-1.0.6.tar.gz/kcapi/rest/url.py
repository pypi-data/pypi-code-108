from urllib.parse import urlparse

EMPTY_STRING = ""
DEBUG = False

class RestURL:
    def __get_res_from_url(self, uri):
        res = uri.path.split('/')
        res = filter(lambda re: re != "", res)

        return list(res)

    def __get_target(self): 
        default_scheme = 'https' if not self.uri.scheme else self.uri.scheme
        
        target_url = default_scheme + "://"+self.uri.hostname  

        if self.uri.port:
            target_url = target_url + ":" + str(self.uri.port)

        return target_url

    def __init__(self, url, resources = []):
        if not url:
            raise Exception("Missing URL.")

        if 'http' not in url:  
            raise Exception("No HTTP schema found: <http(s)>://host")

        self.uri = urlparse(url)
        self.url = url
        self.resources = self.__get_res_from_url(self.uri)  
        self.resources = self.resources + resources 
    
    def pushResource(self, fragment):
        if not self.resources:
            self.resources.append(fragment)
            return True
            
        if self.resources[-1] != fragment:
            self.resources.append(fragment)
            return True

        return False

    def setId(self, _id):
        self.addResource(_id)

    def addResources(self, resources):
        for resource in resources: 
            if resource:
                self.pushResource(resource)

        return self

    def addResource(self, name = None, value = None):
        if name:
            self.pushResource(name)
        if value: 
            self.pushResource(value)
        return self

    def removeResources(self, listOfResources): 
        for resource in listOfResources: 
            if resource in self.resources: 
                index = self.resources.index(resource)
                self.resources.pop(index)

    def removeLast(self):
        if len(self.resources) > 0: 
            self.resources.pop()
        return self
        
    def getCurrentResource(self):
        if not self.resources: 
            raise Exception("No URL resources found.")
        return self.resources[-1]

    def replaceResource(self, origin, replacement):
      self.resources = [replacement if entry==origin else entry for entry in self.resources] 

    def replaceCurrentResourceTarget(self, resReplacementName):
        popped = self.resources.pop()
        self.resources.append(resReplacementName)
        return self

    def buildResURL(self): 
        resource_section = ""
        if len(self.resources) == 0:
            return EMPTY_STRING 

        for part in self.resources:
            resource_section = resource_section + "/" + str(part) 

        if DEBUG:
            print("url: ", self.url + resource_section)
        return resource_section

    def __repr__(self):
        return self.__get_target() + self.buildResURL() 

    def copy(self): 
        return RestURL(self.__get_target(), self.resources.copy())

    def target(self): 
        return self.__get_target()
