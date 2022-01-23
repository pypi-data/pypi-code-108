class 李白error(ValueError):
    """ define an error"""

class poet:
    def __init__(self,name,**poetdict):
        if(name=="李白"):
            if(not 'confirm' in poetdict):
                raise 李白error("包中已经含有李白了")
            self.name=name
            self.__live_from=701
            self.__live_to=762
            self.__born_place="剑南道绵州（巴西郡）昌隆（后避玄宗讳改为昌明）青莲乡"
        else:
            self.name=name
            if "live" in poetdict:
                self.__live_from=poetdict["live"][0]
                self.__live_to=poetdict["live"][1]
            if "born" in poetdict:
                self.__born_place=poetdict["born"]
    def show(self):
        print(f"{self.name}({self.__live_from if self.__live_from else '???'}-{self.__live_to}),出生于{self.__born_place}.")

def 李白():
    b=poet("李白",confirm=True)
    return b
