from abc import ABC, abstractmethod

from pyridy import Campaign


class PostProcessor(ABC):
    def __init__(self, campaign: Campaign):
        self.campaign = campaign

    @abstractmethod
    def execute(self):
        pass
