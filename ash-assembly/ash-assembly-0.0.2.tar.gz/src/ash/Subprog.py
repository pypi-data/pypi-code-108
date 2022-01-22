from Translator import Translator


class Subprog:
    def __init__(self, name, keeplist, ashcode) -> None:
        self.name = name
        self.keeplist = keeplist
        self.ashcode = ashcode
        self.code = Translator.translate(self.ashcode)

        if len(self.keeplist) == 1 and self.keeplist[0] == "":
            self.keeplist = []
    
    def asm(self):
        start = "push ebp\nmov ebp, esp\n"
        for reg in self.keeplist:
            start += f"push {reg.strip()}\n"
        
        end = "pop ebp\nret\n\n"
        for reg in self.keeplist:
            end = f"pop {reg.strip()}\n" + end 
        return f"{self.name}:\n{start}\n{self.code}\n{end}"

    