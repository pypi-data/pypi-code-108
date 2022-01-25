# product
# - deployment_config_object/class - all the information needed for solution
    # this is alot....

from abc import ABCMeta, abstractstaticmethod

class Deployment:
    def __init__(self, value_default=0) -> None:
        self.some_value = value_default

    def __str__(self):
        return f'this is a deployment with value: {self.some_value}'

class IBuilder(metaclass=ABCMeta):
    @abstractstaticmethod
    def set_some_value(self, value):
        """do some work"""
    def get_result(self):
        """return product"""

class CortexBuilder(IBuilder):
    def __init__(self, value):
        self.deployment = Deployment()

    def set_some_value(self, value):
        self.deployment.some_value = value

    def get_result(self):
        return self.deployment

# concrete directors for each supported solution
class CortexDirector:
    """the director, building a different representation"""
    @staticmethod
    def construct():
        return CortexBuilder()\
            .set_some_value(5)\
            .get_result()

