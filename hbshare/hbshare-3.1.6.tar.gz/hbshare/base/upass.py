# -*- coding:utf-8 -*- 

"""
Created on 2020/6/15
@author: Meng Lv
@group: Howbuy FDC
@contact: meng.lv@howbuy.com
"""

import pandas as pd
import os
from hbshare.base import vars as ct


def set_token(token):
    df = pd.DataFrame([token], columns=['token'])
    user_home = os.path.expanduser('~')
    fp = os.path.join(user_home, ct.TOKEN_F_P)
    df.to_csv(fp, index=False)
    
    
def get_token():
    user_home = os.path.expanduser('~')
    fp = os.path.join(user_home, ct.TOKEN_F_P)
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        return str(df.iloc[0]['token'])
    else:
        print(ct.TOKEN_ERR_MSG)
        return None

def set_env(env):
    df = pd.DataFrame([env], columns=['env'])
    user_home = os.path.expanduser('~')
    fp = os.path.join(user_home, ct.TOKEN_F_P)
    df.to_csv(fp, index=False)

def get_env():
    user_home = os.path.expanduser('~')
    fp = os.path.join(user_home, ct.ENV_F_P)
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        return str(df.iloc[0]['env'])
    else:
        return None

def is_prod_env():
    return False if ct.ENV_PROD != get_env() else True
