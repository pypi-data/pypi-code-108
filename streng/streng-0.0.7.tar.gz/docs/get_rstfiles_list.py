import os

def list_files(startpath, filename):
    outfile = open(filename, 'w') 
    exclude_folders = ['__pycache__', 'ipynb_checkpoints', '_build', '_static', '.vscode']
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        if any(fld in os.path.basename(root) for fld in exclude_folders):
            continue
        else:
            outfile.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if '.rst' in f:
                    outfile.write(f'{subindent}{f}\n')

    outfile.close()

list_files(r'D:\mypythons\StrEng\docs\source', r'source\rstfileslist.txt')