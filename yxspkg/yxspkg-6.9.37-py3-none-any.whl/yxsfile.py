from curses.ascii import SP
from re import S
import webbrowser
import time
from pathlib import Path,PosixPath
from . import encrypt
from .file_server import flask_server
import hashlib
import os
import re
import click
# import shutil 
ENCODE_CODE = [chr(i) for i in  range(ord('a'),ord('z')+1)] + [chr(i) for i in  range(ord('A'),ord('Z')+1)]
ENCODE_CODE += [chr(i) for i in  range(ord('0'),ord('9')+1)]
ENCODE_CODE = (''.join(ENCODE_CODE)).encode()
global_dict = {'db':None}
class file_database:
    def __init__(self,dirname=None,database_name='.yxs_file_database.xdb'):
        if global_dict['db'] is not None:
            database_name = global_dict['db']
        self.dirname = dirname 
        if self.dirname:
            self.database = Path(self.dirname) / database_name
        else:
            self.dirname = './'
            self.database = Path(database_name)
        self.database_data = None
        self.file_info = dict()
    def create(self):
        dict2str = lambda x:'{'+','.join([f'{k}:{v}' for k,v in x.items()])+'}'
        fmt = '{zonename}{ftype}{is_link}__:{data}//{info}\n'
        fp = open(self.database,'w')
        fp.write('''#{zonename}{ftype}{is_link}__:{data}//{dict_info}\n''')
        for root,dirs,fs in os.walk(self.dirname):
            proot = Path(root)
            l = 'l' if proot.is_symlink() else '_'
            info = {'size':0,'st_mtime':int(proot.stat().st_mtime)}
            fp.write(fmt.format(zonename='z',ftype='d',is_link=l,data=root,info=dict2str(info)))
            for d in dirs:
                kf = proot/d
                l = 'l' if kf.is_symlink() else '_'
                info = {'size':0,'st_mtime':int(kf.stat().st_mtime)}
                fp.write(fmt.format(zonename='_',ftype='d',is_link=l,data=d,info=dict2str(info)))
            for f in fs:
                kf = proot/f
                l = 'l' if kf.is_symlink() else '_'
                info = {'size':kf.stat().st_size,'st_mtime':int(kf.stat().st_mtime)}
                fp.write(fmt.format(zonename='_',ftype='f',is_link=l,data=f,info=dict2str(info)))
        fp.close()
    def read(self):
        fp = open(self.database)
        result = {}

        for it in fp:
            kk = it.split('//{')
            i = kk[0]
            ztype = i[0]
            if ztype == '#':
                continue 
            elif ztype == 'z':
                files = list()
                zone_name = Path(i[6:])
                dt = kk[1].rstrip()[:-1]
                dd = dict([i.split(':') for i in dt.split(',')])
                dd['files'] = files
                dd['attribute'] = i[:5]
                self.file_info[str(zone_name)] = dd
                result[i[6:]] = dd
            elif ztype == '_':
                dt = kk[1].rstrip()[:-1]
                dd = dict([i.split(':') for i in dt.split(',')])
                dd['attribute'] = i[:5]
                self.file_info[str(zone_name/i[6:])] = dd
                files.append((i[:5],i[6:],dd))
        self.database_data = result 
        return self.database_data
    def write(self,oname=None):
        if oname is None:
            oname = self.database
        fp = open(oname,'w')
        fmt = '{attribute}:{data}//{{{info}}}\n'
        fp.write('''#{zonename}{ftype}{is_link}__:{data}//{dict_info}\n''')

        for k,v in self.database_data.items():
            if v is None:
                continue
            stat = ','.join([f'{kk}:{val}' for kk,val in v.items() if kk!='files' and kk!='attribute'])
            fp.write(fmt.format(attribute=v['attribute'],data=k,info=stat))
            for att,f,dt in v['files']:
                stat=','.join([f'{kk}:{val}' for kk,val in dt.items() if kk!='attribute'])
                fp.write(fmt.format(attribute=att,data=f,info=stat))
    def _update_key(self,zdd,xdb):
        if zdd in xdb:
            return 
        p = Path(zdd)
        files = list()
        xdb[zdd] = {'size':0,'st_mtime':int(p.stat().st_mtime),'attribute':'zd___','files':files}
        for i in p.glob('*'):
            l = 'l' if i.is_symlink() else '_'
            f = 'f' if i.is_file() else 'd'
            stat = i.stat()
            att = f'_{f}{l}__'
            info = {'size':stat.st_size,'st_mtime':int(stat.st_mtime)}
            ss = att,i.name,info
            files.append(ss)

            pdd = f'./{i}'
            if f == 'd':
                self._update_key(pdd,xdb)
    def update(self):
        rr = dict()
        database_data = self.database_data
        for k,v in database_data.items():
            p = Path(k)
            if p.is_dir():
                new_mtime = p.stat().st_mtime
                if new_mtime > int(v['st_mtime']):
                    files = list()
                    v_names = {ii[1]:ii for ii in  v['files']}
                    database_data[k] = {'size':0,'st_mtime':int(new_mtime),'attribute':'zd___','files':files}
                    for i in p.glob('*'):
                        namet = i.name
                        if namet in v_names:
                            files.append(v_names[namet])
                        else:
                            l = 'l' if i.is_symlink() else '_'
                            f = 'f' if i.is_file() else 'd'
                            stat = i.stat()
                            att = f'_{f}{l}__'
                            info = {'size':stat.st_size,'st_mtime':int(stat.st_mtime)}
                            ss = att,namet,info
                            files.append(ss)

                            pdd = f'./{i}'
                            if f == 'd' and pdd not in database_data:
                                self._update_key(pdd,rr)
            else:
                database_data[k] = None
        database_data.update(rr)


    def find(self,find_str):
        if self.database_data is None:
            self.read()
        find_str = find_str.lower()
        fmt = '{} -> {}'
        db = self.database_data
        for zone_name in db:
            rootp = Path(zone_name)
            for ftt in db[zone_name]['files']:
                attri,i = ftt[:2]
                rp = rootp / i 
                if attri[1] == 'f' and attri[2] == '_':
                    t = str(yxsFile(i).decode_filename())
                    if t.lower().find(find_str) != -1:
                        tname = rootp / t
                        iname = rootp / i
                        if t != i:
                            tname = [yxsFile(i).decode_filename().name for i in tname.parts]
                            tname = os.sep.join(tname)
                            print(fmt.format(tname,iname))
                        else:
                            print(iname)

class yxsFile:
    t = ['.jpg','.jpeg','.png','.webp','.gif','.bmp']
    jpg_suffix = set(t+[i.upper() for i in t])
    XS_SUFFIX = set(('.xsd','.xsf','.mpxs','.jpxs'))
    def __init__(self,filename,workdir=None,passwd=None):
        if passwd is None:
            passwd = encrypt.get_default_passwd()
        self.filename = Path(str(filename))
        self.title_size = 2048
        self.passwd = passwd
        self.file_suffix = '.mpxs','.jpxs','.xsf'
        if self.filename.suffix in self.file_suffix:
            self.is_pureFile = False
        else:
            self.is_pureFile = True
        self.workdir = workdir 
        if workdir is None:
            self.workdir = self.filename.parent
    def to_pureFile(self,to_dir = None):
        if not self.is_pureFile:
            fp   = open(self.filename,'rb')
            title = fp.read(self.title_size).replace(bytes([0]),b'')
            new_name = self.filename.parent/title.decode()
            if to_dir:
                new_name = Path(to_dir)/new_name.name
            while new_name.exists():
                new_name = new_name.parent/('new_'+new_name.name)
            tempfn = new_name.with_suffix('.temp_YXS')
            fpp = open(tempfn,'wb')
            t = fp.read(1024*1024*8)
            while t != b'':
                fpp.write(t)
                t = fp.read(1024*1024*32)
            fpp.close()
            os.rename(tempfn,new_name)
        else: 
            new_name = None 
        return new_name

    def to_yxsFile(self,to_dir=None):
        if self.is_pureFile:
            name = self.filename.name.encode()
            yxs_filenme = self.encode_filename()
            newname_stem = self.filename.stem
            ii = 1
            while yxs_filenme.is_file():
                newname = self.filename.parent / (newname_stem+f'_{ii}{self.filename.suffix}')
                yxs_filenme = self.encode_filename(newname)
                ii += 1
            if to_dir:
                yxs_filenme = Path(to_dir)/yxs_filenme.name
            tempfn = yxs_filenme.with_suffix('.temp_YXS')
            fpxs = open(tempfn,'wb')
            fp   = open(self.filename,'rb')
            tbytes = bytes([0]*(self.title_size-len(name)))
            t = name+tbytes
            while t != b'':
                fpxs.write(t)
                t = fp.read(1024*1024*32)
            fpxs.close()
            os.rename(tempfn,yxs_filenme)
        else:
            yxs_filenme = None 
        return yxs_filenme

    def play_video(self):
        webbrowser.open('http://0.0.0.0:9090/'+self.filename.name+'?player=default')
        os.chdir(self.filename.parent)
        flask_server.main(9090)
    def view_image(self):
        pass
    def encode_filename(self,filename=None):
        if not filename:
            filename = self.filename
        else:
            filename = Path(filename)
        name = filename.name
        suffix = filename.suffix 
        if suffix in self.XS_SUFFIX:
            return filename
        if filename.is_dir():
            mysuffix = '.xsd'
        else:
            mysuffix = '.xsf'
        if suffix in self.jpg_suffix:
            mysuffix = '.jpxs'
            name = filename.stem
        if suffix == '.mp4':
            mysuffix = '.mpxs'
            name = filename.stem
        length= len(name)
        while True:
            spname = encrypt.spencode(name[:length].encode(),self.passwd,str_set=ENCODE_CODE).decode()
            if len(spname)< 250:
                break 
            else:
                length = int(length / 2)
        spname = spname + mysuffix 
        return filename.parent/ spname
    def decode_filename(self):
        suffix = self.filename.suffix 
        if suffix in self.XS_SUFFIX:
            stem = self.filename.stem
            try:
                spname = encrypt.spdecode(stem.encode(),self.passwd,str_set=ENCODE_CODE).decode()
            except:
                print(stem)
                exit()
            if suffix == '.mpxs':
                mysuffix = '.mp4'
            elif suffix == '.jpxs':
                mysuffix = '.jpg'
            else: 
                mysuffix = ''

            return self.filename.parent / (spname+mysuffix)
        else:
            return self.filename

    def get_md5(self):
        fp = open(self.filename,'rb')
        if not self.is_pureFile:
            fp.read(self.title_size)
        md5 = hashlib.md5()
        while True:
            t = fp.read(1024*1024*4)
            if t == b'':
                break
            md5.update(t)
        return md5
def listdir(dirname):
    result = []
    for i in os.listdir(dirname):
        t = str(yxsFile(i).decode_filename())
        result.append((t,len(t),i))
    result.sort(key = lambda x:x[0])
    max_length = max([i[1] for i in result])
    f = '{:'+str(max_length+2)+'s}-> {}'
    for dname,_,ename in result:

        if dname != ename:
            print(f.format(dname,ename))
        else:
            print(dname)
class SPath(PosixPath):
    global_xdb = {}
    def glob(self,ftype):
        xdb_key,xp = self.get_xdb_ps()
        xdb_data = self.global_xdb[xdb_key].database_data
        parent = './'+str(xp)
        if parent == './.':
            parent = './'
        pp = Path(xdb_key) / parent
        if parent not in xdb_data:
            return []
        if ftype == '*':
            return [SPath(pp/ft[1],parent=self) for ft in xdb_data[parent]['files']]
        else:
            rr = []
            kre = re.compile(ftype.replace('*','.*'))
            for ft in xdb_data[parent]['files']:
                if kre.match(ft[1]):
                    rr.append(SPath(pp/ft[1],parent=self))
            return rr

    def is_file(self):
        if not self.global_xdb:
            return super().is_file()
        rr = self._is_core('f',1)
        return rr
    def is_dir(self):
        if not self.global_xdb:
            return super().is_dir()
        rr = self._is_core('d',1)
        return rr

    def is_file_abs(self):
        return super().is_file()
    def is_dir_abs(self):
        return super().is_dir()

    def is_symlink(self):
        if not self.global_xdb:
            return super().is_symlink()
        rr = self._is_core('l',2)
        return rr
    def _is_core(self,ftype,ind):
        xdb_key,xp = self.get_xdb_ps()
        if xdb_key is None:
            return False
        xdb_data = self.global_xdb[xdb_key].database_data
        parent = './'+str(xp.parent )
        if parent == './.':
            parent = './'
        fname = xp.name 
        if parent not in xdb_data:
            return False 
        else:
            for ft in xdb_data[parent]['files']:
                if ft[0][ind] == ftype and ft[1] == fname:
                    return True 
            return False

    def get_xdb_ps(self):
        abspath_str = str(self.absolute())
        for key in self.global_xdb.keys():
            if abspath_str.startswith(key):
                return key,Path(abspath_str[len(key)+1:])
        return None,None
    def add_xdb(self,xdb_name):
        xdb_key = str(Path(xdb_name).absolute().parent)
        if xdb_key in self.global_xdb:
            return None 
        else:
            self.global_xdb[xdb_key] = file_database(database_name=xdb_name)
            self.global_xdb[xdb_key].read() 
            return True
    def add_path(self):
        xdb_key,xp = self.get_xdb_ps()
        xdb_data = self.global_xdb[xdb_key].database_data
        parent = './'+str(xp.parent )
        if parent == './.':
            parent = './'
        fname = xp.name 
        xdb_data[parent]['files']

        

def find_file(find_str):
    find_str = find_str.lower()
    db = file_database()
    if not db.database.exists():
        db.create()
    db.find(find_str)

@click.command()
@click.argument('args',nargs=-1)
@click.option('--filename','-i',default=None,help="输入文件名或者文件夹名称")
@click.option('--pure','-p',default=False,is_flag=True,help="转化为原始文件")
@click.option('--xfile','-x',default=False,is_flag=True,help="加密该文件")
@click.option('--find','-f',default='',help="查找文件")
@click.option('--update_db','-u',default=False,is_flag=True,help="更新文件名数据库")
@click.option('--db',default=None,help="设置数据库名称")
@click.option('--decode','-d',default=False,is_flag=True,help="单独显示原文件名,不转码文件,文件名后缀改为._tt")
@click.option('--encode','-e',default=False,is_flag=True,help="加密显示文件名(._tt)")
@click.option('--delete',default=False,is_flag=True,help="删除原始文件")
def main(args=None,filename=None,pure=False,xfile=False,find=None,decode=False,encode=False,update_db=False,db=None,delete=False):
    key_option = 0
    global_dict['db'] = db
    if update_db:
        md = file_database()
        if md.database.is_file():
            md.read()
            md.update()
            md.write()
        else:
            md.create()
    if find:
        key_option += 1
        find_file(find)
    if decode:
        key_option += 1
        for i in os.listdir('./'):
            try:
                if not i.endswith('._tt'):
                    df = yxsFile(i).decode_filename().name
                    if df != i:
                        suffix = Path(i).suffix
                        os.rename(i,df+suffix+'._tt')
                        time.sleep(0.01)
            except:
                print('error file',i)
    if encode:
        key_option += 1
        for i in os.listdir('./'):
            try:
                if i.endswith('._tt'):
                    istem = i[:-4]
                    suffix = Path(istem).suffix
                    ef = yxsFile(istem[:-len(suffix)]).encode_filename().name
                    os.rename(i,Path(ef).with_suffix(suffix))
                    time.sleep(0.01)
            except:
                print('error file',i)
    
    filename_list = list()
    if key_option == 0:
        if filename:
            filename_list = [filename,]
            if Path(filename).is_dir():
                filename_list = [Path(root)/f for root,_,fs in os.walk(filename) for f in fs]
        if args:
            filename_list.extend(args)
        if not filename and not args:
            listdir('./')
        
    for fn in filename_list:
        if pure:
            pf = yxsFile(fn)
            pf.to_pureFile()
            print(pf.decode_filename())
        elif xfile:
            pf = yxsFile(fn)
            pf.to_yxsFile()
            print(fn,'->',pf.decode_filename())
        else:
            pf = yxsFile(fn)
            suffix = Path(fn).suffix
            if suffix == '.mpxs':
                pf.play_video()
        if delete:
            os.remove(fn)
if __name__=='__main__':
    main()