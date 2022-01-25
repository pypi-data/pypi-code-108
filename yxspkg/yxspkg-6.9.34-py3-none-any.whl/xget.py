from pathlib import Path 
import re
import os
from urllib.request import urlretrieve
from urllib.parse import urlparse
import urllib 
import click
import json
import sys
import threading 
import time
import requests
import pickle
import hashlib
from urllib.parse import unquote

from bs4 import BeautifulSoup
def cal_md5(string):
    return hashlib.md5(string.encode()).digest()
class async_run:
    def __init__(self,max_threads = 5,time_wait = 0.001):
        self.running_threads = 0
        self.max_threads = max_threads
        self.time_wait = time_wait

    def append_params(self,func,params):
        while self.running_threads >= self.max_threads:
            time.sleep(self.time_wait)
        t=threading.Thread(target=self.wrapper_func,args=(func,params))
        t.start()
    def wrapper_func(self,*args):
        func,params = args
        self.running_threads += 1
        t = func(*params)
        self.running_threads -= 1
        return t 
global_dict = dict()
global_dict['url_set'] = set()

global_pickle = {'files':dict(),'urls':set()}
def is_html_file(fname):
    md5_tag = cal_md5(str(fname))
    files = global_pickle['files']
    if md5_tag in files:
        attr = files[md5_tag]
    else:
        attr = {}
        files[md5_tag] = attr
    if attr.get('parsed'):
        return False
    if 'h' in attr:
        return attr['h']
    global_dict['new_html'] = True
    data = open(fname,'rb').read(1000)
    if data.find(b'html'):
        attr['h'] = True
    else:
        attr['h'] = False
    return attr['h']

def get_html_url_bs4(html):
    pagesoup=BeautifulSoup(html,'lxml')
    hrefs = [('h',link.get('href')) for link  in pagesoup.find_all(name='a')]
    sts = ('src','data-src','xsrc')
    src = [('s',link.get(src_title)) for link  in pagesoup.find_all() for src_title in sts]
    src = [i for i in src if i[1]]
    return hrefs+src
def get_html_url_re(html):
    if isinstance(html,bytes):
        return get_html_url_re_bytes(html)
    def deal_with(url):
        title = 'h' if url[0] == 'h' else 's'
        for nos in '(+\\':
            if url.find(nos) !=-1:
                ut = None 
                break
        else:
            dn = url.find('=')
            ut = url[dn+1:].strip()
            if ut[0] == '"' or ut[0] == "'":
                ut = ut[1:]
        return title,ut
    href = re.compile('(href|src)= *.[^\'\" )]*')
    s = [deal_with(h.group()) for h in href.finditer(html)]
    s = [i for i in s if i[1]]
    return s
def get_html_url_re_bytes(html):
    def deal_with(url):
        title = 'h' if url[0] == b'h' else 's'
        for nos in b'(+\\':
            if url.find(nos) !=-1:
                ut = None 
                break
        else:
            dn = url.find(b'=')
            ut = url[dn+1:].strip()
            if ut[0] == ord('"') or ut[0] == ord("'"):
                ut = ut[1:]
        return title,ut
    href = re.compile(b'(href|src)= *.[^\'\" )]*')

    s = [deal_with(h.group()) for h in href.finditer(html)]
    s = [(i,v.decode()) for i,v in s if v]
    return s
def get_html_url(html,filetype='text',ftype='bs4',title_dict = {'h':'href','s':'src'},charset_list=[1,'utf-8','gbk']):
    if filetype == 'path':
        read_ok = False
        for i in range(2):
            try:
                charset = charset_list[charset_list[0]]
                html = open(html,encoding=charset).read()
                include_html = global_dict['include_html']
                if include_html:
                    for g in include_html:
                        is_ok = True
                        for i in g:
                            if html.find(i) == -1:
                                is_ok = False
                                break 
                        if is_ok:
                            break
                    else:
                        return []
                include_html_re = global_dict['include_html_re']
                if include_html_re:
                    if not include_html_re.search(html):
                        return []
                read_ok = True
            except Exception as e:
                charset_list[0] += 1
                if charset_list[0] == len(charset_list):
                    charset_list[0] = 1
        if not read_ok:
            return []
    if ftype == 'bs4':
        t = get_html_url_bs4(html)
    else:
        t = get_html_url_re(html)
    return [f'{title_dict[title]}="{val}"' for title,val in t]


def get_all_url(filename):
    p = Path(filename)
    if p.is_file():
        i = p
        for h in get_html_url(i,filetype='path'):
            yield i,h
        yield False,False
    else:
        htmls = 0
        for root,_,files in os.walk(p): 
            proot = Path(root)
            for j in files:
                if j.endswith('.xget'):
                    continue
                i = proot / j
                if is_html_file(i):
                    htmls += 1
                    for h in get_html_url(i,filetype='path'):
                        yield i,h
                    md5_tag = cal_md5(str(i))
                    files = global_pickle['files']
                    if md5_tag in files:
                        files[md5_tag]['parsed']=True 
                    else:
                        files[md5_tag] = {'parsed':True} 
        if htmls == 0:
            yield False,False

            
def get_name_url(p,url,http='https'):
    # p:dir_path : Path('www.baidu.com/s/')
    urlp = urlparse(url)
    netloc = urlp.netloc
    if not url:
        return None,None
    if netloc:
        fname = Path(url[url.find('://')+3:])
        if not url.startswith('http'):
            url = http +':'+url
        hurl  = url
    else:
        ipre = 0
        while url.startswith('../'):
            ipre += 1
            url = url[3:]
        
        if url[0:2] == './':
            url = url[2:]
        elif url[0] == '/':
            ipre = len(p.parts) - 1
            url = url[1:]


        if ipre>0:
            parts = p.parts[:-ipre]
        else:
            parts = p.parts
        pdir = Path(os.sep.join(parts))
        fname = pdir / url
        hurl = http+'://'+str(fname)

    return Path(unquote(str(fname))),hurl

def check_quit(*d):
    p = Path('stop')
    if p.exists():
        os.remove(p)
    ii = 0
    while True:
        if p.exists():
            global_dict['quit'] = True 
            break
        else:
            ii+=5
            if ii>7200:
                write_cache()
                ii = 0
            time.sleep(5)
def write_cache():
    cache_name = global_dict.get('cache_name','xget_cache.pickle')
    fp = open(cache_name,'wb')
    t = pickle.dumps(global_pickle)
    fp.write(t)
    fp.close()
def read_cache():
    cache_name = global_dict.get('cache_name','xget_cache.pickle')
    if Path(cache_name).is_file():
        fp = open(cache_name,'rb')
        t = pickle.load(fp)
        if t:
            for k,v in t.items():
                global_pickle[k]=v
    if global_dict['force']:
        files = global_pickle['files']
        for _,v in files.items():
            v['parsed'] = False
def run(http,dirname,ftypes,include,exclude,sort):
    include_list = split_string(include)
    exclude_list = split_string(exclude)
    if global_dict['one']:
        u = get_all_url(global_dict['one_file'])
    else:
        u = get_all_url(dirname)
    if ftypes:
        ftypes = ['.'+i for i in ftypes.split('|')]
    dn = {'s':4,'h':5}
    ii = 0
    if sort:
        u = list(u)
        u.sort() 
    for pf,surl in u:
        if global_dict['quit']:
            break
        if pf is False:
            return True
        p = pf.parent
        url = surl[dn[surl[0]]:][1:-1]
        download = False
        filter_type = False
        
        if ftypes:
            filter_type = True
            for ft in ftypes:
                if url.endswith(ft):
                    download = True 
                    break 
            else:
                continue
        if exclude_list:
            filter_type = True 
            if match_ok(url,exclude_list):
                continue
        if include_list:
            filter_type = True 
            if match_ok(url,include_list):
                download=True
        else:
            download = True
        
        if not filter_type:
            download = True
        if download:
            ii += 1
            fname,hurl = get_name_url(p,url,http)
            if fname:
                download_file(fname,hurl)
    write_cache()
    return global_dict['quit']

def download_file_kernel(fname,url):
    # if urlparse(url).netloc != global_dict['netloc']:
    #     return
    
    parent_dir = fname.parent
    # 建立文件夹
    if not parent_dir.is_dir():
        pp = Path('.')
        for i in parent_dir.parts:
            pp = pp / i
            if pp.is_file():
                pt = pp.with_suffix('.__temp__ll')
                os.rename(pp,pt)
                try:
                    os.makedirs(pp)
                except:
                    pass
                os.rename(pt,pp/'index.html')
            elif not pp.exists():
                try:
                    os.makedirs(pp)
                except:
                    pass
    # 下载文件
    md5_tag = cal_md5(str(fname))
    files = global_pickle['files']
    if md5_tag in files:
        attr = files[md5_tag]
    else:
        attr = {}
        files[md5_tag] = attr
    if 'exists' in attr:
        print('file already exists (pickle).',fname)
        return 'exit'
    if fname.exists():
        print('file already exists.',fname)
        attr['exists'] = True
        return 'exit'
    print('downloading file',fname)
    try:
        for st in global_dict['nodownload']:
            #建立空文件 不进行下载
            if url.find(st) !=-1:
                open(fname,'wb').close()
                attr['exists'] = True
                return 'download'

        if global_dict['wget']:
            os.system(f'wget {url} -t2 -T 300 -O "{fname}"')
        elif global_dict['aria2']:
            tname = fname.parent / (fname.name+'.xget')
            os.system(f'aria2c {url} -o "{tname}"')
            aname = tname.parent / (tname.name+'.aria2')
            time.sleep(0.001)
            if not aname.is_file():
                os.rename(tname,fname)
                attr['exists'] = True
        else:
            content = global_dict['session'].get(url, stream=True)
            with open(fname, "wb") as fp:
                for chunk in content.iter_content(chunk_size=512):
                    fp.write(chunk)
            attr['exists'] = True
        return 'download'
    except Exception as e:
        print('download failed',e)

def download_file(fname,url):
    url_set = global_dict['url_set']
    if url in url_set:
        return
    url_set.add(url)
    global_dict['downloader'].append_params(download_file_kernel,(fname,url))
def init_env(fname,url,netloc):
    if fname.exists():
        os.remove(fname)
        md5_tag = cal_md5(str(fname))
        if md5_tag in global_pickle['files']:
            global_pickle['files'].pop(md5_tag)
    t = download_file_kernel(fname,url)
    if global_dict['one']:
        global_dict['one_file'] = fname 
        return
    if t=='exit':
        if fname.is_dir():
            p = fname / 'index.html'
            if not p.exists():
                download_file_kernel(p,url)
            else: 
                return
    if fname.name == netloc:
        temp_name = fname.with_suffix('.__temp__ll')
        os.rename(fname,temp_name)
        os.mkdir(fname)
        os.rename(temp_name,fname/'index.html')
def decode_direction(dirname):
    # 将编码过得目录名称进行解码
    parse = urllib.parse
    for root,dirs,fs in os.walk(dirname):
        proot = Path(root)
        for fn in fs:
            nfn = parse.unquote(fn)
            if fn != nfn:
                print(proot/nfn)
                os.rename(proot/fn,proot/nfn)
        r0 = parse.unquote(root)
        if r0 != root:
            print(r0)
            os.rename(root,r0)
def split_string(s):
    if s:
        groups = s.split('|')
        return [i.split('&') for i in groups]
    else:
        return list()
def match_ok(s,groups):
    for g in groups:
        is_ok = True
        for i in g:
            if s.find(i) == -1:
                is_ok = False 
                break 
        if is_ok:
            return True 
    return False

@click.command()
@click.argument('args',nargs=-1)
@click.option('--parallel','-p',default=2,help='必行下载数')
@click.option('--url',default=None,help='指定url')
@click.option('--ftypes',default=None,help='指定文件类型: js|html, 优先级：0')
@click.option('--include',default='',help='include string,url需要匹配到相似字符后再进行下载,不同字符串用逗号隔开 image|pictures ')
@click.option('--exclude',default='',help='exclude string,url匹配到相似字符后不再进行下载，先进行exclude判断再进行include判断，优先级：1')
@click.option('--include_html',default='',help='html文件中需要包含该字符串，才被视为有用的html文件，否则不进行提取 例如： "你好&hello|thank you"')
@click.option('--include_html_re',default='',help='与include_html功能相似，采用正则匹配')
@click.option('--decode_name',default='',help='对目录名称进行解码处理')
@click.option('--convert_links','-k',default='',help='转换为本地url')
@click.option('--cache_name',default='xget_cache.pickle',help='记录文件处理状态')
@click.option('--cookie',default=None,help='指定cookie文件(.json)')
@click.option('--one',help="只下载一个页面的所有信息",is_flag=True)
@click.option('--recursive','-r',default=0,help='递归下载次数，默认为0，即为无限次递归')
@click.option('--sort',default=False,help='对待扫描的url进行排序',is_flag=True)
@click.option('--wget',default=False,help='使用wget进行下载',is_flag=True)
@click.option('--aria2',default=False,help='使用aria2进行下载',is_flag=True)
@click.option('--nodownload',default='',help='url中含有指定字符的不进行真实的下载，如nodownload设置为 ".jpg|.png"，则对该文件不进行下载，只写入一个大小为0的文件')
@click.option('--force',default=False,help='强制下载,忽略parsed参数',is_flag=True)
def main(args,parallel,url,include,exclude,ftypes,decode_name,convert_links,one,sort,include_html,wget,include_html_re,aria2,recursive,force,nodownload,cache_name,
        cookie):
    if not url:
        url = args[0]
    headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}  

    purl = urlparse(url)
    scheme = purl.scheme
    netloc = purl.netloc 
    global_dict['scheme'] = scheme
    global_dict['netloc'] = netloc
    global_dict['cookie'] = cookie 
    if cookie:
        t = json.load(open(cookie))
        headers.update(t)
    global_dict['session'] = requests.Session()
    global_dict['session'].headers = headers
    global_dict['downloader'] = async_run(max_threads=parallel)
    global_dict['include_html'] = split_string(include_html)
    if include_html_re:
        global_dict['include_html_re'] = re.compile(include_html_re)
    else:
        global_dict['include_html_re'] = None

    fname,hurl = get_name_url(None,url)

    global_dict['one'] = one 
    global_dict['first_url'] = url
    global_dict['wget'] = wget
    global_dict['aria2'] = aria2
    global_dict['quit'] = False 
    global_dict['force'] = force
    global_dict['cache_name'] = cache_name
    global_dict['nodownload'] = [i for i in nodownload.split('|') if i]
    read_cache()
    quit_thread = threading.Thread(target=check_quit)
    quit_thread.setDaemon(True)
    quit_thread.start()
    init_env(fname,url,netloc)
    while True:
        global_dict['new_html'] = False
        if run(scheme,netloc,ftypes,include,exclude,sort):
            break
        if not global_dict['new_html']:
            break
        if one:
            break
        if recursive>0:
            if recursive==1:
                break
            else:
                recursive -= 1
    if decode_name:
        decode_direction(decode_name)
    if convert_links:
        from . import convert_url
        convert_url.convert_dir(convert_links,parallel)
if __name__=='__main__':
    main()