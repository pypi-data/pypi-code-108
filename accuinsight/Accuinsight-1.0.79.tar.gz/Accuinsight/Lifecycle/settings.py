import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


def setAPI(api_url, api_port):
    editList = ["BACK_END_API_URL = '{}'".format(api_url), 
                '\n',
                "BACK_END_API_PORT = '{}'".format(api_port)]
    
    LcConst_path = '/usr/lib/modeler-python-package/Accuinsight/modeler/core/LcConst/LcConst.py'   # 수정 필요
    
    with open(LcConst_path, 'r+') as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if not line.startswith('BACK_END_API_URL') and not line.startswith('BACK_END_API_PORT'):
                f.write(line)
        f.truncate()
        for i in editList:
            f.write(i)
            
    with open(LcConst_path, 'r') as f:
        
        for line in f:
            if line.startswith('BACK_END_API_URL'):
                a = line
            elif line.startswith('BACK_END_API_PORT'):
                logging.info('[Edited] {}         {}'.format(a, line))
