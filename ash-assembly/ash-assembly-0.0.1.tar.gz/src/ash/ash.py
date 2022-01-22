import sys
import re
import os

from Subprog import Subprog
from Translator import Translator

print("ASH (Assembly Shorthand Syntax)")

location = sys.argv[1]

print(os.getcwd())

f = open(f"{os.getcwd()}/{location}", "r")
lines = f.readlines()
f.close()

code = "".join(lines)

sizes = {
    "byte": "b",
    "word": "w",
    "doubleword": "d",
    "quadword": "q",
    "b": "b",
    "w": "w",
    "d": "d",
    "q": "q",
    "dword": "d",
    "qword": "q"
}

asm = ""

sectiondatafound = re.findall(r"<.data>(.*)</.data>", code, re.DOTALL)

if len(sectiondatafound) == 1:
    print("✅ Data")
    sectiondata = sectiondatafound[0]

    asm += "section .data\n"

    for line in sectiondata.split("\n"):
        stripline = line.strip()
        vals = stripline.split(":")
        if len(vals) == 1 and stripline != "}" and stripline != "":
            asm += line.replace("{", "").strip() + ":\n"
        elif len(vals) == 2:
            asm += f"d{sizes.get(vals[0])} {vals[1]}\n"

    asm += "\n"
else:
    print("❌ Data")

sectionbssfound = re.findall(r"<.bss>(.*)</.bss>", code, re.DOTALL)

if len(sectionbssfound) == 1:
    print("✅ BSS")
    sectionbss = sectionbssfound[0]

    asm += "section .bss\n"

    for line in sectionbss.split("\n"):
        stripline = line.strip()
        vals = stripline.split(" ")
        if len(vals) == 2 and "{" in stripline:
            asm += line.replace("{", "").strip() + ":\n"
        elif len(vals) == 2:
            asm += f"res{sizes.get(vals[1])} {vals[0]}\n"

    asm += "\n"
else:
    print("❌ BSS")


sectiontextfound = re.findall(r"<.text>(.*)</.text>", code, re.DOTALL)

if len(sectiontextfound) == 1:
    print("✅ Text")
    sectiontext = sectiontextfound[0]

    asm += "section .text\n"

    subprogs = re.findall(r"<([a-zA-Z_][a-zA-Z0-9_]*)\s{(.*)?}>(.*)</\1>", sectiontext, re.DOTALL)

    main = re.findall(r"<.main>(.*)</.main>", sectiontext, re.DOTALL)

    for subprog in subprogs:
        s = Subprog(subprog[0], subprog[1].split(","), subprog[2])
        asm += s.asm()

    if len(main) == 1:
        asm += "global CMAIN\nCMAIN:\n"
        asm += "push ebp\nmov ebp, esp\n"
        asm += Translator.translate(main[0])
        asm += "pop ebp\nret\n\n"
else:
    print("❌ Text")

if asm != "":
    filename = location.replace(".ash", ".asm")
    f = open(filename, "w")
    f.write(asm);
    f.close()
    print(f"\n✅ {filename} was created successfully.")
else:
    print(f"\n❌ {location} is blank.")