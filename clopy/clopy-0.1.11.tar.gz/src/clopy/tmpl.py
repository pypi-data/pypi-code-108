from jinja2 import Template
from wora.file import read_file, mkdir
from pathlib import Path
import plumbum
import toml

''' Common template functions are stored here '''

CLOPY_CONFIG_DIR = Path('~/.config/clopy/templates').expanduser()

def to_path(fp: str) -> Path:
    ''' Convert str to Path '''
    if isinstance(fp, Path):
        return fp
    elif isinstance(fp, str):
        return Path(fp)

def render(src: str, tmpl_name: str, vardict: dict) -> str:
    ''' Renders the template file
        src: File path/directory of the template source
        tmpl_name: Name of the template file source
        vardict: A dictionary that contains the template variable names as keywords with.
    '''
    tmpl = Template(read_file(str(Path(src) / tmpl_name)))
    res = tmpl.render(vardict)
    return res

def output(dest: str, tmpl_name: str, tmpl: str):
    ''' Outputs the rendered template contents to the destination
        dest: File path/directory of the template output
        tmpl_name: Name of the destination file where the output will be written to
        tmpl: The contents of the file
    '''
    dest = str(to_path(dest) / tmpl_name)
    (plumbum.cmd.echo[tmpl] > dest)()

def promptf(prompt: str, val='') -> str:
    ''' Prompts the user with the given message and defaults to a set value if null'''
    return input(prompt.format(val)) or val

def match(s: str, choices: list) -> bool:
    ''' Checks if a str matches the given choices '''
    for choice in choices:
        if s == choice:
            return True
    return False

def loadcfg(cfp: str, cfg: dict) -> dict:
    ''' Loads the given config file for a template
        cfp: Config file path
        cfg: Default/Empty config file dictionary

        `loadcfg` reads the contents of cfp into a dictionary, and returns
        the config file as a dict if it exists, and returns cfg if the dict doesn't exist.
    '''
    hostfp = f'{CLOPY_CONFIG_DIR}/{cfp}'
    if (to_path(hostfp).exists()):
        return toml.loads(read_file(hostfp))["config"]
    return cfg

def mkdest(path: Path, cmd: str):
    ''' Initializes or overwrites the destination directory '''
    if (not path.exists()): # If dest doesn't exist
        mkdir(path)
    elif (len([path.iterdir()]) != 0): # If dest is not empty
        overwrite = ''
        while (not match(overwrite.lower(), ['y', 'n', 'no', 'yes'])):
            overwrite = input((f'{path} is not empty. Overwrite? [y/n]: '))
            if (cmd == 'init' or (overwrite.lower() == 'n' or overwrite.lower() == 'no')):
                return 0

def init_all(fp:str, tmpls: dict) -> dict:
    ''' Renders all file templates, and returns the output files '''
    outputs = {}
    for name, vardict in tmpls.items():
        outputs[name.removesuffix(".tmpl")] = (render(fp, name, vardict))
    return outputs
