import numpy as np
def compute_gcd(X):
    if len(X)==1:
        return X
    elif len(X)==2:
        x,y=X
    else:
        return compute_gcd([compute_gcd(X[0:2]),compute_gcd(X[2:])])
    while(y):
        x, y = y, x % y
    return x

def MWs(table_file):
    mws_dict = {}
    with open(table_file) as f:
        lines = f.readlines()
        for li in lines:
            li_lst = li.split()
            if '#' not in li_lst[0]:
                mws_dict[li_lst[2]] = float(li_lst[0])/1000
    return mws_dict

def txt2dict(txt):
    lines=txt.split('\n')
    keys=lines[0][1:].split()
    vals_arr=[]
    for linei in lines[1:]:
        vals = linei.split()
        if len(vals)==len(keys):
            vals_arr.append([float(vali) for vali in vals])
    vals_arr=np.array(vals_arr)
    res_dict={}
    for k,v in zip(keys,vals_arr.T):
        res_dict[k]=v
    return res_dict
