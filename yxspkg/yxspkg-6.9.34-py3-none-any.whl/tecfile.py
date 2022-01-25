
import numpy as np
from os.path import getsize
import pandas as pd
import re
from . import plot3d
from . import numeca_file

__version__='1.12'
__author__='Blacksong'
class _zone_data(dict):
    plot_package = {}
    def __init__(self,*d,**dd):
        super().__init__(*d,**dd)
        self.Elements = None
        self.tec_cellcentered=False

    def rename(self,old,new):
        if old == new:return
        self[new]=self[old]
        self.pop(old)
    def DataFrame(self,center=False,columns=None):
        ''''将数据转化为DataFrame格式，
        center:是否将数据都转化为中心格式
        '''
        if columns is None:
            columns = self.keys()
        dic = {i:self[i] if not center else self.center_value(i) for i in columns}
        return pd.DataFrame(dic)

    def fit_mesh(self,zone_data,var,X='x',Y='y',Z=None):
        '''
        将zong_data中的变量var,根据Elements适应,调整var中数据的存储顺序
        X,Y,Z：表述存储网格坐标的变量名
        '''
        if Z:
            mesh = [X,Y,Z]
        else:
            mesh = [X,Y]
        assert self.Elements.shape == zone_data.Elements.shape
        m1 = {i:self.center_value(i) for i in mesh}
        m2 = {i:zone_data.center_value(i) for i in mesh}
        m2['__var'] = var
        m1 = pd.DataFrame(m1)
        m2 = pd.DataFrame(m2)
        m2.index = m1.index
        m1.sort_values(mesh, inplace=True)
        m2.sort_values(mesh, inplace=True)
        
        m1['__var'] = m2['__var'].values
        m1.sort_index(inplace=True)
        return m1['__var'].values
    def set_data(self,names,values,attribute):
        self.names=names
        self.data=values
        self.attribute=attribute
        for i,v in zip(names,values):
            self[i]=v
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:
            if self.attribute == 'fluent_prof':
                return self.data[:,k]
    def is_centered(self,name): #判断一个tecplot变量是不是centered变量
        nodes = int(self.attribute['Nodes'])
        if len(self[name])==nodes:
            return False
        else:
            return True

    def center_value(self,name):# 获取tecplot文件中某个变量在cell中心的值，即求出各个节点的平均值
        elements = self.Elements - 1
        n = elements.shape[1]
        elements_flat = elements.flatten()
        data = self[name][elements_flat].reshape((-1,n))
        return data.mean(1)
    def __add__(self,other):#重载加法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] + other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __sub__(self,other):#重载减法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] - other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __mul__(self,other):#重载乘法运算
        z = class_read()
        names = list(self.keys())
        if isinstance(other,_zone_data):
            values = [self[i] * other[i] for i in names]
        else:
            values = [self[i] * other for i in names]
        z.update(zip(names,values))
        return z
    def contour_plot(self,x_name,y_name,z_name,triangles=None,set_mask = None):
        if not self.plot_package:
            import matplotlib.tri as tri
            import matplotlib.pyplot as plt
            self.plot_package['tri'] = tri
            self.plot_package['plt'] = plt
        else:
            tri = self.plot_package['tri'] 
            plt = self.plot_package['plt'] 
        self.plt = plt
        if isinstance(x_name,str):
            x = self[x_name]
        else:
            x = x_name
        if isinstance(y_name,str):
            y = self[y_name]
        else:
            y = y_name
        if isinstance(z_name,str):
            z = self[z_name]
        else:
            z = z_name

        triang = tri.Triangulation(x, y, triangles=triangles)
        if set_mask is not None:
            set_mask(triang)
        fig1, ax1 = plt.subplots()
        ax1.set_aspect('equal')
        tpc = ax1.tripcolor(triang, z,shading='gouraud',cmap=plt.get_cmap('jet'))
        fig1.colorbar(tpc)
        self.ax = ax1
        self.fig = fig1
class class_read(dict):
    def __init__(self,filename=None,filetype=None,read_grid=True,**kargs):
        if filename is None:return
        self.fp=open(filename,'r')
        self.default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv'}
        self.data=None
        self.read_grid = read_grid
        if not filetype:
            key=filename.split('.')[-1].lower()
            if key=='out':key=self.__recognize_out(self.fp)
            self.filetype=self.default_filetypes[key]
        else:
            self.filetype=filetype
        self.filesize=getsize(filename)
        if self.filetype=='tecplot_dat':
            self._read_dat()
        elif self.filetype=='fluent_prof':
            self._read_prof()
        elif self.filetype=='fluent_residual_out':
            self._read_out()
        elif self.filetype=='fluent_monitor_out':
            self.__read_out2()
        elif self.filetype=='csv':
            self.__read_csv(filename)

        self.fp.close()
    
    def __read_csv(self,filename):
        title=self.fp.readline()
        tmp=np.loadtxt(self.fp,dtype='float64',delimiter=',')
        title=title.strip().split(',')
        for i,j in enumerate(title):
            self[j]=tmp[:,i]
        self.data=tmp
    def __recognize_out(self,fp):
        fp.readline()
        t=fp.readline()
        t=t.split()
        key='out'
        if t:
            if t[0]=='"Iteration"':
                key='out2'
        fp.seek(0,0)
        return key
    def __read_out2(self):
        self.fp.readline()
        t=self.fp.readline()
        t=t.lstrip()[11:].strip()[1:-1]
        d=self.fp.read().encode().strip()
        d=d.split(b'\n')
        d=[tuple(i.split()) for i in d]
        x=np.array(d,dtype=np.dtype({'names':["Iteration",t],'formats':['int32','float64']}))
        self["Iteration"]=x['Iteration']
        self[t]=x[t]
        self.data=x
    def _read_out(self):#fluent residual file
        items=[]
        items_n=0
        data=[]
        iter_pre='0'
        time_index=False
        for i in self.fp:
            if i[:7]=='  iter ':
                if items_n!=0:continue
                j=i.strip().split()
                items.extend(j)
                if items[-1]=='time/iter':
                    items.pop()
                    items.extend(('time','iter_step'))
                    time_index=True
                items_n=len(items)
            if items_n==0:continue
            else:
                j=i.split()
                if len(j)==items_n:
                    if j[0].isdigit():
                        if j[0]==iter_pre:continue
                        iter_pre=j[0]
                        if time_index:j.pop(-2)
                        data.append(tuple(j))
        if time_index:items.pop(-2)
        a=np.array(data,dtype=np.dtype({'names':items,'formats':['i']+['f']*(len(items)-2)+['i']}))
        for i,k in enumerate(items):
            self[k]=a[k]
        self.data=a
    def _read_prof(self):
        fp=self.fp
        d=fp.read()
        d=d.replace('\r','')
        d=d.split('((')
        d.pop(0)
        data=[]
        def read(x):
            x=x.split('(')
            title=x[0].split()[0]
            x.pop(0)
            data=[]
            name=[]
            ii=0
            for i in x:
                c=i.split('\n')
                ii+=1
                name.append(c[0])
                data.append(c[1:-2])
            data[-1].pop()
            values=np.array(data,dtype='float32')
            if len(values)!=len(name):return False
            t=_zone_data()
            t.set_data(name,values,self.filetype)
            return title,t
        for i in d:
            k,v=read(i)
            self[k]=v
    
    def _parse_variables(self,string_list):#解析tecplot文件的变量名有哪些
        return re.findall('"([^"]*)"',''.join(string_list))
    @staticmethod
    def _parse_strlist(kstring):
        a=[]
        if kstring:
            for i in kstring[1:-1].split(','):
                if i.find('-')!=-1:
                    start,end = i.split('-')
                    a.extend(range(int(start),int(end)+1))
                else:
                    a.append(int(i))
        a.sort()
        return a
    def _parse_zone_type(self,string_list):# 解析tecplot文件
        s=' '.join(string_list)
        attri = dict(re.findall('([^ ]+)=([^ ,=]+)',s))
        attri.update(dict(re.findall('([^ ]+)="([^"]+)"',s)))
        k = re.findall('VARLOCATION=\(([^=]+)=CELLCENTERED\)',s)#检查是否有cellcentered变量
        auxdata = re.findall(' AUXDATA [^ ]*',s)
        if auxdata:
            attri['AUXDATA'] = '\n'.join(auxdata)
        attri['CELLCENTERED'] = self._parse_strlist(k[0])
        return attri
        
    def _read_dat(self):#解析tecplot_dat数据格式
        fp=self.fp
        title = fp.readline()
        assert title.lstrip().startswith('TITLE')!=-1#查看文件开头是否是TITLE

        string = fp.readline().strip()
        assert string.startswith('VARIABLES') #查看文件第二行开头是否是VARIABLES

        string_list=[string,]#获取包含所有变量名的字符串
        while True:
            i = fp.readline()
            if i=='':
                break
            i=i.strip()
            if not i.startswith('"'):
                string = i
                break
            else:
                string_list.append(i)
        self._variables=self._parse_variables(string_list) #对字符串进行解析得到变量名
        while True:
            if not string:
                string = fp.readline()
                if not string:
                    break
            string_list=[string,]#获取包含zone name， element， nodes，zonetype, datapacking的字段
            while True:
                i = fp.readline()
                if i=='':
                    break
                i=i.strip()
                if i.startswith("DT=("):
                    string = i 
                    break
                else:
                    string_list.append(i)
            self._tecplot_attribute=self._parse_zone_type(string_list) #获取包含zone name， element， nodes，zonetype, datapacking 返回形式为字典
            string = string[len('DT=('):-1].strip().split()
            self._DT=string  #保存每个变量的类型
            assert len(self._variables) == len(string)
            if self._tecplot_attribute['DATAPACKING']=='BLOCK':
                self._parse_block()
            if self._tecplot_attribute['DATAPACKING'] == 'POINT':
                self._parse_point()
            string = None
    def _read_numbers(self,fp,nums):#读取文件一定数目的 数据
        data = fp.readline().split()
        n = len(data)
        strings = [fp.readline() for _ in range(int(nums/n)-1)]
        data.extend(''.join(strings).split())
        nn = nums - len(data)
        assert nn>=0
        if nn>0:
            while True:
                i = fp.readline()
                if i=='':
                    break
                data.extend(i.split())
                if len(data) == nums:
                    break 
        return data
    def _parse_Elements(self,zonedata):#解析tecplot的Element
        elements = int(self._tecplot_attribute['Elements'])
        data_elements = self.fp.readline().split()
        num_points = len(data_elements)
        data = self._read_numbers(self.fp,num_points*(elements-1))
        if self.read_grid:
            data_elements += data
            zonedata.Elements = np.array(data_elements,dtype=np.int).reshape((-1,num_points))
    def _get_passivevarslist(self):
        # 获取PASSIVEVARLIST
        pos = self.fp.tell()
        passive_line = self.fp.readline().strip()
        if passive_line.startswith('PASSIVEVARLIST'):
            k = passive_line[passive_line.find('=')+1:]
            passivevarlist = self._parse_strlist(k)
        else:
            self.fp.seek(pos,0)
            passivevarlist = []
        return passivevarlist
    def _parse_block(self,isBlock=True):#解析tecplot block方式存储的数据
        cellcentered = self._tecplot_attribute['CELLCENTERED']
        variables = self._variables
        if self._tecplot_attribute['ZONETYPE'].lower() == 'ordered':
            i = int(self._tecplot_attribute['I'])
            j = int(self._tecplot_attribute['J'])
            k = int(self._tecplot_attribute.get('K',1))
            nodes = i*j*k 
            elements = max(1,i-1)*max(j-1,1)*max(k-1,1)
            isElements = False
        else:
            isElements = True
            nodes,elements = int(self._tecplot_attribute['Nodes']),int(self._tecplot_attribute['Elements'])
        value_list = []
        passivevarlist = self._get_passivevarslist()
        for i in range(len(variables)):
            if i+1 in cellcentered:
                nums = elements 
            else:
                nums = nodes
            if i+1 not in passivevarlist:
                data = self._read_numbers(self.fp,nums)
            else: 
                data = []
            value_list.append( np.array(data,dtype = 'float64'))
        zonedata = _zone_data()
        zonedata.set_data(variables,value_list,self._tecplot_attribute)
        self[self._tecplot_attribute['T']] = zonedata

        if isElements:
            self._parse_Elements(zonedata)


    def _parse_point(self,isElements=True,isBlock=False):
        variables,nodes,elements = self._variables,int(self._tecplot_attribute['Nodes']),int(self._tecplot_attribute['Elements'])
        nn=nodes*len(variables)
        data = self._read_numbers(self.fp,nn)
        if isBlock:
            data = np.array(data,dtype = 'float').reshape((len(variables),-1))
        else:
            data = np.array(data,dtype = 'float').reshape((-1,len(variables))).T
        
        zonedata = _zone_data()  #设置zonedata数据
        zonedata.set_data(self._variables,data,self._tecplot_attribute) 
        self[self._tecplot_attribute['T']] = zonedata
        
        if isElements:
            #添加Elements的属性
            self._parse_Elements(zonedata)
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:return self.data[k]
    def enable_short_name(self):#启用简单名 即将名字命名为 原来名字的第一个单词
        for i in list(self.keys()):
            for j in list(self[i].keys()):
                self[i].rename(j,j.split()[0])
            self.rename(i,i.split()[0])
    def rename(self,old,new):
        if old == new:return
        self[new]=self[old]
        self.pop(old)
    def write(self,filename):
        write(filename,self)

    def __add__(self,other):#重载加法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] + other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __sub__(self,other):#重载减法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] - other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __mul__(self,other):#重载乘法运算
        z = class_read()
        names = list(self.keys())
        if isinstance(other,class_read):
            values = [self[i] * other[i] for i in names]
        else:
            values = [self[i] * other for i in names]
        z.update(zip(names,values))
        return z
class data_ndarray(np.ndarray):
    def write(self,filename):
        write(filename,self)
    def setfiletype(self,filetype):
        self.filetype=filetype
def read(filename,filetype='',read_grid=True,**kargs):
    '''
    支持的文件格式： suffix (filetype)
    .szplt  (tecplot)
    .txt    (numpy)
    .g   (plot3d)
    .q 
    .xyz 
    .fmt
    .mf    (numeca)
    .inp   (scfd)
    .prout
    .prof (fluent_prof) 
    .dat  (tecplot_dat) 
    .out (fluent_residual_out)
    .out2 (fluent_monitor_out) 
    .csv   (csv) 
    .xs3d  (SCFDui 使用的网格格式)
    .cgns  (CGNS File)
    '''
    filename = str(filename)
    ext=filename.split('.')[-1].lower()
    filetype = filetype.lower()
    if ext=='txt' and not filetype:
        data = [i.split() for i in open(filename) if i.lstrip() and i.lstrip()[0]!='#']
        data=np.array(data,dtype='float64')
        data=data_ndarray(data.shape,dtype=data.dtype,buffer=data.data)
        data.setfiletype('txt')

    elif (ext=='szplt' and not filetype) or filetype=='szplt':
        if 'pytecio' not in globals():
            from . import pytecio 
            global pytecio 
        data = pytecio.read(filename)
    elif (ext in ['g','q','xyz','fmt','xs3d'] and not filetype) or filetype == 'plot3d':
        return plot3d.read(filename,**kargs)
    elif ext in ('mf',) and not filetype:
        return numeca_file.read_mf(filename)
    elif (ext in ('inp','prout') and not filetype) or filetype == 'scfd':
        if 'scfd_io' not in globals():
            from cfl3d_post import scfd_io
            global scfd_io
        return scfd_io.read(filename)
    elif ext == 'cgns' or filetype == 'cgns':
        if 'cgns' not in globals():
            from . import cgns
            global cgns
        return cgns.read(filename)
    else:
        data=class_read(filename,filetype=filetype,read_grid=read_grid)
    return data
class write:
    def __init__(self,filename,data,filetype=None,**kargs):
        default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv','txt':'txt','fmt':'plot3d','g':'plot3d','q':'plot3d','xyz':'plot3d',
        'szplt':'szplt'}
        self.kargs = kargs
        filename = str(filename)
        ext=filename.split('.')[-1].lower()
        if filetype is None:
            filetype=default_filetypes.get(ext,None)
        if filetype is None:
            filetype=data.filetype

        if filetype=='fluent_prof':
            self.__write_prof(filename,data)
        elif filetype=='tecplot_dat':
            self.__write_dat(filename,data)
        elif filetype=='csv':
            self.__write_csv(filename,data)
        elif filetype=='fluent_monitor_out':
            self.__write_out2(filename,data)
        elif filetype=='fluent_residual_out':
            self.__write_out(filename,data)
        elif filetype=='txt':
            np.savetxt(filename,data)
        elif filetype=='plot3d':
            self.__write_plot3d(filename,data)
        elif filetype=='szplt':
            self.__write_szplt(filename,data)
        else:
            raise EOFError('file type error!')
    def __write_szplt(self,filename,data):
        verbose = self.kargs.get('verbose',False)
        if 'pytecio' not in globals():
            from . import pytecio 
            global pytecio 
        pytecio.write(filename,data,verbose=verbose)
    def __write_plot3d(self,filename,data):
        plot3d.write(filename,data)

    def __write_out(self,filename,data):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,'  ',title_format='',specified_format=' %d',specified_titles=['iter'],other_format='%.8e')
        fp.close()
    def __write_out2(self,filename,data):
        fp=open(filename,'w')
        value=[i for i in data.keys() if i!='Iteration'][0]
        fp.write('"Convergence history of %s"\n' % value)
        self.__write_delimiter(data,fp,' ',title_format='"',specified_format='%d',specified_titles=['Iteration'])
        fp.close()
    def __write_csv(self,filename,data):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,',')
        fp.close()
    def __write_delimiter(self,data,fp,delimiter,title_format='',specified_format='',specified_titles=[],other_format='%.15e'):
        other_titles=[i for i in data.keys() if i not in specified_titles]
        title=specified_titles+other_titles
        title_w=[title_format+i+title_format for i in title]
        fp.write(delimiter.join(title_w)+'\n')
        s=np.vstack([data[i] for i in title]).T
        data_format=specified_format+delimiter+delimiter.join([other_format]*len(other_titles))+'\n'
        for i in s:
            fp.write(data_format % tuple(i))
    def __write_prof(self,filename,data):
        fp=open(filename,'wb')
        for i in data.keys():
            keys=list(data[i].keys())
            keys.sort()
            keys.sort(key=lambda x:len(x))
            n=len(data[i][keys[0]])
            fs='(('+i+' point '+str(n)+')\n'
            fp.write(fs.encode())
            for k in keys:
                fs='('+k+'\n'
                fp.write(fs.encode())
                [fp.write((str(j)+'\n').encode()) for j in data[i][k]]
                fp.write(')\n'.encode())
            fp.write(')\n'.encode())
    def __write_dat(self,filename,data):#写入tecplot dat文件，目前只支持写入DATAPACKING=POINT类型的数据DATAPACKING=BLOCK类型的数据也会被改写为POINT类型
        fp = open(filename,'w')
        fp.write('TITLE  = "Python Write"\n')
        zones = list(data.keys())  #获取所有zone的名字
        variables = list(data[zones[0]].keys())#获取变量名
        fp.write('VARIABLES = ')
        fp.writelines(['"{}"\n'.format(i) for i in variables])
        for i in zones:
            zonedata = data[i]
            z = zonedata.attribute
            nodes, elements = int(z['Nodes']), int(z['Elements'])
            fp.write('ZONE T="{}"\n'.format(i))
            fp.write(' STRANDID={}, SOLUTIONTIME={}\n'.format(z.get('STRANDID',1),z.get('SOLUTIONTIME',0)))
            fp.write(' Nodes={0}, Elements={1}, ZONETYPE={2}\n'.format(nodes, elements, z['ZONETYPE']))
            if z['DATAPACKING'] == 'POINT':
                fp.write('DATAPACKING=POINT\n')
                if z.get('AUXDATA') is not None:
                    fp.write(z.get('AUXDATA')+'\n')
                fp.write('DT=('+'SINGLE '*len(variables)+')\n')
                fs = ' {}'*len(variables)+'\n'
                for value in zip(*([zonedata[j] for j in variables])):
                    fp.write(fs.format(*value))
                fs = ' {}'*len(zonedata.Elements[0])+'\n'
            else:
                fp.write(' DATAPACKING=BLOCK\n')
                cellcentered = [str(i+1) for i,v in enumerate(variables) if zonedata.is_centered(v)]
                if cellcentered:
                    s =','.join(cellcentered)
                    fs = ' VARLOCATION=([{}]=CELLCENTERED)\n'.format(s)
                    fp.write(fs)
                if z.get('AUXDATA') is not None:
                    fp.write(z.get('AUXDATA')+'\n')
                fp.write('DT=('+'SINGLE '*len(variables)+')\n')
                ofs = ' {}'*5+'\n'
                for var in variables:
                    
                    value = zonedata[var]
                    
                    for i in range(5,len(value)+1,5):
                        
                        fp.write(ofs.format(*value[i-5:i]))

                    leave = len(value) % 5

                    if leave != 0:
                        fs = ' {}'*leave+'\n'
                        fp.write(fs.format(*value[-leave:]))
                

            if zonedata.Elements is not None:
                fs = ' {}'*len(zonedata.Elements[0])+'\n'
                for i in zonedata.Elements:
                    fp.write(fs.format(*i))

if __name__=='__main__':
    pass