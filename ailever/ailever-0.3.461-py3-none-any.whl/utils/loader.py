import os
from urllib.request import urlretrieve

def repository(repo, tree=None, path=None):
    if not tree and not path:
        if repo == 'list':
            print('[AILEVER] List of contents in the repository')
            contents = ['ailever',
                        'openapi',
                        'programming-language',
                        'numerical-method',
                        'statistics',
                        'applications',
                        'deep-learning',
                        'reinforcement-learning']
            for content in contents:
                print(f'* {content}')
        elif repo == 'ailever':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/ailever.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'openapi':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/openapi.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'programming-language':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/programming-language.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'numerical-method':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/numerical-method.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'statistics':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/statistics.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'applications':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/applications.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'deep-learning':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/deep-learning.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        elif repo == 'reinforcement-learning':
            os.chdir('./')
            os.system('git clone https://github.com/ailever/reinforcement-learning.git')
            if os.path.isdir(f'{repo}'):
                print(f'[AILEVER] The repository "{repo}" is successfully cloned!')
        

    elif tree:
        urlretrieve('https://raw.githubusercontent.com/ailever/ailever/master/storage/'+repo+'.txt', f'./{repo}.txt')
        print(f'[AILEVER] The file "{repo}.txt" about directory structure of repository "{repo}" is successfully downloaded!')
        
    elif path:
        urlretrieve('https://raw.githubusercontent.com/ailever/'+repo+'/master/'+path, f'./{os.path.split(path)[-1]}')
        print(f'[AILEVER] The file "{path} in repository {repo}" is successfully downloaded!')


def cloud(name=None):
    if name == 'list':
        print('[AILEVER] List of contents in the cloud')
        contents = ['template.pptx',
                    'regression.pptx']
        for content in contents:
            print(f'* {content}')

    elif name == 'template.pptx':
        urlretrieve('https://docs.google.com/uc?export=download&id=1MFQuoE1B58TSice5aPDqQDdSJqu1CLB3', f'./{name}')
    elif name == 'regression.pptx':
        urlretrieve('https://docs.google.com/uc?export=download&id=1OsS7Dd56yf9VftF7BBLWxECI9l_xmksG', f'./{name}')
    
    if name != 'list':
        print(f'[AILEVER] The file "{name}" is downloaded!')


