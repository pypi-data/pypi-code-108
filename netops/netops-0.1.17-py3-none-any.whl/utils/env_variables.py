import os

def set_env_vars(dic):
    """ TODO: translate to English
    Cria variaveis de ambiente iguais as chave valor de um dicionario de entrada.
    
    Recebe:
            dic = Dicionario que contem as chave valor a serem transformados em variaveis
            de ambiente"""
    for key in dic.keys():
        # Set environment variables
        os.environ[key.upper()] = dic[key]
    
    return
