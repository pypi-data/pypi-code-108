class Unop:
    def __init__(self, o, op) -> None:
        self.o = o.strip()

        if "[" in self.o and "]" in self.o:
            num = int(self.o.replace("[", "").replace("]", ""))
            self.o = f"[ebp + {8 + num*4}]"

        self.op = op

    def asm(self):
        instructions = {
            "push": "push",
            "pop": "pop",
            "*": "mul",
            "/": "div",
            "!": "not",
            "printstr": "PRINT_STRING",
            "printnum": "PRINT_DEC 4,",
            "call": "call",
            "jump": "jump",
            "++": "inc",
            "--": "dec"
        }

        required = {
            "mul": ("xor edx, edx\n", ""),
            "div": ("xor edx, edx\n", "")
        }

        instr = instructions.get(self.op)
        start = ""
        end = ""
        if instr in required:
            reqs = required.get(instr)
            start = reqs[0]
            end = reqs[1]
       
        return f"{start}{instructions.get(self.op)} {self.o}\n{end}"