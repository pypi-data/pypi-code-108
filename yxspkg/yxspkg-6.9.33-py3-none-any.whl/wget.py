import fire
import requests
import re,os
from multiprocessing.pool import ThreadPool
from os import path
from hashlib import md5
from bs4 import BeautifulSoup 
import sys
import shelve
import time
import copy
__version__='0.1.3'
__author__="Blacksong"
class Wget:
    def __init__(self,url,**kargs):
        url0=url
        url=url.split('?')[0]
        self.n=0
        dbname=md5(url.encode()).hexdigest()[:7]+'.pydb'

        self.filetype=kargs.get('filetype','.jpg')
        self.iterarion = kargs.get('iter','NO')
        if self.iterarion == 'NO':
            record_db = dict()
        else:
            record_db=shelve.open(dbname)

        self.headers=self.setheaders()
        self.srcpro=None
        self.rule=kargs.get('rule',list())
        self.re_rule=kargs.get('re_rule',list())
        self.max_download=8
        self.num_download = 0
        self.asyncThread=ThreadPool(self.max_download)
        self.htm=url.split('/')[2]
        print(self.htm,'htm')
        dirname = kargs.get('dirname',None)
        if dirname is None:
            dirname = self.htm
        if not path.isdir(dirname): 
            os.makedirs(dirname)
        self.dirname = dirname
        self.auto=kargs.get('auto',True)
        print(self.htm)

        self.rule_list=[re.sub('[^A-Za-z]','', url)]
        [self.rule_list.append(re.sub('[^A-Za-z]','', i)) for i in self.rule]
        self.rule_list=list(set(self.rule_list))
        self.rule_dir=[path.dirname(url)]
        [self.rule_dir.append(path.dirname(i)) for i in self.rule]
        self.rule_dir=list(set(self.rule_dir))

        self.re_rule=[re.compile(i) for i in self.re_rule]
        url=url0
        print(self.re_rule,'\n',self.rule_dir,'\n',self.rule_list)
        
        try:
            halt=record_db.get('halt',False)
            if halt == True:
                self.href=record_db.get('href',[(url,{})])
                self.pagedb = record_db.get('pagedb',set())
                self.srcdb = record_db.get('srcdb',set())
                record_db['halt']=False
            else:
                self.href=[(url,{})]
                self.pagedb=set()
                self.srcdb=set()
            self.autofind(url)
            self.main()
            record_db.close()
            if path.isfile(dbname): os.remove(dbname)
        except:
            print('the program is halted!')
            record_db['halt']=True
            record_db['srcdb']=self.srcdb
            record_db['pagedb']=self.pagedb
            record_db['href']=[i for i in self.href if i!=None]
        self.asyncThread.close()
        self.asyncThread.join()
    def my_hash(self,x):
        return int(md5(x.encode()).hexdigest()[:8],16)
    def setheaders(self):
        headers='''
User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Host: i.meizitu.net
Referer: http://www.mzitu.com/131504/5
'''
        headers=headers.split('\n')
        d=dict()
        for i in headers:
            n=i.find(':')
            if n ==-1:continue
            d[i[:n].strip()]=i[n+1:].strip()
        return d
    def getHost(self,url):
        return url.split('/')[2]
    def autofind(self,url):
        print('Autofind the label of the target picture')
        volume=0
        x,y=self.Analyze(url)
        
        r=set()
        for i in y:
            s=str(i[1])
            if self.iterarion == 'NO':
                self.Download(i[0],i[0])
            if s in r:continue
            r.add(s)
            try:
                headers = self.headers
                headers['Host']=self.getHost(i[0])
                headers['Referer']=url
                f=requests.get(i[0],timeout=30,headers = headers).content
                t=len(f)
                
            except:
                t=0
            print(t,i[0])
            if volume<t:
                volume=t
                tt=i[1]
        if self.iterarion == 'NO':
            sys.exit(0)

        self.srcpro=tuple(tt.items())
        print(self.srcpro)
    def main(self):
        '''主循环函数，控制寻找页面以及查找页面资源链接，主要起控制作用'''
        def run(u):
            print('Analyse the html ',u)
            hr,src=self.Analyze(u)

            for i in src:
                if self.UsefulSrc0(*i):
                    self.num_download+=1
                    self.asyncThread.apply_async(self.Download,(i[0],u))
                    while self.num_download>self.max_download+4:
                        time.sleep(1)
                    # self.Download(i[0],u)
            self.pagedb.add(self.my_hash(u))
            for i in hr:
                if self.UsefulHtml0(*i):
                    self.href.append(i)
        while True:
            ii=0
            n=len(self.href)
            while ii<n:
                if self.UsefulHtml0(*self.href[ii]):
                    run(self.href[ii][0])
                self.href[ii]=None
                ii+=1
            self.href=[i for i in self.href if i!=None]

            if len(self.href)==0 or self.iterarion=='NO':break
    def DivSplit(self,s):
        '''将一个html页面分成多个div块，主要通过寻找div标签的位置，返回一个记录了div块所在位置以及各个块的名字的链表'''
        a=[]
        [a.append((-1,i.span())) for i in re.finditer('< *div[^><]*>', s)]
        b=[]
        for i,j in a:
            if i==1:
                b.append((i,j[0]))
            else:
                t=s[j[0]:j[1]]
                n=re.findall('id *= *"[^"]*"|class *= *"[^"]*"', t)
                d=dict([i.replace('"','').split('=') for i in n])
                b.append((i,j[0],d))
        b.sort(key=lambda x:x[1])
        return b
    def DivSplit2(self,s):
        '''将一个html页面分成多个div块，主要通过寻找div标签的位置，返回一个记录了div块所在位置以及各个块的名字的链表'''
        a=[(-1,0,{'id':'mystart'})]
        for i in re.finditer('(id|class) *=["\' ]*[^"\']*', s):
            j=re.sub('["\' ]', '',i.group())
            n=j.find('=')
            d={j[:n]:j[n+1:]}
            a.append((-1,i.span()[1],d))
        a.sort(key=lambda x:x[1])
        return a
    def Download(self,url,purl,nn=[0]):
        '''下载url'''
        if self.iterarion == 'NO':
            print('Downloading ',url)
        tf=re.sub('\W','', purl)
        filename=self.dirname+'/'+tf[-min(len(tf),10):]+md5(url.encode()).hexdigest()[:5]+self.filetype
        if not path.isfile(filename):
            nn[0]+=1
            if nn[0]%50==0:
                print('Downloading ',url)
            headers = self.headers
            headers['Host']=self.getHost(url)
            headers['Referer']=purl
            x=requests.get(url,timeout=30,headers = headers)
            t=open(filename,'wb').write(x.content)
        else:
            print('file already exist')
        self.srcdb.add(self.my_hash(url))
        self.num_download -= 1
        return filename
    def UsefulHtml0(self,url,pro):
        '''判断一个页面的url是否是有用的'''
        if self.my_hash(url) in self.pagedb:return False
        if self.re_rule:
            for i in self.re_rule_list:
                if i.search(url):return True
        if not self.rule:
            if not re.search(self.htm, url):return False
        t= re.sub('[^A-Za-z]','', url)
        d=path.dirname(url)
        if t in self.rule_list:return True
        if d in self.rule_dir:return True
        if self.auto:
            return False
        return self.UsefulHtml(url,pro)
    def UsefulHtml(self,url,pro):
        '''判断一个页面的url是否是 有用的，这个函数可以在不同的环境中重写，其中pro是该链接所在div的属性'''
        return True
    def UsefulSrc0(self,url,pro):
        if self.my_hash(url) in self.srcdb:return False
        if self.auto:
            for k,v in self.srcpro:
                if v.isdigit():continue
                if pro.get(k)!=v:return False
        return self.UsefulSrc(url,pro)
    def UsefulSrc(self,url,pro):
        return True
    def correct_url(self,s,website,webdir):
        if s[0]=='/':return website+s
        elif s=='#':return ''
        elif s.find('http')!=-1:return s
        else: return webdir+s
    def Analyze(self,url):
        '''返回 href 和 src的链接，返回值为一个二元tuple'''
        headers = self.headers
        headers['Host']=self.getHost(url)
        s=requests.get(url,timeout=30,headers = headers).text
        divs=self.DivSplit(s)
        href=[]
        src=[]
        split_url=url.split('/')
        website='/'.join(split_url[:3])
        webdir='/'.join(split_url[:-1])+'/'
        for i in re.finditer(' *(href|src) *=["\' ]*[^ )("\';\+>}]+', s):
            div=self.FindDiv(divs, i.span()[0])
            j=i.group()
            j=re.sub('["\' \\\\]', '', j) #针对某些网站将url写在javascript中，用到了转义符\
            if j[0]=='h':
                j=j.replace('href=', '')
                j=self.correct_url(j,website,webdir)
                if len(j)==0:continue
                href.append((j,div))
            if j[0]=='s':
                j=j.replace('src=', '')
                if j.find(self.filetype)==-1:continue
                div=self.FindDiv(divs, i.span()[0])
                j=self.correct_url(j,website,webdir)
                if len(j)==0:continue
                src.append((j,div))
        return href,src
    def FindDiv(self,divs,pos):
        a,b=0,len(divs)
        if b==0:
            return {'id':'nodivs'}
        if pos>divs[-1][1]:return divs[-1][2]
        while b-a>1:
            t=int((a+b)/2)
            p0=divs[t][1]
            if pos>p0:a=t
            else:b=t
        return divs[a][2]
class Wget_novel:
    website = ['https://www.x83zw.com/', 'https://www.zhuaji.org/','https://www.ybdu.com/',
    'https://www.23us.so']
    trans=str.maketrans('一二三四五六七八九','123456789')
    trans2=str.maketrans(dict(zip(['零','十','百','千','万','亿'],['','0 ','00 ','000 ',' 10000 ',' 100000000 '])))
    trans.update(trans2)
    def __init__(self,url,novel_name=None,author = None,chapter_attrs=None,content_attrs=None,next_attrs=None):
        content = requests.get(url)
        bs=BeautifulSoup(content.content)

        self.re_br = re.compile('<[^>]+>')
        self.re_n = re.compile('[\n]+')
        self.re_chapter = re.compile('(第[\d]+[章节回]|第[一二三四五六七八九]+[章节回])')
        self.re_chinese_number = re.compile('[一二三四五六七八九十零百千万\d]+')

        self.author = author
        self.chapter_attrs = chapter_attrs
        self.content_attrs = content_attrs 
        self.next_attrs = next_attrs
        
        title,author = self.__get_author(bs)
        self.__auto_select(bs)
        print(self.chapter_attrs,self.content_attrs,self.next_attrs)
        print(title,author)
        if novel_name is None:fname=title+'.txt'
        else:fname=novel_name+'.txt'
        self.fp=open(fname,'w',encoding = 'utf8')
        print(fname)
        self.fp.write(title+'\n'+author+'\n')
        self.chapter=[]
        try:
            self.__start(url)
        except Exception as e:
            print(e)
        self.fp.close()
        x=set(self.chapter)
        y=set(range(1,max(self.chapter)+1))
        print(y-x)
    def div_generate(self,bs,div_list=None):
        if div_list is None:
            div_list = list()
        if bs.div is None:
            return div_list
        for i in bs.find_all('div'):
            div_list.append(i)
            self.div_generate(i,div_list)
        return div_list
    def __auto_select(self,bs):#自动识别 章 div标签 正文div标签 和下一章div标签
        div_list = self.div_generate(bs)
        if self.chapter_attrs is None:
            for i in div_list:
                t = i.text.lstrip()
                if len(t)>50:
                    continue
                if self.re_chapter.match(t):
                    self.chapter_attrs = i.attrs
                    break
            else:
                try:
                    t = self.__get_chapter(bs)
                    if not self.re_chapter.match( t[0]):
                        assert False
                except:
                    title = bs.title.text
                    t = self.re_chapter.search( title)
                    chapter = t.group()
                    t = title.split(chapter)
                    self.chapter_attrs = len(t)

        if self.content_attrs is None:
            length = 0
            for i in div_list:
                div = copy.deepcopy(i)
                for j in div.find_all('div'):
                    j.decompose()
                l = len(re.sub('\s','',div.text))
                if length<l:
                    length = l
                    self.content_attrs = div.attrs
        if self.next_attrs is None:
            for i in div_list:
                if i.div:continue
                t = re.sub('\s', '', i.text)
                if len(t)>50:
                    continue
                if t.find('下一') !=-1 and t.find('上一') != -1 and i.a is not None:
                    self.next_attrs = i.attrs
                    break

    def __start(self,url):#主循环函数
        self.url = url
        re_sub_title = re.compile('^[^\n]+\n')
        while True:
            print(url,'url')
            content = requests.get(url)
            bs = BeautifulSoup(content.content)
            title_info=self.__get_chapter(bs)
            self.chapter.append(title_info[-1])
            print(title_info)
            #必须先找下一页才能找内容，查找内容会破坏bs数据
            next_info=self.__get_next(bs)
            content_info=self.__get_content(bs)
            
            if title_info[0] is not None:
                titles = '\n\n'+title_info[0]+' '+title_info[1]+'\n\n'
                if content_info.startswith(title_info[0]):
                    content_info = re_sub_title.sub('',content_info)
                self.fp.write(titles)
                self.fp.write(content_info)
            if next_info is False:break
            url=next_info
    def __get_author(self,bs):
        title = bs.title.text.split()
        title = ''.join(title)
        return title,'作者：无名氏'
    def __get_content(self,bs):
        x = bs.find(attrs=self.content_attrs)
        if x.div:
            for i in x.find_all('div'):
                i.decompose()
        sx = str(x)

        a = x.find_all('a')
        for i in a:
            sx = sx.replace(str(i),'')
        sx = self.re_br.sub('\n',sx)
        sx = self.re_n.sub('\n',sx)
        return sx.strip()
    def __get_next(self,bs,html=None):
        c=bs.find(attrs=self.next_attrs)
        t=c.find_all('a')
        for i in t:
            if i.text.find('下')!=-1:
                href=i['href']
        if len(href)==0:return False
        if href[0]!='/':
            url=self.url.split('/')
            url[-1]=href
            return '/'.join(url)
        else:
            url=self.url.split('/')
            url = url[:3]
            url.append(href)
            return '/'.join(url)
    def __get_chapter(self,bs,html=None):
        if isinstance(self.chapter_attrs,int):
            title = bs.title.text
            t = self.re_chapter.search( title)
            chapter = t.group()
            tt = title.split(chapter)
            n = self.__ChineseNumber_to_number(self.re_chinese_number.search(chapter).group())
            tt = chapter,tt[-1],n
            return tt
            
        else:
            title=bs.find(attrs=self.chapter_attrs).h1.text
            t=self.re_chinese_number.search(title)
            if not t:return None,None,-1
            t=t.group()
            n=self.__ChineseNumber_to_number(t)
            m=title.find(t)+len(t)
            name=title[m+1:].strip()
            if name:
                if name[0]=='章' or name[0]=='节':name=name[1:]
            else:
                name = ''
            name=re.sub(':|：|,|，','',name)
            s='第'+t+'章',name,n
        return s
    def __ChineseNumber_to_number(self,s):
        t=self.trans
        s=s.translate(t)
        l=s.rstrip().split()
        n,m=0,0
        for i in l:
            j=int(i)
            if j<10000:
                if j==0:j=10
                n+=j
            else:
                n*=j
                m+=n
                n=0
        m+=n
        return m
def main(url,**karg):
    print(url,karg)
    Wget(url,**karg)
if __name__=='__main__':
    fire.Fire(main)