# 这是一个matplotlib显示中文的库，只要你在文件开头调用即可
# 调用方式
# from yxspkg import matplotlib_chinese

from pathlib import Path 
import sys
import os
import json
from urllib import request
from matplotlib import font_manager
import matplotlib as mpl

if sys.platform.startswith('linux'):
    p = Path(os.environ['HOME']) /'.cache'/'matplotlib'
    json_path = list(p.glob('*.json'))[0]
    json_data = json.load(open(json_path))
    need_install_simhei = True
    for i in json_data['ttflist']:
        if i['name'] == 'SimHei':
            need_install_simhei = False
            break
    else:
        
        need_install_simhei = True
        url = 'https://github.com/blacksong/fragment/raw/master/simhei.ttf'
        yxspkg_path = Path(os.environ['HOME']) /'.yxspkg' /'matplotlib'
        if not yxspkg_path.exists():
            os.makedirs(yxspkg_path)
        ttf = yxspkg_path/'SimHei.ttf'
        if not ttf.exists():
            print('Downloading SimHei.ttf from GitHub:{}'.format(url))
            request.urlretrieve(url,ttf)
        myfont = font_manager.FontProperties(fname=str(ttf)) 
        ttf_info = {
            'fname':str(ttf),
            'name':myfont.get_name(),
            'style':myfont.get_style(),
            'variant':myfont.get_variant(),
            'weight':myfont.get_weight(),
            'stretch':myfont.get_stretch(),
            'size':myfont.get_size(),
            '__class__':'FontEntry'
            }
        json_data['ttflist'].append(ttf_info)
        json.dump(json_data,open(json_path,'w'),indent=4, separators=(',', ': '))
    mpl.rcParams['font.sans-serif'] = ['SimHei'] 
    mpl.rcParams['axes.unicode_minus'] = False
