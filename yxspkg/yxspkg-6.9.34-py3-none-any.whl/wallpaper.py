from urllib import request
import ssl
import time 
from pathlib import Path
import os
import random 
import click
import subprocess
from bs4 import BeautifulSoup
from hashlib import md5
import requests
import fcntl
global_urls = ['https://eatshit.cn/',
            'https://acg.yanwz.cn/wallpaper/api.php',
            'https://api.lyiqk.cn/scenery',
            'https://random.52ecy.cn/randbg.php',
            'https://img.paulzzh.com/touhou/random',
            'https://www.dmoe.cc/random.php',
            'https://api.cyfan.top/acg',
            'https://wallhaven.cc/hot',
            'https://wallhaven.cc/hot',
            'https://wallhaven.cc/hot',
            'https://wallhaven.cc/hot',
            'https://wallhaven.cc/hot',
            'https://wallhaven.cc/latest',
            'https://wallhaven.cc/toplist',
            'https://wallhaven.cc/random']
ssl._create_default_https_context = ssl._create_unverified_context
opener=request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
request.install_opener(opener)
def is_already_running(lock_name,pf=[]):
    p = Path.home()/'.yxspkg'
    if not p.is_dir():
        os.makedirs(p)
    f = open(p/lock_name,'w')
    pf.append(f)
    try:
        fcntl.flock(f,fcntl.LOCK_NB | fcntl.LOCK_EX)
        return False
    except:
        return True
def get_picture_from_url(output,url):
    request.urlretrieve(url,output)
    return output
def get_picture_from_wallhavern(output,url='https://wallhaven.cc/hot',lin=None):
    ft = request.urlopen(url).read()
    bt = BeautifulSoup(ft,'lxml')
    ul = bt.body.main.section.ul
    li_list = ul.find_all('li')
    if lin is None:
        lin = random.randint(0,len(li_list)-1)
    a = li_list[lin].figure.a
    href = a.attrs['href']
    t = request.urlopen(href).read()
    bt2 = BeautifulSoup(t,'lxml')
    img = bt2.body.main.section.img
    src = img.attrs['src']
    print(src)
    suffix = Path(src).suffix 
    output = Path(output).with_suffix(suffix)
    request.urlretrieve(src,output)
    return output
def get_picture_from_url_set(output):

    url = random.choice(global_urls)
    if url.find('wallhaven.cc') !=-1:
        kdd = {'hot':26}
        key = url.split('/')[-1]
        kmax = kdd.get(key,100)
        rid = random.randint(1,kmax)
        url += f'?page={rid}'
        return get_picture_from_wallhavern(output,url)
    else:
        return get_picture_from_url(output,url)
def rename_picture(abs_path):
    abs_path = Path(abs_path)
    m = md5(open(abs_path,'rb').read())
    new_name = abs_path.with_name(m.hexdigest()).with_suffix(abs_path.suffix)
    os.rename(abs_path,new_name)
    return new_name
def set_wallpaper(screen_name='DP-2',url=None):
    abs_path = Path.home()/'.yxspkg'/'wallpapers'
    if not abs_path.is_dir():
        os.makedirs(abs_path)
    abs_path = abs_path / (str(int(time.time()))+'.jpg')
    if url:
        abs_path = get_picture_from_url(abs_path,url)
    else:
        abs_path = get_picture_from_url_set(abs_path)
    abs_path = rename_picture(abs_path)
    if not abs_path.exists() or abs_path.stat().st_size<1000:
        for _ in range(10):
            get_picture_from_url_set(abs_path)
            if abs_path.exists() and abs_path.stat().st_size>1000:
                break 
    if abs_path.exists() and abs_path.stat().st_size>1000:
        cmd = f'dbus-send --dest=com.deepin.daemon.Appearance /com/deepin/daemon/Appearance --print-reply com.deepin.daemon.Appearance.SetMonitorBackground string:"{screen_name}" string:"file:///{abs_path}"'
        subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")

@click.command()
@click.option('--screen','-s',default=None,help='设置显示器的名称，右键显示设置可以查看')
@click.option('--url',default=None,help='指定url')
@click.option('--show_urls',default=False,help='显示内置的url',is_flag=True)
@click.option('--time_interval','-t',default=0,help="壁纸更换时间间隔，默认0s")
@click.option('--lock_name','-l',default='',help="进程锁定名称，防止重复执行")
def main(screen,url,show_urls,time_interval,lock_name):
    if show_urls:
        for i in global_urls:
            print(i)
    if screen:

        if lock_name and not is_already_running(lock_name):
            print('start ...')
            while True:
                try:
                    set_wallpaper(screen,url)
                except:
                    pass
                if time_interval>0:
                    time.sleep(time_interval)
                else:
                    break
if __name__=='__main__':
    main()