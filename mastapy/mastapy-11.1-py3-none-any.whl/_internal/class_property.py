'''class_property.py

Decorator for class properties.
'''


class classproperty(property):
    '''classproperty

    An extension of the property decorator for handling class properties.
    '''

    def __get__(self, cls, owner):
        if self.fget is None:
            raise AttributeError('Unreadable attribute')

        return classmethod(self.fget).__get__(None, owner)()

    def __set__(self, cls, value):
        if self.fset is None:
            raise AttributeError('Unreadable attribute')

        classmethod(self.fset).__set__(None, value)()
