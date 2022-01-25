import os

# https://gist.github.com/kmanalo/8103281
# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python/9728478#9728478

def list_files(startpath, filename):
    outfile = open(filename, 'w')

    exclude_folders = ['__pycache__', 'ipynb_checkpoints']
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        if any(fld in os.path.basename(root) for fld in exclude_folders):
            # if '__pycache__' in os.path.basename(root) or 'ipynb_checkpoints' in os.path.basename(root):
            continue
        else:
            outfile.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if '.py' in f and '.pyc' not in f and '__init__' not in f:
                    outfile.write(f'{subindent}{f}\n')

    outfile.close()

list_files(r'..\streng', r'source\pyfileslist.txt')
