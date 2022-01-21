import os
from sys import path, version
from types import new_class
from .tree import load_json, dump_json


def simple_list_md_load(p):
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        result = []
        for line in lines:
            item = line.strip('\n')
            result.append(item)
        return result


def simple_list_md_dump(p, lines):
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


class ImgWalker():

    def __init__(self, root) -> None:
        self.root = root

    def walk(self):
        for base, dirs, files in os.walk(self.root):
            for file in files:
                if file[-3:] == '.md':
                    md_file = os.path.join(base, file)
                    md_lines = simple_list_md_load(md_file)
                    md_new = []
                    for line in md_lines:
                        new_line = line.replace(
                            '![](./', f'![](https://gitcode.net/csdn/skill_tree_opencv/-/raw/master/{base}/')
                        md_new.append(new_line)
                    md_new.append('')
                    simple_list_md_dump(md_file, md_new)
                    # import sys
                    # sys.exit(0)
