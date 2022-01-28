import os

def repository(repo):
    if repo == 'ailever':
        os.system('git clone https://github.com/ailever/ailever.git')
    elif repo == 'programming-language':
        os.system('git clone https://github.com/ailever/programming-language.git')
    elif repo == 'numerical-method':
        os.system('git clone https://github.com/ailever/numerical-method.git')
    elif repo == 'applications':
        os.system('git clone https://github.com/ailever/applications.git')
    elif repo == 'deep-learning':
        os.system('git clone https://github.com/ailever/deep-learning.git')

