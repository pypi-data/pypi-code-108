try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from matplotlib import pyplot
import numpy as np
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_base import OMFITtree

__all__ = ['OMFITeliteGamma','OMFITeliteEigenfunction','OMFITelite2DEigenfunction','OMFITelitefun2d','OMFITelitextopsi','OMFITeliteAggregated','OMFITeqdat','OMFITbalstab','OMFIToutbal']

class OMFITeliteGamma(SortedDict,OMFITascii):
    """ELITE growth rates data file (Gamma file)"""
    def __init__(self,filename,**kw):
        OMFITascii.__init__(self,filename,**kw)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        self.clear()
        with open(self.filename,'r') as f:
            lines=f.readlines()
        for line in lines[1:]:
            tmp=line.split()
            nn=int(tmp[0])
            items=tmp[1:]
            self[nn]=SortedDict()
            for k,item in enumerate(['cent_gam/w_A','gam/(omegspi_max/4)','gamsq','del','gamr','gamr2','tmatasym']):
                self[nn][item]=float(items[k])

class OMFITeliteEigenfunction(OMFITascii,SortedDict):
    def __init__(self,filename,symmetric=False):
        OMFITobject.__init__(self,filename)
        SortedDict.__init__(self)
        self.symmetric=symmetric
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        lines=self.read().splitlines()
        self['date']=lines[0]
        self['version']=lines[1]
        self['eq_type']=lines[2]
        self['n']=int(lines[3])
        self['eq_data']=np.array(list(map(float,(lines[4]+' '+lines[5]).split())))
        self['eq_par']=np.array(list(map(int,(' '.join(lines[6:8])).split())))
        self['dummy']=np.array(list(map(float,(' '.join(lines[8:12])).split())))
        tmp=np.array(list(map(float,(' '.join(lines[12:])).split())))
        tmp=np.reshape(tmp,(-1,self['eq_par'][9])).T
        self['xx']=tmp[:,0]
        self['psi']=tmp[:,-1]
        if self.symmetric:
            self['eigh'] = tmp[:, 1:-1:1] + 1j * np.zeros(tmp[:, 1:-1:1].shape)
        else:
            self['eigh']=tmp[:,1:-2:2]+1j*tmp[:,2:-1:2]

    def peak(self,decimate=1):
        f = np.zeros(self['eigh'][::decimate].shape)
        for k1 in np.linspace(0,2*np.pi,64)[:-1]:
            m1=np.exp(1j*k1*2)
            f=np.max([f,np.real(self['eigh'][::decimate]*m1)],0)
        return f

    def envelope(self,decimate=1):
        return np.max(self.peak(decimate),1)

    def plot(self,fancy=False,decimate=None):
        from omfit_classes.utils_plot import plotc
        if decimate is None:
            decimate=int(np.ceil(1+len(self['eigh'])/10000.))
        if fancy:
            tmp=self.peak(decimate)
            plotc(self['psi'][::decimate],tmp)
            pyplot.plot(self['psi'][::decimate],np.max(tmp,1),color='k')
        else:
            y=self.envelope(decimate)
            x=self['psi'][::decimate]
            tmp=abs(np.trapz(y[np.where(x<0.98)[0]],x[np.where(x<0.98)[0]]))
            pyplot.plot(x,y/tmp)
        pyplot.ylim([1E-8,pyplot.ylim()[-1]])
        pyplot.xlabel('$\\psi$')
        pyplot.title('Eigenfunction n=%d'%self['eq_par'][5])

class OMFITelite2DEigenfunction(OMFITtree):
    def __init__(self, filename, psicontour=np.asarray([0.4,0.5,0.6,0.7,0.8,0.9,1])):
        self.dynaLoad = True
        self.filename = filename
        self.psicontour = psicontour

    @dynaLoad
    def load(self):
        self['xtopsi' ] =OMFITelitextopsi(self.filename + '.xtopsi')
        self['fun2d'] = OMFITelitefun2d(self.filename + '.fun2d')
        self['xtopsi'].load()
        self['fun2d'].load()
        if len(self.psicontour)>0:
            self['psiind']=[]
            for psi in self.psicontour:
                self['psiind'].append(np.argmin(abs(self['xtopsi']['psiinterp']-psi)))
            self['rind']=[]
            for i in self['psiind']:
                self['rind'].append(np.argmin(abs(np.asarray(self['fun2d']['xx'][1:self['fun2d']['ns']*self['fun2d']['nxplt']:self['fun2d']['ns']])-self['xtopsi']['rrmax'][i])))

    @dynaSave
    def save(self):
        self['xtopsi'].save()
        self['fun2d'].save()

    def plot(self):
        pyplot.tricontourf(self['fun2d']['xx'],self['fun2d']['zz'],self['fun2d']['f2d'],30,cmap='rainbow')
        if len(self.psicontour)>0:
            for i in self['rind']:
                pyplot.plot(self['fun2d']['xx'][i*self['fun2d']['ns']+1:(i+1)*self['fun2d']['ns']],
                              self['fun2d']['zz'][i*self['fun2d']['ns']+1:(i+1)*self['fun2d']['ns']],'k-',linewidth=0.5)
        pyplot.axis('equal')

class OMFITelitefun2d(OMFITascii,SortedDict):
    def __init__(self,filename):
        OMFITobject.__init__(self,filename)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        lines=self.read().splitlines()
        self['cdatetime']=lines[0]
        self['codver']=lines[1]
        self['shape']=lines[2]
        self['npts']=int(lines[3])
        set3=np.array(list(map(float,(' '.join(lines[4:6])).split())))
        set2=np.array(list(map(int,(' '.join(lines[6:8])).split())))
        self['nx']=set2[9]
        self['nm']=set2[4]
        set1=np.array(list(map(float,(' '.join(lines[8:12])).split())))
        set0=np.array(list(map(int,(lines[12]).split())))
        self['nxplt']=set0[0]
        self['ns']=set0[1]
        tmp=np.array(list(map(float,(' '.join(lines[13:])).split())))
        tmp=np.reshape(tmp,(-1,self['nxplt']*self['ns'])).T
        self['xx']=tmp[:,0]/100.0
        self['zz']=tmp[:,1]/100.0
        self['bp']=tmp[:,2]
        self['f2d']=tmp[:,3]

    def plot(self):
        from matplotlib import pyplot
        pyplot.tricontourf(self['xx'],self['zz'],self['f2d'],30,cmap='rainbow')
        pyplot.axis('equal')

class OMFITelitextopsi(OMFITascii,SortedDict):
    def __init__(self,filename):
        OMFITobject.__init__(self,filename)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        lines=self.read().splitlines()
        self['nxinterp']=int(lines[0])
        tmp=np.array(list(map(float,(' '.join(lines[1:-1])).split())))
        tmp=np.reshape(tmp,(-1,self['nxinterp'])).T
        self['xinterp']=tmp[:,0]
        self['psiinterp']=tmp[:,1]
        self['rrmax']=tmp[:,2]/100.0
        self['rmax']=tmp[:,3]/100.0

class OMFITeliteAggregated(OMFITascii,SortedDict):
    def __init__(self,filename):
        OMFITascii.__init__(self,filename)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        with open(self.filename,'r') as f:
            tmp=f.readlines()
        dum=' '.join([line.strip() for line in tmp])
        dum=list(map(float,dum.split()))
        try:
            dum=np.reshape(dum,(-1,12))
        except Exception:
            dum=np.reshape(dum,(-1,11))

        #in case the ELITE run did not finish
        self['alpha']=dum[:,0]
        self['pprime']=dum[:,1]
        self['jmax']=dum[:,2]
        self['jsep']=dum[:,3]
        self['gamma']=dum[:,4]
        self['ngam']=dum[:,5].astype('int')
        self['gamws']=dum[:,6]
        self['ngamws']=dum[:,7].astype('int')
        self['javg']=dum[:,8]
        self['gamws16']=dum[:,9]
        self['ngamws16']=dum[:,10].astype('int')
        if dum.shape[1]==12:
            self['icount']=dum[:,11].astype('int')

class OMFITeqdat(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface to equilibria files generated by ELITE and BALOO (.dskbal files)

    NOTE: this object is "READ ONLY", meaning that the changes to the entries of this object will not be saved to a file. Method .save() could be written if becomes necessary

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename='', **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        for k, line in enumerate(lines):
            if 'npsi,nthet' in line:
                break
        if k == len(lines) - 1:
            raise ValueError('eqdat file should have a line with `npsi,nthet` in it')

        k += 1
        self['npsi'], self['npts'] = list(map(int, lines[k].split()))
        lsegment = int(np.ceil(self['npsi'] / 5.))

        while k < len(lines) - 1:
            k += 1
            name = lines[k].strip()
            self[name] = []
            if name not in ['X', 'Z', 'poloidal field--bpol']:
                for seg in range(lsegment):
                    k += 1
                    self[name].extend(re.sub('D', 'E', lines[k]).split())
                self[name] = np.flipud(np.array(list(map(eval, self[name]))))
            else:
                for x in range(self['npts']):
                    self[name].append([])
                    for seg in range(lsegment):
                        k += 1
                        self[name][-1].extend(re.sub('D', 'E', lines[k]).split())
                    self[name][-1] = np.array(list(map(eval, self[name][-1])))
                self[name] = np.array(self[name])

        for name in self:
            if isinstance(self[name], np.ndarray) and len(self[name].shape) == 1:
                self[name] = self[name][::-1]

    @dynaLoad
    def plot(self, **kw):
        from omfit_classes.utils_plot import title_inside, autofmt_sharex
        items = [item for item in self if item not in ['npsi', 'npts', 'X', 'Z', 'poloidal field--bpol']]

        ax = None
        r = np.sqrt(len(items) + 1)
        c = np.ceil((len(items)) / np.sqrt(len(items))) + 1

        for k, item in enumerate(items):
            x = self.get('poloidal flux--psiv', np.arange(len(self[item])))
            x = (x - min(x)) / (max(x) - min(x))
            ax = pyplot.subplot(r, c, k + 1 + k // (c - 1) + 1)
            ax.plot(x, self[item], **kw)
            title_inside(item, y=0.8)
            ax.set_xlim([0, 1])

        nskip = (self['npsi'] // 10)
        ax0 = ax
        ax = pyplot.subplot(1, c, 1)
        ax.plot(self['X'][:, ::-nskip] / 100., self['Z'][:, ::-nskip] / 100., color=ax0.lines[-1].get_color())
        ax.set_aspect('equal')
        ax.set_frame_on(False)

        autofmt_sharex()

class OMFITbalstab(SortedDict,OMFITascii):
    r"""
    OMFIT class used to interface to `balstab` file from BALOO

    NOTE: this object is "READ ONLY", meaning that the changes to the entries of this object will not be saved to a file. Method .save() could be written if becomes necessary

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """
    def __init__(self, filename='', **kw):
        OMFITascii.__init__(self,filename,**kw)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        with open(self.filename,'r') as f:
            tmp=f.read().strip()
        tmp=re.sub('% ','%_',tmp)
        tmp=re.sub(' s ',' 0 ',tmp)
        tmp=re.sub(' u ',' 1 ',tmp)
        tmp=tmp.split('\n')
        numbers=list(map(int,tmp[0].split()))
        headers=tmp[1].split()
        self.clear()
        for k in range(2,numbers[0]+2):
            res=list(map(float,tmp[k].split()))
            res[0]=int(res[0])
            res[4]=int(res[4])
            self[res[0]]={}
            for k1,h in enumerate(headers):
                if k1==0:
                    continue
                self[res[0]][h]=res[k1]

class OMFIToutbal(SortedDict,OMFITascii):
    r"""
    OMFIT class used to interface to `outbal` file from BALOO

    NOTE: this object is "READ ONLY", meaning that the changes to the entries of this object will not be saved to a file. Method .save() could be written if becomes necessary

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """
    def __init__(self, filename='', **kw):
        OMFITascii.__init__(self,filename,**kw)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        with open(self.filename,'r') as f:
            lines=f.read().strip().split('\n')
        tmp=[]
        for k in range(int(len(lines)//2)):
            tmp.append(lines[k*2]+lines[k*2+1])
        names=tmp[0].split()
        tmp=tmp[1:]
        for k,line in enumerate(tmp):
            tmp[k]=list(map(float,line.split()))
        tmp=np.array(tmp)
        for k,name in enumerate(names):
            self[name]=tmp[:,k]

    @dynaLoad
    def plot(self, **kw):
        from omfit_classes.utils_plot import title_inside

        items=[item for item in self if item not in ['surf','psi_norm']]

        r=np.sqrt(len(items)+1)
        c=np.ceil((len(items))/np.sqrt(len(items)))
        for k,item in enumerate(items):
            x=self.get('psi_norm',np.arange(len(self[item])))
            x=(x-min(x))/(max(x)-min(x))
            ax=pyplot.subplot(r,c,k+1)
            ax.plot(x,self[item],**kw)
            title_inside(item,y=0.8)
            ax.set_xlim([0,1])
