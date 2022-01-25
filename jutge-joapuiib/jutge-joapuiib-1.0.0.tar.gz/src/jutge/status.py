from colorama import Fore

class Stat:
    def __init__(self, name, color, priority=0):
        self.name = name
        self.color = color
        self.priority = priority

    def __str__(self):
        return f"{self.color}{self.name}{Fore.RESET}"


    def merge(self, other):
        return other if other.priority < self.priority else self

    def __eq__(self, other):
        if not isinstance(other, Stat):
            return False
        else:
            return self.name == other.name

    def __ne__(self, other):
       return not self.__eq__(other)

class Status:
    PERFECT = Stat("PERFECT", Fore.GREEN, 5)
    PRESENTATION = Stat("PRESENTATION", Fore.CYAN, 4)
    PASSED = Stat("PASSED", Fore.YELLOW, 3)
    EMPTY = Stat("EMPTY", Fore.YELLOW, 2)
    FAILED = Stat("FAILED", Fore.RED, 1)
    TIMEOUT = Stat("TIMEOUT", Fore.RED, -1)
    RUNTIME = Stat("RUNTIME", Fore.RED, -1)
