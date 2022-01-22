class Binop:
    def __init__(self, o1, o2, op) -> None:
        self.o1 = o1.strip()

        if "(" in self.o1 and ")" in self.o1:
            num = int(self.o1.replace("(", "").replace(")", ""))
            self.o1 = f"[ebp + {8 + num*4}]"

        self.o2 = o2.strip()

        if "(" in self.o2 and ")" in self.o2:
            num = int(self.o2.replace("(", "").replace(")", ""))
            self.o2 = f"[ebp + {8 + num*4}]"


        self.op = op

    def asm(self):
        instructions = {
            "=": "mov",
            "+=": "add",
            "-=": "sub",
            "*=": "imul",
            "\=": "div",
            "%=": "mod",
            "jump": "jump",
            "??": "cmp",
            "cmp": "cmp",
            "test": "test",
            "?": "test"
        }

        jumps = {
            "if equals": "je",
            "if zero": "jz",
            "if not equals": "jne",
            "if not zero": "jnz",
            "if less": "jl",
            "if greater": "jg"
        }

        required = {
            "div": ("xor edx, edx\n", "")
        }

        instr = instructions.get(self.op)
        start = ""
        end = ""
        if instr in required:
            reqs = required.get(instr)
            start = reqs[0]
            end = reqs[1]

        if self.op == "jump":
            return f"{jumps.get(self.o1)} {self.o2}\n"

        return f"{start}{instructions.get(self.op)} {self.o1}, {self.o2}\n{end}"