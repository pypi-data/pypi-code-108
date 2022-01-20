from rich import print

data = """
# heading 1
test

## subtitle 
hello 

# heading 2
test 2
"""

citation_part = "#heading-2".replace("#", "# ").replace("-", " ")
section = []
heading = 0
sub_section = []

data = data.split("\n")

for i in data:
    if citation_part in i and i.startswith("#"):
        heading = i.count("#")
        sub_section.append([i])
    else:
        if heading != 0:
            if i.count("#") == 0 or heading < i.count("#"):
                section.append(i)
            else:
                sub_section.append(section)
                section = []

sub_section = [x for y in sub_section for x in y]
sub_section = "\n".join(sub_section)
print(sub_section)
