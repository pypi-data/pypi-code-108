from .url import RestURL

''' 
        The guys at Keycloak don't use standard intuitive Rest path for all the resources:

        for example to create a car you can do:
            Post /car, 

        But to delete it you have to do:
            Delete /house/1,  # this delete de car above  

        Thats why we need this class.  
    '''
class Targets: 
    targets = {}

    @staticmethod
    def makeWithURL(url = None): 
        url = RestURL(url)
        t = Targets()

        t.targets = {
                    "create": url.copy(),
                    "update": url.copy(),
                    "delete": url.copy(),
                    "read":   url.copy(),
        }

        return t

    @staticmethod
    def makeWithArrayOfURLs(urls = {}): 
        t = Targets()
        t.targets = urls
        return t
    
    def getDeleteMethod(self): 
        return self.targets['delete']

    def getReadMethod(self): 
        return self.targets['read']

    def getCreateMethod(self): 
        return self.targets['create']

    def getUpdateMethod(self): 
        return self.targets['update']

    def change(self, resourceName): 
        for method in self.targets: 
            self.targets[method].replaceCurrentResourceTarget(resourceName)

    def removeResources(self, resources):
        for method in self.targets: 
            self.targets[method].removeResources(resources)

        return self

    def removeLast(self):
        for method in self.targets: 
            self.targets[method].removeLast()

        return self

    def addResourcesFor(self, name, resources):
        self.targets[name].addResources(resources)
        return self

    def addResources(self, resources): 
        for method in self.targets: 
            self.targets[method].addResources(resources)
        return self

    def copy(self):
        urls = {}
        for key in self.targets: 
            urls[key] = self.targets[key].copy()
        return Targets.makeWithArrayOfURLs(urls) 

    def methods(self):
        return self.targets.keys()

    def url(self, methodName): 
        if methodName not in self.targets:
            raise Exception('Method: '+ methodName +' not supported')

        return self.targets[methodName].copy()


