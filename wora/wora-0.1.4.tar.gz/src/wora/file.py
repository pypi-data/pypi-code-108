import pathlib

def read_file(fname: str) -> str:
    file = open(fname, 'r')
    res = file.read()
    file.close()
    return res

def write_file(fname: str, content: str) -> str:
    file = open(fname, 'w')
    file.write(content)
    file.close()

def mkdir(file):
    if isinstance(file, str):
        pathlib.Path(file).mkdir(parents=True, exist_ok=True)
    elif isinstance(file, pathlib.Path):
        file.mkdir(parents=True, exist_ok=True)
