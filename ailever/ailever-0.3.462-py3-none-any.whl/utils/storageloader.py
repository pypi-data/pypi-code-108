from urllib.request import urlretrieve

def storage(name):
    urlretrieve('https://raw.githubusercontent.com/ailever/ailever/master/storage/'+name, f'./{name}')
    print(f'[AILEVER] The file "{name}" is downloaded!')

