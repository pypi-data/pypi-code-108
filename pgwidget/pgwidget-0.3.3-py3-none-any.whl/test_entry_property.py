# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 17:39:43 2021

@author: EUROCOM
"""



class Test:
    def __init__(self,pos,text):
        
        
       
        

        self.pos=pos
        
        self._text=text
        
        self.label=[text]
        
        
        
    @property
    def x(self):
        return(self._x)
    
    @property
    def y(self):
        return(self._y)
    
    @x.setter
    def x(self,x):
        self._x=x
        self.pos[0]=x
        
    @y.setter
    def y(self,y):
        self._y=y
        self.pos[1]=y
        
    
    
        
    @property
    def text(self):
        return(self._text)
    
    @text.setter
    def text(self,text):
        self._text=text
        self.label[0]=text
        
        
        
        


test1=Test([100,200],"INIT")

test1.text="BLABLA"


print(test1.text,test1.label)
        
print(test1.pos)


test1.x=341

print(test1.pos)


test1.pos=[300,300]

print(test1.x)
