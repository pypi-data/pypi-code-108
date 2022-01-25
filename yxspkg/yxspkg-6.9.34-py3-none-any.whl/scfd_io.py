from functools import wraps
import re
import json
from pathlib import Path
def stop(fun):
    @wraps(fun)
    def function(*args):
        fp = args[0].fp
        pos0 = fp.tell()
        t = fp.readline().strip()
        if t == '':
            return False
        elif t.lower() == 'iyxs':
            fp.seek(pos0,0)
            return None
        return fun(*args)
    return function 
class read_inp(dict):
    def __init__(self,inpfile):
        self.fp = open(inpfile)
        self.one2oneData = None
        self.periodicData= None
        self.boundaryData= None
        self.start_read() 
    def start_read(self):
        fp = self.fp
        fp.readline()
        self['files'] = [fp.readline().strip() for i in range(13)]
        #读取空行 
        s = fp.readline()
        key_words = []
        if s.startswith('>'):
            while True:
                s = fp.readline()
                if s.startswith('<'):
                    fp.readline()
                    break
                else: 
                    key_words.append(s.split())
        self['key_words'] = key_words
        for key in write.title_list1[:4]:
            self._read_one_line(key.split()[0])
        self.ngrid = abs(int(self['ngrid'][0]))
        for key in write.title_list1[4:11]:
            self._read_ngrid_lines(key.split()[0].split('(')[0])
        keys = ['I0','IE','J0','JE','K0','KE']
        for key,key_n in zip(keys,range(1,7)):
            self._read_boundaryData(key,key_n)
        keys = ['mseq','issc']
        for key in keys:
            self._read_one_line(key)
        keys = ['ncyc','mit1']
        for key in keys:
            self._read_one_line(key,self['mseq'][0])
        self._read_one2oneData()
        self._read_patchData()
        self._read_output()
        #read movie
        fp.readline()
        self['movie'] = int(fp.readline())
        for f in [self._read_print,self._read_control,self._read_trans,
                self._read_rotate, self._read_dynamic_patch, self._read_iyxs]:
            if f() is False:
                return
    def _read_one_line(self,key,nline=1):
        nline = int(nline)
        self.fp.readline()
        if nline == 1:
            self[key] = [float(i) for i in self.fp.readline().split()]
        else: 
            self[key] = [[float(i) for i in self.fp.readline().split()] for _ in range(nline)]
    def _read_ngrid_lines(self,key):
        self.fp.readline()
        self[key] = [[float(l) for l in self.fp.readline().split()] for _ in range(self.ngrid)]
    def _read_boundaryData(self,key,key_n):
        fp = self.fp 
        fp.readline()
        result = list()
        t = self['grid']
        nbc = sum([t[i][key_n] for i in range(self.ngrid)])
        for ibc in range(int(nbc)):
            ts = [int(i) for i in fp.readline().split()]
            if ts[-1] == 0:
                opt_data = None
            else:
                fp.readline()
                opt_data = fp.readline().split()
            result.append([ts,opt_data])
        self[key] = result
    def _read_one2oneData(self):
        fp = self.fp 
        fp.readline()
        fp.readline()
        nbli = int(fp.readline())
        fp.readline()
        t1 = [[int(i) for i in fp.readline().split()] for _ in range(nbli)]
        fp.readline()
        t2 = [[int(i) for i in fp.readline().split()] for _ in range(nbli)]
        self['one2oneData'] = t1,t2
    def _read_patchData(self):
        self.fp.readline()
        self.fp.readline()
        self['patchFile'] = int(self.fp.readline())
    def _read_output(self):
        fp = self.fp
        fp.readline()
        fp.readline()
        nplot = abs(int(self['ngrid'][1]))
        self['output'] = [[int(i) for i in fp.readline().split()] for _ in range(nplot)] 
    def _read_print(self):
        [self.fp.readline() for i in range(2)]
        print_out = []
        while True:
            t = self.fp.readline()
            if t.lstrip()[0].isalpha():
                break 
            print_out.append([int(i) for i in t.split()])
        self['print_out'] = print_out
    def _read_control(self):
        [self.fp.readline() for i in range(1)]
        ncs = int(self.fp.readline())
        self.fp.readline() 
        if ncs > 0:
            self['control_surface'] = [[int(i) for i in self.fp.readline().split()] for _ in range(ncs)]
        else: 
            self['control_surface'] = []
    @stop  #stop 会读取一行文件
    def _read_trans(self):
        fp = self.fp 
        fp.readline()
        assert int(fp.readline()) == 0
        [fp.readline() for _ in range(3)]
    @stop
    def _read_rotate(self):
        fp = self.fp 
        fp.readline() 
        assert int(fp.readline()) == 0
        [fp.readline() for _ in range(3)]
    @stop  
    def _read_dynamic_patch(self):
        fp = self.fp 
        fp.readline() 
        ninter = int(fp.readline())
        fp.readline()
        # dynamic_patch = {'ninter':ninter}
        dynamic_patch = {'int':[[int(i) for i in fp.readline().split()] for _ in range(ninter)]}
        data2 = list()
        for _ in range(ninter):
            fp.readline()
            rr0 = fp.readline().split()
            rr0 = [int(j) for j in rr0]
            nfb = rr0[-1]
            rr_from = list()
            for _ in range(nfb):
                fp.readline()
                rr1 = fp.readline().split()
                rr1 = [float(j) for j in rr1]
                fp.readline()
                rr2 = fp.readline().split()
                rr2 = [float(j) for j in rr2]
                rr_from.append([rr1, rr2])
            data2.append([rr0, rr_from])
        dynamic_patch['info'] = data2
        self['dynamic_patch'] = dynamic_patch
    def _read_iyxs(self):
        fp = self.fp 
        pos = fp.tell()
        t = fp.readline()
        if t == '':
            return False
        if t.lower().find('iyxs') == -1:
            fp.seek(pos,0)
            return
        yxsData = dict()
        yxsData['iyxs'] = int(fp.readline())
        fp.readline()
        yxsData['init'] = fp.readline().split()
        fp.readline()
        yxsData['init_params'] = [int(i) for i in fp.readline().split()]
        assert len(yxsData['init_params']) == 5
        fp.readline()
        ngap = int(fp.readline())
        if ngap != 0:
            fp.readline()
            yxsData['gap_blocks'] = [int(fp.readline()) for i in range(ngap)]
        else: 
            yxsData['gap_blocks'] = []
        fp.readline()
        yxsData['noninflag'] = int(fp.readline())
        if yxsData['noninflag'] != 0:
            fp.readline()
            yxsData['noninData'] = [[float(i) for i in fp.readline().split()] for _ in range(abs(yxsData['noninflag']))]
        fp.readline()
        ibflag = int(fp.readline())
        if ibflag > 0:
            fp.readline()
            yxsData['initBoundaryData'] = [[float(j) for j in fp.readline().split()] for i in range(ibflag)]
        fp.readline()
        yxsData['meanflag'] = int(fp.readline())
        if yxsData['meanflag'] != 0:
            fp.readline()
            yxsData['meanData'] = [[float(i) for i in fp.readline().split()] for _ in range(abs(yxsData['meanflag']))]

        fp.readline()
        yxsData['relaxflag'] = int(fp.readline())
        if yxsData['relaxflag'] != 0:
            fp.readline()
            yxsData['relaxcoeff'] = [float(i) for i in fp.readline().split()]
        fp.readline()
        nvars = int(fp.readline())
        yxsData['nvars'] = nvars
        if nvars > 0:
            fp.readline()
            yxsData['vars_list'] = [fp.readline().split() for i in range(nvars)]
            yxsData['vars_list'] = [[int(i),int(j),s] for i,j,s in yxsData['vars_list']]
        
        data = self.fp.read()

        n1  = data.find('{')
        if n1 != -1:
            n2 = data.find('}')
            self['jsonData'] = json.loads(data[n1:n2+1])
            self['otherString'] = data[n2+1:]

        self['yxsData'] = yxsData


    def _getline(self,line):
        grid = line[1]
        istart_end = line[2], line[5]
        jstart_end = line[3], line[6]
        kstart_end = line[4], line[7]
        v1 = line[8]
        v2 = line[9]
        return grid, (istart_end, jstart_end, kstart_end, v1, v2)
    def get_one2oneData(self):
        #,下标从1开始
        if self.one2oneData is None:
            start,end = self['one2oneData']
            start = [self._getline(i) for i in start]
            end   = [self._getline(i) for i in end  ]
            self.one2oneData = [(i1, i2, j1, j2) for (i1, i2), (j1, j2) in zip(start, end)]
        return self.one2oneData
    def get_periodicData(self):
        #,下标从1开始
        if self.periodicData is None:
            pdata = list()
            for ii,f in enumerate('IJK'):
                for jj,t in enumerate('0E'):
                    for bc,bcdata in self[f+t]:
                        if bc[2] == 2005:
                            pdata.append([bc[0],ii*2+jj,bc[3],bc[4],bc[5],bc[6],
                                          int(float(bcdata[0])), float(bcdata[1]), float(bcdata[2]), float(bcdata[3]) ])
            self.periodicData = pdata 
        return self.periodicData
    def get_boundaryData(self):
        # 获取bctype不等于0的边条信息,下标从1开始
        if self.boundaryData is None: 
            keys1 = ['I0','IE','J0','JE','K0','KE']
            self.boundaryData = [[b1,b2,k1] for k1 in keys1 for b1,b2 in self[k1] if b1[2] != 0]

        return self.boundaryData
   
class write:
    bc_title = {'2002': ('pexit/pinf\n',None),
                '2003': ('      Mach   Pt/Pinf   Tt/Tinf     alpha      beta\n',None),
                '2004': ('        Tw        Cq\n',('{:10.5f}{:10.5f}{:10.0f}{:10.0f}\n',4)),
                '2005': ('    ngridp      dthx      dthy      dthz\n',('{:10.0f}'+'{:10.5f}'*3+'\n',4)),
                '2009': ('   pt/pinf   tt/tinf     alpha      beta\n',('{:10.5f}{:10.5f}{:10.5f}{:10.5f}\n',4)),
                '2006': ('    ngridc    P/Pinf    intdir   axcoord\n',('{:10.0f}{:10.5f}{:10.0f}{:10.0f}\n',4))}
    string_re = re.compile('[a-zA-Z]')
    title_list1 = (
        '     xmach     alpha      beta      reue      tinf     ialph    ihstry\n',
        '      sref      cref      bref       xmc       ymc       zmc\n',
        '        dt     irest   iflagts      fmax     iunst   cfl_tau\n',
        '     ngrid   nplot3d    nprint    nwrest      ichk       i2d    ntstep       ita\n',
        '       ncg       iem  iadvance    iforce  ivisc(i)  ivisc(j)  ivisc(k)\n',
        '      idim      jdim      kdim\n',
        '    ilamlo    ilamhi    jlamlo    jlamhi    klamlo    klamhi\n',
        '     inewg    igridc        is        js        ks        ie        je        ke\n',
        '  idiag(i)  idiag(j)  idiag(k)  iflim(i)  iflim(j)  iflim(k)\n',
        '   ifds(i)   ifds(j)   ifds(k)  rkap0(i)  rkap0(j)  rkap0(k)\n',
        '      grid     nbci0   nbcidim     nbcj0   nbcjdim     nbck0   nbckdim    iovrlp\n',
    )
    title_list2 = (
        '      mseq    mgflag    iconsf       mtt      ngam\n',
        '      issc  epssc(1)  epssc(2)  epssc(3)      issr  epssr(1)  epssr(2)  epssr(3)\n',
        '      ncyc    mglevg     nemgl     nifo\n',
        '      mit1      mit2      mit3      mit4      mit5\n')
    variables_string = '''
    1    0  X
    2    0  Y
    3    0  Z
    4    1  Density
    5    1  VelocityX
    6    1  VelocityY
    7    1  VelocityZ
    8    1  Pressure
    9    0  Temperature
    10   0  PressureStagnation
    11   0  Mach
    12   1  Turbulent_viscosity
    13   1  Turbulent_model_var1
    14   0  Turbulent_model_var2
    15   0  Turbulent_model_var3
    16   0  Turbulent_model_var4
    17   0  Turbulent_model_var5
    18   0  dUdX
    19   0  dUdY
    20   0  dUdZ
    21   0  dVdX
    22   0  dVdY
    23   0  dVdZ
    24   0  dWdX
    25   0  dWdY
    26   0  dWdZ
    27   0  ReynoldsUU
    28   0  ReynoldsVV
    29   0  ReynoldsWW
    30   0  ReynoldsUV
    31   0  ReynoldsUW
    32   0  ReynoldsVW
    33   0  Cell_volume
    '''
    def __init__(self,filename,inp):
        self.inp = inp 
        self.ofp = open(filename,'w')
        self.get_variables_list()
        self.start_write()
    def get_variables_list(self):
        var_list = self.variables_string.strip().split()
        nvars = len(var_list) // 3
        assert len(var_list) % 3==0
        self.variables_list = [var_list[i*3+2] for i in range(nvars)]
    def start_write(self):
        fp = self.ofp
        inp = self.inp
        t = '\n'.join(inp['files'])
        fp.write('I/O FILES\n')
        fp.write(t)
        key_words = inp.get('key_words')
        if key_words:
            fp.write('\n>\n')
            for i in key_words:
                fp.write('  '.join([str(j) for j in i])+'\n')
            fp.write('<')
        fp.write(
            '\n  CFL3D Case configuration\n')
        for t in self.title_list1:
            print(t.rstrip())
            self._write_lines(t)
        self._write_boundaryData()
        for t in self.title_list2:
            print(t.rstrip())
            self._write_lines(t)
        self._write_one2oneData()
        self._write_patch_surface()
        self._write_output()
        self.ofp.write('{:>9s}\n{:9d}\n'.format('movie', inp['movie']))
        self._write_print()
        self._write_control()
        self._write_trans()
        self._write_rotate()
        self._write_dynamic_patch()
        self._write_iyxs()
        
    def _write_boundaryData(self):
        fp = self.ofp 
        title1 = '{:6s}grid   segment    bctype      jsta      jend      ksta      kend     ndata\n'
        title2 = '{:6s}grid   segment    bctype      ista      iend      ksta      kend     ndata\n'
        title3 = '{:6s}grid   segment    bctype      ista      iend      jsta      jend     ndata\n'
        keys1 = ['I0','IE','J0','JE','K0','KE']
        keys2 = ['i0', 'idim', 'j0', 'jdim', 'k0', 'kdim']
        title_dict = {'I':title1,'J':title2,'K':title3}
        sf = '{:10d}'* 8 + '\n'
        for k1,k2 in zip(keys1,keys2):
            fp.write(title_dict[k1[0]].format(k2+':'))
            for bc,bcdata in self.inp[k1]:
                fp.write(sf.format(*bc))
                ndata = int(bc[-1])
                if ndata != 0:
                    bctype = str(bc[2])
                    bc_title,sf2 = self.bc_title[bctype]
                    fp.write(bc_title)
                    if self.string_re.search(str(bcdata[0])):
                        fp.write(' '.join(bcdata)+'\n')
                    else:
                        if ndata < 0:
                            fp.write(bcdata[0]+'\n')
                        else:
                            bcdata = [float(i) for i in bcdata]
                            self._write_one_line(None,bcdata)
    def _write_one2oneData(self):
        o1,o2 = self.inp['one2oneData']
        self.ofp.write('   1-1 blocking data:\n      nbli\n')
        self.ofp.write('{:10d}\n'.format(len(o1)))
        title = '   NUMBER   GRID   :   ISTA   JSTA   KSTA   IEND   JEND   KEND   ISVA1   ISVA2\n'
        sf = '{:9d}{:7d}{:11d}'+'{:7d}'*7+'\n'
        self.ofp.write(title)
        for i in o1:
            self.ofp.write(sf.format(*i))
        self.ofp.write(title)
        for i in o2:
            self.ofp.write(sf.format(*i))
    def _write_patch_surface(self):
        n = self.inp.get("patchFile",0)
        if n is not 0:
            n = 1
        self.ofp.write('''  patch surface data:
    ninter
         {}\n'''.format(n))
    def _write_output(self):
        self.ofp.write(
            '  plot3d output:\n   grid iptype istart   iend   iinc jstart   jend   jinc kstart   kend   kinc\n')
        sf = '{:7d}'*11 + '\n'
        for i in self.inp['output']:
            self.ofp.write(sf.format(*[int(j) for j in i]))
    def _write_print(self):
        self.ofp.write(
        '  print out:\n  block iptype istart   iend   iinc jstart   jend   jinc kstart   kend   kinc\n')
        if self.inp.get('print_out'):
            self._write_lines('',self.inp['print_out'])
    def _write_control(self):
        cfs = self.inp['control_surface']
        self.ofp.write(' control surfaces:\n   ncs\n{:>6d}\n'.format(len(cfs)))
        self.ofp.write(
            '  grid   ista  iend  jsta  jend  ksta  kend iwall inorm\n')
        if cfs:
            sf = '{:>6d}'*9 + '\n'
            for i in cfs:
                self.ofp.write(sf.format(*i))
    def _write_trans(self):
        self.ofp.write('  moving grid data - translation\n  trans\n       0\n')
        self.ofp.write('''    lref
    grid itrans   rfreq   utrans   vtrans   wtrans
    grid  dxmax   dymax    dzmax\n''')
    def _write_rotate(self):
        self.ofp.write('''  MOVING GRID DATA - ROTATION
  NROTAT
       0
    LREF
    GRID IROTAT   RFREQ   OMEGAX   OMEGAY   OMEGAZ   XORIG   YORIG   ZORIG
    GRID   THXMAX   THYMAX   THZMAX\n'''.lower())
    def _write_dynamic_patch(self):
        dynamic = self.inp.get('dynamic_patch',None)
        if dynamic is None:
            return
        self.ofp.write('  dynamic patch input data\n    ninter\n')
        self.ofp.write(
            '{:10d}\n   int  ifit    limit    itmax    mcxie    mceta      c-0    iorph    itoss\n'.format(len(dynamic['int'])))
        sf = '{:6d}{:6d}'+'{:9d}'*7 + '\n'
        for i in dynamic['int']:
            self.ofp.write(sf.format(*i))
        info = dynamic['info']
        to_sf = '{:6d}{:6d}'+'{:9d}'*5 + '\n'
        to_title = '   int    to     xie1     xie2     eta1     eta2      nfb\n'
        f_title1 = '        from     xie1     xie2     eta1     eta2    factj    factk\n'
        f_title2 = '          dx       dy       dz   dthetx   dthety   dthetz\n'
        sf1 = '{:12.0f}' + '{:9.0f}'*4 + '{:9.5f}'*2 + '\n'
        sf2 = '{:12.4f}' + '{:9.4f}'*5 + '\n'
        for to,from_ in info:
            self.ofp.write(to_title)
            self.ofp.write(to_sf.format(*to))
            for t1,t2 in from_:
                self.ofp.write(f_title1)
                self.ofp.write(sf1.format(*t1))
                self.ofp.write(f_title2)
                self.ofp.write(sf2.format(*t2))
    def _write_iyxs(self):
        yxsData = self.inp.get('yxsData')
        if yxsData is None:
            return False 
        iyxs = yxsData['iyxs']
        self.ofp.write('    IYXS\n{:8d}\n'.format(iyxs))
        init_title = '    init_file ig yxs_g  iq yxs_q\n'
        sf = '     {}  {}  {}  {}  {}  {}\n'
        self.ofp.write(init_title)
        self.ofp.write(sf.format(*yxsData['init']))
        self.ofp.write('    init_param (1-5)\n')
        self.ofp.write('    {}  {}  {}  {}  {}\n'.format(*yxsData['init_params']))
        self.ofp.write('    gap_blocks\n')
        self.ofp.write('    {}\n'.format(len(yxsData['gap_blocks'])))
        if yxsData['gap_blocks']:
            self.ofp.write('    gap_blocks\n')
            sf = '    {}\n'
            for i in yxsData['gap_blocks']:
                self.ofp.write(sf.format(i))
        noninflag = yxsData['noninflag']
        if abs(noninflag) > 0:
            self.ofp.write('    noninflag\n{:8d}\n'.format(len(yxsData['noninData'])))
            self._write_lines('    grid  flag  xcentrotg,ycentrotg,zcentrotg,xrotrateg,yrotrateg,zrotrateg\n',
                yxsData['noninData'])
        else:
            self.ofp.write('    noninflag\n{:8d}\n'.format(0))
        initBoundaryData = yxsData.get('initBoundaryData',[])
        self.ofp.write('    init_boundary_data(Pt/pinf  Tt/tinf  alpha    beta     pressure auxdata)\n    {}\n'.format(len(initBoundaryData)))
        if initBoundaryData:
            self.ofp.write('    Pt/pinf  Tt/tinf  alpha    beta     pressure auxdata\n')
            fs = '  ' + '  {:.5f}'*6 + '\n'
            for i in initBoundaryData:
                self.ofp.write(fs.format(*i))
        meanData = yxsData.get('meanData',[])
        if len(meanData)> 0:
            self.ofp.write('    meanflag\n{:8d}\n'.format(len(meanData)))
            self._write_lines('     igrid   ijkface    method      idia     itmax    igroup\n',
                 meanData,)
        else: 
            self.ofp.write('    meanflag\n{:8d}\n'.format(0))
        relaxData = yxsData.get('relaxcoeff',[])
        self.ofp.write('    relaxflag\n{:8d}\n'.format(len(relaxData)))
        if len(relaxData) != 0:
            self._write_one_line('    relaxcoeff([1-10].1:5140,2:other mixing plane,3:gap_list)\n',relaxData)
        vars_list = yxsData.get('vars_list',[])
        self.ofp.write('    nvars\n    {}\n'.format(len(vars_list)))
        sf = '    {:<3d}  {}  {}\n'
        if vars_list:
            self.ofp.write("    variables list\n")
            if not isinstance(vars_list[0],int):
                vars_list = [i[1] for i in vars_list]
        for i,v in enumerate(vars_list):
            self.ofp.write(sf.format(i+1,v,self.variables_list[i]))
        jdata = self.inp.get('jsonData')
        if jdata is not None:
            json.dump(jdata,self.ofp)
        otherString = self.inp.get('otherString')
        if otherString is not None:
            self.ofp.write('\n')
            self.ofp.write(otherString.lstrip())
    def _write_one_line(self,title,data,sf1=' {:9.0f}',sf2=' {:9.6f}'):
        if title is not None:
            self.ofp.write(title)
        sf = [sf1 if i % 1<1e-6 else sf2 for i in data]
        sf = ''.join(sf)+'\n'
        data = [float(i) for i in data]
        self.ofp.write(sf.format(*data))
    def _write_lines(self,title,data=None):
        try:
            title_split = title.split()
            if data is None:
                key = title_split[0].lower().split('(')[0]
                data = self.inp[key]
            if isinstance(data[0],float) or isinstance(data[0],int):
                multi = False 
            else: 
                multi = True
            self.ofp.write(title)
            if multi:
                for t in data:
                    sf = ['{:10.0f}' if i % 1 < 1e-5 else '{:10.5f}' for i in t]
                    sf = ''.join(sf) + '\n'
                    self.ofp.write(sf.format(*t))
            else:
                sf = ['{:10.0f}' if i % 1 < 1e-5 else '{:10.5f}' for i in data]
                sf = ''.join(sf) + '\n'
                self.ofp.write(sf.format(*data))
        except Exception as e:
            print(data)
            raise(e)
def merge_boundary(inp):
    keys = ['I0','IE','J0','JE','K0','KE']
    types = [0]
    for nface,key in zip(range(1,7),keys):
        bound = inp[key]
        n = -1
        for typ in types:
            while True:
                n+=1
                if n+1 >=len(bound):
                    break
                if bound[n][0][2] == typ:
                    nblock = bound[n][0][0]
                    if bound[n-1][0][0] == nblock or bound[n+1][0][2] != typ or bound[n+1][0][0] != nblock:
                        continue
                    nsum = 0
                    while True:
                        nsum += 1
                        if n+nsum >= len(bound):
                            break
                        if bound[n+nsum][0][0] == nblock and bound[n+nsum][0][2] == typ:
                            continue 
                        else: 
                            break 
                    if n+nsum >= len(bound):
                        break
                    if bound[n+nsum][0][0] == nblock:
                        continue 
                    else: 
                        for _ in range(nsum-1):
                            bound.pop(n+1)
                        for j in range(3,7):
                            bound[n][0][j] = 0 
                        inp['grid'][nblock-1][nface] = 1
def read_prout(fname):
    fp = open(fname)
    d = dict()
    force_list = ['x-force', 'y-force','z-force','resultant-force','lift-force','drag-force']
    while True:
        s = fp.readline()
        if not s:
            break
        if s.strip().startswith('Control Surface'):
            n = s.split()[-1]
            face_data = dict()
            d[f'Surface{n}'] = face_data
            while True:
                s = fp.readline().strip()
                if s.startswith('x-area'):
                    data_list = s.split()
                    face_data['x-area'] = float(data_list[2])
                    face_data['y-area'] = float(data_list[5])
                    face_data['z-area'] = float(data_list[8])
                    face_data['total-area'] = float(data_list[11])
                if s.startswith('P/Pinf'):
                    data_list = s.split()
                    face_data['P/Pinf'] = float(data_list[2])
                    face_data['Pt/Pinf'] = float(data_list[-1])
                if s.startswith('T/Tinf'):
                    data_list = s.split()
                    face_data['T/Tinf'] = float(data_list[2])
                    face_data['Tt/Tinf'] = float(data_list[-1])
                if s.startswith('Mach number'):
                    data_list = s.split()
                    face_data['Mach'] = float(data_list[-1])
                if s.startswith('Mass flow / (rhoinf*vinf*(L_R)**2)'):
                    data_list = s.split()
                    face_data['mass_flow'] = float(data_list[-1])
                if s.startswith('Pressure force'):
                    for key in ['Pressure_force','Thrust force','Total force']:
                        dl = [float(i) for i in s.split()[2:]]
                        face_data[key] = dict(zip(force_list,dl))
                    break
    
    return d
def read(fname):
    fname = Path(fname)
    if fname.suffix == '.prout':
        r = read_prout(fname)
    else:
        r = read_inp(fname)
    return r
if __name__=='__main__':
    k = read('/home/yxs/Documents/learning/case/case_stage35/stage35_5161/stage35mm_sp64_auto_153500/stage35_cfl3d.prout')
    print(k)
