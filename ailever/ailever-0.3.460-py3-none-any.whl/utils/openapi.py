import os
from urllib.request import urlretrieve

def source(name):
    urlretrieve('https://raw.githubusercontent.com/ailever/openapi/master/source/'+name+'.py', f'./{name}.py')
    print(f'[AILEVER] The file "{name}.py" is downloaded!')

def storage(name):
    urlretrieve('https://github.com/ailever/openapi/raw/master/storage/'+name, f'./{name}')
    print(f'[AILEVER] The file "{name} is downloaded!')
