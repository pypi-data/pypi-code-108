from pythreader import Processor, Flag
import random
from threading import Condition

done = Flag()

class MyProcessor(Processor):
    
    def __init__(self, name, nworkers, output = None):
        self.Name = name
        Processor.__init__(self, nworkers, output = output)
        
    def process(self, lst):
        print(self.Name, lst)
        lst.append(self.Name)
        if random.random() < 0.2:
            done.value = "done"
            print("done")
            return None
        else:
            return lst
        
        

p1 = MyProcessor("A", 2)
p2 = MyProcessor("B", 2, output = p1)
p1.Output = p2

lst = []
p1.add(lst)

done.sleep(lambda x: x == "done")

print("--->", lst)