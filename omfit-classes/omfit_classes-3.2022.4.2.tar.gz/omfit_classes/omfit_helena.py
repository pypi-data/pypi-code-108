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
from scipy.interpolate import interp1d
import scipy.fftpack

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_nc import OMFITncData
from omfit_classes.omfit_osborne import OMFITpFile
from omfit_classes.omfit_eqdsk import fluxSurfaces
from omfit_classes.utils_math import fourier_boundary

__all__ = ['OMFIThelena','OMFITmishkamap','OMFIThelenaout','OMFIThelenainput']

class OMFIThelena(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with Helena mapping file for ELITE

    :param filename: filename passed to OMFIThelena class

    :param \**kw: keyword dictionary passed to OMFITobject class, not currently used
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

        self.descriptions=SortedDict()
        self.descriptions['0d']=SortedDict()
        self.descriptions['0d']['npsi']='number of flux surfaces'
        self.descriptions['0d']['nchi']='number of points on each flux surface'
        self.descriptions['1d']=SortedDict()
        self.descriptions['2d']=SortedDict()
        self.descriptions['1d']['psi']='psi'
        self.descriptions['1d']['dp']='dp/dpsi'
        self.descriptions['1d']['fpol']='Poloidal current function'
        self.descriptions['1d']['ffp']='fpoldfpol/dpsi'
        self.descriptions['1d']['d2pdpsi2']='d2p/dpsi2'
        self.descriptions['1d']['dffp']='d(ffp)/dpsi'
        self.descriptions['1d']['q']='Safety factor'
        self.descriptions['2d']['R']='Major radius of grid points'
        self.descriptions['2d']['Z']='Height of grid points'
        self.descriptions['2d']['Bp']='Poloidal magnetic field on grid points'
        self.descriptions['1d']['ne']='Electron density'
        self.descriptions['1d']['te']='Electron temperature'
        self.descriptions['1d']['nmainion']='Main ion density'
        self.descriptions['1d']['nimpurity']='Main impurity density'
        self.descriptions['1d']['ni']='Total ion density'
        self.descriptions['1d']['ti']='Ion temperature'
        self.descriptions['0d']['Zeff'] = 'Effective charge'
        self.descriptions['0d']['Aimp'] = 'Atomic mass of the impurity species'
        self.descriptions['0d']['Amain'] = 'Atomic mass of the main ion'
        self.descriptions['0d']['Zimp'] = 'Charge number of the impurity species'

        # There may be more impurity species, but let's stop here for now
        self.units=SortedDict()
        self.units['1d']=SortedDict()
        self.units['2d']=SortedDict()
        self.units['1d']['ne']='10^20/m^3'
        self.units['1d']['te']='KeV'
        self.units['1d']['nmainion']='10^20/m^3'
        self.units['1d']['nimpurity']='10^20/m^3'
        self.units['1d']['ni']='10^20/m^3'
        self.units['1d']['ti']='KeV'
        self.units['1d']['psi']='Wb'
        self.units['1d']['dp']='Pa*mu0/Wb'
        self.units['1d']['fpol']='A?'
        self.units['1d']['ffp']='A^2/Wb'
        self.units['1d']['dffp']='A^2/Wb^2'
        self.units['1d']['d2pdpsi2']='Pa*mu0/Wb^2'
        self.units['2d']['R']='m'
        self.units['2d']['Z']='m'
        self.units['1d']['q']=''
        self.units['2d']['Bp']='T'

        self['0d']=SortedDict()
        self['1d']=SortedDict()
        self['2d']=SortedDict()
        for key in self.descriptions['1d'].keys():
            self['1d'][key]=OMFITncData()
            self['1d'][key]['data']=np.array([0])
            self['1d'][key]['description']=self.descriptions['1d'][key]
            self['1d'][key]['psinorm']=np.array([0])
            self['1d'][key]['units']=self.units['1d'][key]
            self['1d'][key]['derivative']=np.array([0])
        for key in self.descriptions['2d'].keys():
            self['2d'][key]=OMFITncData()
            self['2d'][key]['data']=np.array([[0]])
            self['2d'][key]['description']=self.descriptions['2d'][key]
            self['2d'][key]['units']=self.units['2d'][key]
        for key in self.descriptions['0d'].keys():
            self['0d'][key]=OMFITncData()
            self['0d'][key]['description']=self.descriptions['0d'][key]
            self['0d'][key]['data']=0
            self['0d'][key]['units']=''

        columns_map = 5
        #read the file
        f=os.path.getsize(self.filename)
        if f==0:
            return

        with open(self.filename,'r') as file:
            (self['0d']['npsi']['data'],self['0d']['nchi']['data'])=self.read_nlines_and_split(file,1).astype(int)
            mod1=int(np.ceil(float(self['0d']['npsi']['data'])/columns_map - self['0d']['npsi']['data']//columns_map))
            nlines1=int(float(self['0d']['npsi']['data'])/columns_map)+mod1
            nlines2=self['0d']['nchi']['data']
            self['1d']['psi']['data']=self.read_nlines_and_split(file,nlines1)
            psi_norm=self['1d']['psi']['data']/self['1d']['psi']['data'][-1]
            self['1d']['dp']['data'] = self.read_nlines_and_split(file,nlines1)
            self['1d']['d2pdpsi2']['data'] = self.read_nlines_and_split(file,nlines1)
            self['1d']['fpol']['data'] = self.read_nlines_and_split(file,nlines1)
            self['1d']['ffp']['data'] = self.read_nlines_and_split(file,nlines1)
            self['1d']['dffp']['data'] = self.read_nlines_and_split(file,nlines1)
            self['1d']['q']['data'] = self.read_nlines_and_split(file,nlines1)
            self['2d']['R']['data'] = self.read_2d_array(file,nlines1,nlines2)
            self['2d']['Z']['data'] = self.read_2d_array(file,nlines1,nlines2)
            self['2d']['Bp']['data'] = self.read_2d_array(file,nlines1,nlines2)
            self['1d']['ne']['data'] = self.read_nlines_and_split(file,nlines1)/1e20
            self['1d']['ne']['derivative'] = self.read_nlines_and_split(file,nlines1)/1e20
            self['1d']['te']['data'] = self.read_nlines_and_split(file,nlines1)/1e3
            self['1d']['te']['derivative'] = self.read_nlines_and_split(file,nlines1)/1e3
            self['1d']['ti']['data'] = self.read_nlines_and_split(file,nlines1)/1e3
            self['1d']['ti']['derivative'] = self.read_nlines_and_split(file,nlines1)/1e3
            self['1d']['nmainion']['data'] = self.read_nlines_and_split(file,nlines1)/1e20
            self['1d']['nimpurity']['data'] = self.read_nlines_and_split(file,nlines1)/1e20
            self['0d']['Zeff']['data'] = float(self.read_nlines_and_split(file,1))
            self['0d']['Zimp']['data']= float(self.read_nlines_and_split(file,1))
            self['0d']['Aimp']['data']= float(self.read_nlines_and_split(file,1))
            self['0d']['Amain']['data']=float(self.read_nlines_and_split(file,1))

        for key in self['1d'].keys():
            self['1d'][key]['psinorm'] = psi_norm
        self['1d']['ni']['data'] = self['1d']['nmainion']['data'] + self['1d']['nimpurity']['data']
        self['1d']['ni']['derivative'] = self['1d']['ne']['derivative'] * self['1d']['ni']['data']/self['1d']['ne']['data']

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """

        order = ['psi','dp','d2pdpsi2','fpol','ffp','dffp','q','R','Z','Bp','ne','dnedpsi','te','dtedpsi','ti','dtidpsi','nmainion','nimpurity']
        d0_data = ['Zeff','Zimp','Aimp','Amain']

        with open(self.filename,'w') as f:
            f.write('Mapping file\n')
            f.write('%4i %4i\n'%(self['0d']['npsi']['data'],self['0d']['nchi']['data']))
            for key in order:
                f.write(key + ':\n')
                if key in self['1d']:
                    if key in ['ne','nmainion','nimpurity']:
                        self.write_helena_mapping_lines(f,self['1d'][key]['data']*1e20)
                    elif key in ['te','ti']:
                        self.write_helena_mapping_lines(f,self['1d'][key]['data']*1e3)
                    else:
                        self.write_helena_mapping_lines(f,self['1d'][key]['data'])
                elif key in self['2d']:
                    self.write_helena_mapping_lines(f,self['2d'][key]['data'])
                else:
                    data = key[1:3]
                    if data  == 'ne':
                        self.write_helena_mapping_lines(f,self['1d'][data]['derivative']*1e20)
                    else:
                        self.write_helena_mapping_lines(f,self['1d'][data]['derivative']*1e3)
            for key in d0_data:
                f.write(key + ':\n')
                f.write('%19.12g\n'%self['0d'][key]['data'])

        return None

    def plot(self):
        """
        Method used to plot all profiles, one in a different subplots

        :return: None
        """
        nplot=len(self['1d'])
        cplot=np.floor(np.sqrt(nplot)/2.)*2
        rplot=np.ceil(nplot*1.0/cplot)
        pyplot.subplots_adjust(wspace=0.35,hspace=0.0)
        pyplot.ioff()
        try:
            for k,item in enumerate(self['1d']):
                r=np.floor(k*1.0/cplot)
                c=k-r*cplot

                if k==0:
                    ax1=pyplot.subplot(rplot,cplot, r*(cplot)+c+1 )
                    ax=ax1
                else:
                    ax=pyplot.subplot(rplot,cplot, r*(cplot)+c+1, sharex=ax1)
                ax.ticklabel_format(style='sci', scilimits=(-3,3))
                if 'psinorm' not in self['1d'][item]:
                    printi('Can\'t plot %s because no psinorm attribute'%item)
                    continue
                x=self['1d'][item]['psinorm']

                pyplot.plot(x,self['1d'][item]['data'],'.-')
                pyplot.text(0.5, 0.9,item,
                            horizontalalignment='center',
                            verticalalignment='top',
                            size='medium',
                            transform = ax.transAxes)

                if k<len(self['1d'])-cplot:
                    pyplot.setp( ax.get_xticklabels(), visible=False)
                else:
                    pyplot.xlabel('$\\psi$')

                pyplot.xlim(min(x),max(x))

        finally:
            pyplot.ion()
            pyplot.draw()

    def write_helena_mapping_lines(self,file,mat,title = '', n=5):
        '''
        Writes a matrix in the HELENA mapping line format

        : param file : file to write the data

        : param mat: Matrix to be written, can be 1 or 2 dimensional

        : title : title for the data

        : param n : number of columns

        '''

        try:
            width = np.size(mat,1)
        except IndexError:
            width = 1
        length = np.size(mat,0)
        lines = []
        for row in range(width):
            mod1 = length%n
            if width > 1:
                slice = mat[:,row]
            else:
                slice = mat
            for column in range(length//n) :
                writeparam = slice[column * n : column * n + n ]
                lines.append(' '.join(str('%19.12g'%e) for e in writeparam) + '\n')
            if mod1 > 0:
                end_position = (length//n) * n
                remain = slice[end_position:]
                lines.append(' '.join(str('%19.12g'%e) for e in remain) + '\n')
        for line in lines:
            file.write(line)
        return

    def read_nlines_and_split(self, file, n, read_title=True):
        if read_title:
            line = file.readline()  # read title
        b = []
        for i in range(n):
            ifl = file.readline()
            a = ifl.split()
            for arg in a:
                b.append(float(arg))
        return np.array(b)

    def read_2d_array(self,file,n1,n2):
        line = file.readline() # read title
        b=[]
        for i in range(n2):
            a=self.read_nlines_and_split(file,n1,read_title=False)
            b.append(a)
        return np.transpose(b)

    def Helena_to_pFile(self,pFilename=''):
        '''
        Translate OMFIThelena class to pfile data structure

        :param pFilename: pFile to which Helena data is overwritten

        :return: pfile OMFITpFile structure that has ne, te and ti elements
        '''
        d1_data_to_pfile=['ne','te','ti','ni']
        lines = []

        pfile = OMFITpFile(pFilename)

        for key in d1_data_to_pfile:
            pfile[key] = self['1d'][key]
        return pfile

class OMFITmishkamap(SortedDict,OMFITascii):
    r"""
    OMFIT class used to interface with the mapping file for MISHKA

    :param filename: filename passed to OMFITmishkamap class

    :param \**kw: keyword dictionary passed to OMFITobject class, not currently used
    """
    def __init__(self,filename,**kw):
        OMFITascii.__init__(self,filename,**kw)
        SortedDict.__init__(self)
        self.dynaLoad=True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

        # Set up descriptions and units for all 0d, 1d and 2d dictionary entries

        self.descriptions=SortedDict()
        self.descriptions['0d']=SortedDict()
        self.descriptions['0d']['npsi']='number of flux surfaces'
        self.descriptions['0d']['nchi']='number of points on each flux surface'
        self.descriptions['1d']=SortedDict()
        self.descriptions['ends']=SortedDict()
        self.descriptions['2d']=SortedDict()
        self.descriptions['1d']['cs']='sqrt(psi)'
        self.descriptions['1d']['q']='Safety factor'
        self.descriptions['ends']['dqsend']='dq/ds in core and boundary'
        self.descriptions['1d']['dqs']='dq/ds'
        self.descriptions['1d']['curj']='current density'
        self.descriptions['ends']['dcurj']='dcurj/ds in core and boundary'
        self.descriptions['1d']['chi']='chi coordinate'
        self.descriptions['2d']['GEM11']='Grad psi ^ 2'
        self.descriptions['2d']['GEM12']='Grad psi x Grad chi'
        self.descriptions['0d']['cpsurf']='Normalised plasma current'
        self.descriptions['0d']['radius']='Geometric centre'
        self.descriptions['2d']['GEM33']='Grad phi ^ 2'
        self.descriptions['0d']['Raxis'] = 'R on axis'
        self.descriptions['1d']['p0']='pressure'
        self.descriptions['ends']['dpds']='dp/ds in core and boundary'
        self.descriptions['1d']['RBphi']='Poloidal current function'
        self.descriptions['ends']['dfds']='df/ds in core and boundary'
        self.descriptions['1d']['vx']='Vacuum interface for psi'
        self.descriptions['1d']['vy']='Vacuum interface for chi'
        self.descriptions['0d']['eps'] = 'Inverse aspect ratio'
        self.descriptions['2d']['xout']='Normalised R for grid points'
        self.descriptions['2d']['yout']='Normalised Z for grid points'

        self.units=SortedDict()
        self.units['1d']=SortedDict()
        self.units['2d']=SortedDict()
        self.units['ends']=SortedDict()
        self.units['1d']['cs']=''
        self.units['1d']['chi']=''
        self.units['1d']['p0']='Pa'
        self.units['1d']['q']=''
        self.units['1d']['dqs']=''
        self.units['1d']['curj']=''
        self.units['1d']['RBphi']='Tm'
        self.units['1d']['vx']=''
        self.units['1d']['vy']=''
        self.units['2d']['GEM11']=''
        self.units['2d']['GEM12']=''
        self.units['2d']['xout']=''
        self.units['2d']['yout']=''
        self.units['2d']['GEM33']=''
        self.units['ends']['dqsend']=''
        self.units['ends']['dcurj']=''
        self.units['ends']['dpds']='Pa'
        self.units['ends']['dfds']='Tm'

        # Initialise all the dictionaries with dummy parameters

        self['0d']=SortedDict()
        self['1d']=SortedDict()
        self['2d']=SortedDict()
        self['ends']=SortedDict()
        for key in self.descriptions['1d'].keys():
            self['1d'][key]=OMFITncData()
            self['1d'][key]['data']=np.array([0])
            self['1d'][key]['description']=self.descriptions['1d'][key]
            self['1d'][key]['units']=self.units['1d'][key]
        for key in self.descriptions['2d'].keys():
            self['2d'][key]=OMFITncData()
            self['2d'][key]['data']=np.array([[0]])
            self['2d'][key]['description']=self.descriptions['2d'][key]
            self['2d'][key]['units']=self.units['2d'][key]
        for key in self.descriptions['0d'].keys():
            self['0d'][key]=OMFITncData()
            self['0d'][key]['description']=self.descriptions['0d'][key]
            self['0d'][key]['data']=0
            self['0d'][key]['units']=''
        for key in self.descriptions['ends'].keys():
            self['ends'][key]=OMFITncData()
            self['ends'][key]['data']=np.array([0,0])
            self['ends'][key]['description']=self.descriptions['ends'][key]
            self['ends'][key]['units']=self.units['ends'][key]

        columns_map = 4

        f=os.path.getsize(self.filename)
        if f==0:
            return

        # Fill dictionaries from the file
        with open(self.filename,'r') as file:
            self['0d']['npsi']['data']=int(self.read_nlines_and_split(file,1))
            mod1=int(np.ceil(float(self['0d']['npsi']['data']+1)/columns_map - \
                          (self['0d']['npsi']['data']+1)//columns_map))
            nlines1=int((self['0d']['npsi']['data']+1)/columns_map)+mod1
            mod3=int(np.ceil(float(self['0d']['npsi']['data'])/columns_map - \
                          (self['0d']['npsi']['data'])//columns_map))
            nlines3=int(self['0d']['npsi']['data']//columns_map)+mod3
            npsi=self['0d']['npsi']['data']
            self['1d']['cs']['data']=self.read_nlines_and_split(file,nlines1)
            psi_norm=self['1d']['cs']['data']**2
            self['1d']['q']['data'] = self.read_nlines_and_split(file,nlines1)
            self['ends']['dqsend']['data'] = self.read_nlines_and_split(file,1)
            self['1d']['dqs']['data'] = self.read_nlines_and_split(file,nlines3)
            self['1d']['curj']['data'] = self.read_nlines_and_split(file,nlines1)
            self['ends']['dcurj']['data'] = self.read_nlines_and_split(file,1)
            self['0d']['nchi']['data']=int(self.read_nlines_and_split(file,1))
            mod2=int(np.ceil((self['0d']['nchi']['data'])/columns_map - \
                          (self['0d']['nchi']['data'])//columns_map))
            nlines2=int((self['0d']['nchi']['data'])/columns_map)+mod2
            nchi=self['0d']['nchi']['data']
            self['1d']['chi']['data'] = self.read_nlines_and_split(file,nlines2)
            self['2d']['GEM11']['data'] = self.read_2d_array(file,npsi,nchi)
            self['2d']['GEM12']['data'] = self.read_2d_array(file,npsi,nchi)
            (self['0d']['cpsurf']['data'], self['0d']['radius']['data']) = self.read_nlines_and_split(file,1)
            self['2d']['GEM33']['data'] = self.read_2d_array(file,npsi,nchi)
            self['0d']['Raxis']['data']=float(self.read_nlines_and_split(file,1))
            self['1d']['p0']['data'] = self.read_nlines_and_split(file,nlines1)
            self['ends']['dpds']['data'] = self.read_nlines_and_split(file,1)
            self['1d']['RBphi']['data'] = self.read_nlines_and_split(file,nlines1)
            self['ends']['dfds']['data'] = self.read_nlines_and_split(file,1)
            self['1d']['vx']['data'] = self.read_nlines_and_split(file,nlines2)
            self['1d']['vy']['data'] = self.read_nlines_and_split(file,nlines2)
            self['0d']['eps']['data']=float(self.read_nlines_and_split(file,1))
            self['2d']['xout']['data'] = self.read_2d_array(file,npsi,nchi)
            self['2d']['yout']['data'] = self.read_2d_array(file,npsi,nchi)

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        The variables need to be written in particular order and format for MISHKA.

        :return: None
        """

        order = ['npsi','cs','q','dqsend','dqs','curj','dcurj','nchi','chi',\
                 'GEM11','GEM12','cpsurf','radius','GEM33','Raxis','p0','dpds',\
                 'RBphi','dfds','vx','vy','eps','xout','yout']

        with open(self.filename,'w') as f:
            for key in order:
                if key in self['0d']:
                    endline = True
                    if key == 'cpsurf':
                        endline = False
                    if key == 'npsi' or key == 'nchi':
                        f.write(' %i\n'%self['0d'][key]['data'])
                    else:
                        self.write_mishka_mapping_lines(f,self['0d'][key]['data'],endline=endline)
                elif key in self['1d']:
                    self.write_mishka_mapping_lines(f,self['1d'][key]['data'])
                elif key in self['2d']:
                    self.write_mishka_mapping_lines(f,self['2d'][key]['data'])
                elif key in self['ends']:
                    self.write_mishka_mapping_lines(f,self['ends'][key]['data'])
        return None

    def plot(self):
        """
        Method used to plot all profiles, one in a different subplots

        :return: None
        """
        plots =[]
        for key in self['1d']:
            if len(self['1d'][key]['data']) == int(self['0d']['npsi']['data']) + 1:
                plots.append(key)
        nplot=len(plots)
        cplot=np.floor(np.sqrt(nplot)/2.)*2
        rplot=np.ceil(nplot*1.0/cplot)
        pyplot.figure()
        pyplot.subplots_adjust(wspace=0.35,hspace=0.0)
        pyplot.ioff()
        try:
            for k,item in enumerate(plots):
                r=np.floor(k*1.0/cplot)
                c=k-r*cplot

                if k==0:
                    ax1=pyplot.subplot(rplot,cplot, r*(cplot)+c+1 )
                    ax=ax1
                else:
                    ax=pyplot.subplot(rplot,cplot, r*(cplot)+c+1, sharex=ax1)
                ax.ticklabel_format(style='sci', scilimits=(-3,3))
                x=self['1d']['cs']['data']**2

                pyplot.plot(x,self['1d'][item]['data'],'.-')
                pyplot.text(0.5, 0.9,item,
                            horizontalalignment='center',
                            verticalalignment='top',
                            size='medium',
                            transform = ax.transAxes)

                if k<len(self['1d'])-cplot:
                    pyplot.setp( ax.get_xticklabels(), visible=False)
                else:
                    pyplot.xlabel('$\\psi$')

                pyplot.xlim(min(x),max(x))

        finally:
            pyplot.draw()
            pyplot.ion()

        pyplot.figure()

        try:
            # Plot all the metric elements in contour plots

            numbchi=20
            w = self['0d']['nchi']['data']
            step = w//numbchi
            ax1=pyplot.subplot(2,2,1)
            pyplot.plot(self['2d']['xout']['data'][:,::step],self['2d']['yout']['data'][:,::step],'-k')
            pyplot.axis('equal')
            pyplot.title('Straight field line grid')

            ax2=pyplot.subplot(2,2,2)
            x=self['2d']['xout']['data'].flatten()
            y=self['2d']['yout']['data'].flatten()
            z=self['2d']['GEM11']['data'].flatten()
            pyplot.tricontourf(x,y,z)
            pyplot.axis('equal')
            pyplot.title(r'$\nabla\psi\cdot\nabla\psi$')
            pyplot.colorbar()

            ax3=pyplot.subplot(2,2,3)
            x=self['2d']['xout']['data'].flatten()
            y=self['2d']['yout']['data'].flatten()
            z=self['2d']['GEM12']['data'].flatten()
            pyplot.tricontourf(x,y,z)
            pyplot.axis('equal')
            pyplot.title(r'$\nabla\psi\cdot\nabla\chi$')
            pyplot.colorbar()

            ax4=pyplot.subplot(2,2,4)
            x=self['2d']['xout']['data'].flatten()
            y=self['2d']['yout']['data'].flatten()
            z=self['2d']['GEM33']['data'].flatten()
            pyplot.tricontourf(x,y,z)
            pyplot.axis('equal')
            pyplot.title(r'$\nabla\phi\cdot\nabla\phi$')
            pyplot.colorbar()
        finally:
            pyplot.draw()
            pyplot.ion()

    def write_mishka_mapping_lines(self,file,mat, n=4,endline=True):
        '''
        Writes a matrix in the MISHKA mapping line format

        : param file : file to write the data

        : param mat: Matrix to be written, can be 1 or 2 dimensional

        : title : title for the data

        : param n : number of columns

        '''

        try:
            width = np.size(mat,1)
        except IndexError:
            width = 1
        try:
            length = np.size(mat,0)
        except IndexError: # scalar
            if endline:
                file.write(' %16.8e\n'%mat)
            else:
                file.write('%16.8e'%mat)
            return
        lines = []
        if width == 1: # 1D case
            width = length
            length = 1
        for row in range(length):
            mod1 = width%n
            if length > 1:
                slice = mat[row,:]
            else:
                slice = mat
            for column in range(width//n) :
                writeparam = slice[column * n : column * n + n ]
                lines.append(' '.join(str('%16.8e'%e) for e in writeparam))
                if endline:
                    lines.append('\n')
            if mod1 > 0:
                end_position = (width//n) * n
                remain = slice[end_position:]
                lines.append(' '.join(str('%16.8e'%e) for e in remain))
                if endline:
                    lines.append('\n')
        for line in lines:
            file.write(line)
        return

    def read_nlines_and_split(self,file,n):
        b=[]
        for i in range(n):
            ifl=file.readline()
            a=ifl.split()
            for arg in a:
                b.append(float(arg))
        return np.array(b)

    def read_2d_array(self,file,n1,n2,columns=4):
        b=[]
        ntot = n1*n2
        mod = int(np.ceil(ntot/columns - ntot//columns))
        nlines = ntot // columns + mod
        a=self.read_nlines_and_split(file,nlines)
        b = a.reshape(n1,n2)
        return(b)

class OMFIThelenaout(SortedDict,OMFITascii):
    r"""
    OMFIT class used to interface with Helena output file

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """
    def __init__(self,filename,**kw):
        OMFITascii.__init__(self,filename,**kw)
        SortedDict.__init__(self)

        '''Data identifiers for stored 1D data in HELENA output file
        Directory entry is string  in the HELENA output file to find the array
        The 1st element lists the 1d-array names in the following matrix
        The 2nd element identifies the radial coordinate column
        The 3rd eleement tells to what power the radial coordinate has to be raisesd to get poloidsal flux
        The 4th element lists the data columns
        The 5th element tells the end string
        '''

        self.dataident1d={}
        self.dataident1d['VOL '] = [['volume','area'],[1],[1],[7,9],'**********']
        self.dataident1d['ALPHA'] = [['q','shear','alpha','ball'],[1],[1],[3,5,6,8],'**********']
        self.dataident1d['Pa'] = [['p','ne','Te','Ti','Jboot','Jtot','s'],[0],[2],[1,2,3,4,5,8,0],'*******']
        self.dataident1d['JPHI'] = [['jz','circ'],[0],[2],[1,2],'*******']
        self.dataident1d['SIG'] = [['Fcirc','nue','nui','sig_spitzer','sig_neo'],[0],[2],[2,3,4,5,6],'*******']

        '''Data identifiers for stored 1D data in HELENA output file
        Directory entry is string  in the HELENA output file to find the
        parameter that is the value of the directory entry
        '''

        self.dataident0d={}
        self.dataident0d['TOTAL CURRENT'] = 'Ip'
        self.dataident0d['MAGNETIC FIELD'] = 'Bt'
        self.dataident0d['PSI ON BOUNDARY'] = 'psib'
        self.dataident0d['POLOIDAL BETA'] = 'betap'
        self.dataident0d['NORM. BETA'] = 'betan'
        self.dataident0d['TOROIDAL BETA'] = 'betat'
        self.dataident0d['INDUCTANCE'] = 'li'
        self.dataident0d['ZEFF'] = 'Zeff'
        self.dataident0d['MAJOR RADIUS'] = 'Rgeo'
        self.dataident0d['RADIUS (a)'] = 'a'

        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

    # Set up descriptions and units for all 0d, 1d and dictionary entries

        self.descriptions=SortedDict()
        self.descriptions['0d']=SortedDict()
        self.descriptions['0d']['Ip']='Plasma current'
        self.descriptions['0d']['Bt']='Vacuum toroidal field'
        self.descriptions['0d']['Rgeo']='Geometric Axis'
        self.descriptions['0d']['a']='Minor radius'
        self.descriptions['0d']['betap']='Poloidal beta'
        self.descriptions['0d']['betat']='Toroidal beta'
        self.descriptions['0d']['betan']='Normalised beta'
        self.descriptions['0d']['li']='Internal inductance'
        self.descriptions['0d']['psib']='Total poloidal flux'
        self.descriptions['0d']['Zeff']='Effective charge'
        self.descriptions['1d']=SortedDict()
        self.descriptions['1d']['alpha']='Normalised pressure gradient'
        self.descriptions['1d']['p']='Plasma pressure'
        self.descriptions['1d']['jz']='Flux surface averaged current density'
        self.descriptions['1d']['q']='Safety factor'
        self.descriptions['1d']['shear']='Magnetic shear'
        self.descriptions['1d']['ball']='Ballooning stability <1 unstable'
        self.descriptions['1d']['ne']='Electron density'
        self.descriptions['1d']['Te']='Electron temperature'
        self.descriptions['1d']['Ti']='Ion temperature'
        self.descriptions['1d']['Jboot']='Bootstrap current density'
        self.descriptions['1d']['Jtot']='Total parallel current density'
        self.descriptions['1d']['circ']='Flux surface circumference'
        self.descriptions['1d']['Fcirc']='Passing particle fraction'
        self.descriptions['1d']['nue']='Electron collisionality'
        self.descriptions['1d']['nui']='Ion collisionality'
        self.descriptions['1d']['sig_spitzer']='Spitzer resitivity'
        self.descriptions['1d']['sig_neo']='Neo-classical resistivity'
        self.descriptions['1d']['volume']='Plasma volume'
        self.descriptions['1d']['area']='Cross-section area'
        self.descriptions['1d']['s']='normalised radius (sqrt(psi))'

        self.units=SortedDict()
        self.units['0d']=SortedDict()
        self.units['0d']['Ip']='MA'
        self.units['0d']['Bt']='T'
        self.units['0d']['Rgeo']='m'
        self.units['0d']['a']='m'
        self.units['0d']['betap']=''
        self.units['0d']['betat']=''
        self.units['0d']['betan']=''
        self.units['0d']['li']=''
        self.units['0d']['psib']='Wb/rad'
        self.units['0d']['Zeff']=''
        self.units['1d']=SortedDict()
        self.units['1d']['alpha']=''
        self.units['1d']['p']='Pa'
        self.units['1d']['jz']='A/m^2'
        self.units['1d']['q']=''
        self.units['1d']['shear']=''
        self.units['1d']['ball']=''
        self.units['1d']['ne']='10^19 m^-3'
        self.units['1d']['Te']='eV'
        self.units['1d']['Ti']='eV'
        self.units['1d']['Jboot']='A/m^2'
        self.units['1d']['Jtot']='A/m^2'
        self.units['1d']['circ']='m'
        self.units['1d']['Fcirc']=''
        self.units['1d']['nue']=''
        self.units['1d']['nui']=''
        self.units['1d']['sig_spitzer']=''
        self.units['1d']['sig_neo']=''
        self.units['1d']['volume']='m^3'
        self.units['1d']['area']='m^2'
        self.units['1d']['s']=''

#   Initialise all the dictionaries with dummy parameters.

        self['0d']=SortedDict()
        self['1d']=SortedDict()

        for key in self.descriptions['1d'].keys():
            self['1d'][key]=OMFITncData()
            self['1d'][key]['data']=np.array([0])
            self['1d'][key]['description']=self.descriptions['1d'][key]
            self['1d'][key]['psinorm']=np.array([0])
            self['1d'][key]['units']=self.units['1d'][key]
        for key in self.descriptions['0d'].keys():
            self['0d'][key]=OMFITncData()
            self['0d'][key]['description']=self.descriptions['0d'][key]
            self['0d'][key]['data']=0
            self['0d'][key]['units']=self.units['0d'][key]


        #read the file
        f=os.path.getsize(self.filename)
        if f==0:
            return

        #Reads the file content to the dictionaries.
        #The dataident (0d and 1d) tells which strings are used to locate the data

        with open(self.filename,'r') as file:
            while True:
                line = file.readline()
                if line == '':
                    break
                for key in self.dataident1d:
                    if line.find(key) > -1:
                        self.read_1d_vectors(file,self.dataident1d[key])
                for key in self.dataident0d:
                    if line.find(key) > -1:
                        self['0d'][self.dataident0d[key]] = OMFITncData()
                        self['0d'][self.dataident0d[key]]['description'] = self.descriptions['0d'][self.dataident0d[key]]
                        self['0d'][self.dataident0d[key]]['units'] = self.units['0d'][self.dataident0d[key]]
                        for num in line.split():
                            try:
                                self['0d'][self.dataident0d[key]]['data'] = float(num)
                                break
                            except ValueError:
                                continue
                                # not a number

        self['1d']['volume']['data'] *=  self['0d']['Rgeo']['data'] * self['0d']['a']['data'] ** 2
        self['1d']['area']['data'] *=  self['0d']['a']['data'] ** 2
        self['0d']['Ip']['data'] /=  1000
        self['0d']['betan']['data'] *=  100
        self['1d']['Jboot']['data'] /= abs(self['0d']['Bt']['data'])
        self['1d']['Jtot']['data'] /= abs(self['0d']['Bt']['data'])

        return

    def plot(self):
        """
        Method used to plot all profiles, one in a different subplots

        :return: None
        """
        nplot=len(self['1d'])
        cplot=np.floor(np.sqrt(nplot)/2.)*2
        rplot=np.ceil(nplot*1.0/cplot)
        pyplot.subplots_adjust(wspace=0.35,hspace=0.0)
        pyplot.ioff()
        try:
            for k,item in enumerate(self['1d']):
                r=np.floor(k*1.0/cplot)
                c=k-r*cplot

                if k==0:
                    ax1=pyplot.subplot(rplot,cplot, r*(cplot)+c+1 )
                    ax=ax1
                else:
                    ax=pyplot.subplot(rplot,cplot, r*(cplot)+c+1, sharex=ax1)
                ax.ticklabel_format(style='sci', scilimits=(-3,3))
                if 'psinorm' not in self['1d'][item]:
                    printi('Can\'t plot %s because no psinorm attribute'%item)
                    continue
                x=self['1d'][item]['psinorm']

                if item == 'nue' or item == 'nui':
                    pyplot.semilogy(x,self['1d'][item]['data'],'-')
                else:
                    pyplot.plot(x,self['1d'][item]['data'],'-')
                pyplot.text(0.5, 0.9,item,
                            horizontalalignment='center',
                            verticalalignment='top',
                            size='medium',
                            transform = ax.transAxes)

                if k<len(self['1d'])-cplot:
                    pyplot.setp( ax.get_xticklabels(), visible=False)
                else:
                    pyplot.xlabel('$\\psi$')

                pyplot.xlim(min(x),max(x))

        finally:
            pyplot.draw()
            pyplot.ion()

    def read_1d_vectors(self,f,dataident):

        '''
        Method to read 1D vectors from HELENA output file.
        param f: File to read the data. It is assumed that the file is at
                 the right position to start reading
        param dataident: a list containing 4 elements:
                            [0] : names of the data to be read. The global 1d dictionary will use these names.
                            [1] : The column indicating the location of the psinorm vector
                            [2] : The exponent needed to produce psinorm :
                                1 = the data in file already is already psinorm
                                2 = the data is in sqrt(psinorm)
                            [3] : Column numbers for the data
                            [4] : A string indicating the end of data
        '''

        mat = self.read_matrix(f,end=dataident[4])
        index = 0
        for key in dataident[0]:
            self['1d'][key] = OMFITncData()
            self['1d'][key]['data'] = mat[:,dataident[3][index]]
            self['1d'][key]['psinorm'] = np.squeeze(mat[:,dataident[1]]**dataident[2])
            self['1d'][key]['description'] = self.descriptions['1d'][key]
            self['1d'][key]['units'] = self.units['1d'][key]
            index += 1
        return

    def read_matrix(self,f,end='*',separator=' '):
        '''
        Method that reads a 2D ASCII matrix and turns it into a np array
        Reads until the end string is found
        '''

        line=f.readline()
        eof=False
        mat=[]
        while True:
            line = f.readline()
            if line == '':
                eof=True
                break
            if (line.find(end) > -1) or (len(line.split()) == 0):
                break
            mat.append(np.fromstring(line,dtype='float',sep=separator))

        return(np.asarray(mat))

    def update_aEQDSK(self, aEQDSK):
        aEQDSK['vout'] = self['1d']['volume']['data'][-1]
        aEQDSK['areao'] = self['1d']['area']['data'][-1]
        aEQDSK['betap'] = self['0d']['betap']['data']
        aEQDSK['betan'] = self['0d']['betan']['data']
        aEQDSK['betat'] = self['0d']['betat']['data']
        aEQDSK['bt0vac'] = self['0d']['Bt']['data']
        aEQDSK['rcencm'] = self['0d']['Rgeo']['data']*100
        aEQDSK['bcentr'] = self['0d']['Bt']['data']
        aEQDSK['pasmat'] = self['0d']['Ip']['data']*1e6
        aEQDSK['cpasma'] = self['0d']['Ip']['data']*1e6
        aEQDSK['aout'] = self['0d']['a']['data']*100
        aEQDSK['rout'] = self['0d']['a']['data']*100 + self['0d']['Rgeo']['data']
        aEQDSK['qqmin'] = min(self['1d']['q']['data'])

    def p_jz_q_plot(self):
        ax1=pyplot.subplot(3,1,1)
        pyplot.plot(self['1d']['p']['psinorm'],self['1d']['p']['data'])
        pyplot.setp( ax1.get_xticklabels(), visible=False)
        ax2=pyplot.subplot(3,1,2,sharex=ax1)
        pyplot.plot(self['1d']['jz']['psinorm'],self['1d']['jz']['data'])
        pyplot.setp( ax2.get_xticklabels(), visible=False)
        ax3=pyplot.subplot(3,1,3,sharex=ax1)
        pyplot.plot(self['1d']['q']['psinorm'],self['1d']['q']['data'])
        pyplot.xlabel('$\\psi$')

class OMFIThelenainput(OMFITnamelist):
    '''
    Class for the input namelist for HELENA
    '''

    def profiles_from_pfile(self,pfile):
        '''
        Reconstructs Te, Ne, Ti and Zeff profiles from a pFile
        '''

        npts=self['PROFILE']['NPTS']
        zimp = max(pfile['N Z A']['Z'])
        self['PHYS']['ZIMP'] = zimp
        teprof = interp1d(pfile['te']['psinorm'],pfile['te']['data'],kind='cubic')
        neprof = interp1d(pfile['ne']['psinorm'],pfile['ne']['data']*10.0,kind='cubic')
        niprof = interp1d(pfile['ni']['psinorm'],pfile['ni']['data']*10.0,kind='cubic')
        tiprof = interp1d(pfile['ti']['psinorm'],pfile['ti']['data'],kind='cubic')
        psihelena=np.linspace(0,1,npts)
        self['PROFILE']['TEPROF'] = teprof(psihelena)
        self['PROFILE']['NEPROF'] = neprof(psihelena)
        self['PROFILE']['TIPROF'] = tiprof(psihelena)
        self['PROFILE']['ZPR'] = zimp + 1 - niprof(psihelena)/neprof(psihelena) * zimp
        self['PHYS']['IDETE'] = 10

    def read_from_eqdsk(self,EQDSK,boundary_flx=0.996, nf=256, boundary_plot = True,bmultip=1.0,boundary=None,symmetric=False):

        import copy

        '''
        Reads a gEQDSK file, extracts the global parameters and the
        boundary shape from that. Calculates HELENA parameters and
        reconstructs the boundary using the fourier representation.
        '''

        mu0=4e-7*np.pi
        if boundary_flx == 1:
            if boundary == None:
                rb=EQDSK['RBBBS']
                zb=EQDSK['ZBBBS']
            else:
                rb=boundary['RBBBS']
                zb=boundary['ZBBBS']
        else:
            if isinstance(boundary,fluxSurfaces):
                flx = boundary
            else:
                flx = copy.deepcopy(EQDSK['fluxSurfaces'])
            flx.findSurfaces(np.linspace(boundary_flx-0.01,boundary_flx,3),map=None)
            rb=flx['flux'][2]['R']
            zb=flx['flux'][2]['Z']

        bndfour = fourier_boundary(nf,rb,zb,symmetric=symmetric)
        try:
            print('EFIT Rvac = %f, Rgeo from boundary = %f'%(EQDSK['RVTOR'],bndfour.r0))
            bcentr=abs(EQDSK['BCENTR']/bndfour.r0*EQDSK['RVTOR'])
        except KeyError:
            print('EFIT Rvac = %f, Rgeo from boundary = %f'%(EQDSK['RCENTR'],bndfour.r0))
            bcentr=abs(EQDSK['BCENTR']/bndfour.r0*EQDSK['RCENTR'])
        self.bsign=EQDSK['BCENTR']/abs(EQDSK['BCENTR'])

        self['SHAPE']['MHARM'] = nf
        self['SHAPE']['MFM'] = nf

        self['SHAPE']['FM'] = np.zeros(nf)
        if symmetric:
            self['SHAPE']['FM'] = bndfour.realfour
            self['SHAPE']['IAS'] = 0
        else:
            self['SHAPE']['FM'][0::2] = bndfour.realfour
            self['SHAPE']['FM'][1::2] = bndfour.imagfour
            self['SHAPE']['IAS'] = 1

        # The PROFILE part of the namelist
        self['PROFILE']['NPTS'] = EQDSK['NW']
        self['PROFILE']['ICUR'] = 0
        self['PROFILE']['IPAI'] = 7
        self['PROFILE']['IGAM'] = 7
        self['PROFILE']['DPR'] = EQDSK['PPRIME']
        self['PROFILE']['DF2'] = EQDSK['FFPRIM']
        if self['PROFILE']['DF2'][0] == 0.0:
             printw('FFprime zero in the centre, changing FFP[0] to 0.01 * FFP[1]')
             self['PROFILE']['DF2'][0] = self['PROFILE']['DF2'][1] * 0.01


        # The PHYS part of the self
        if 'BETAP' in self['PHYS']:
            del self['PHYS']['BETAP']

        self['PHYS']['B'] = bndfour.r0*bndfour.r0*mu0*self['PROFILE']['DPR'][0]/self['PROFILE']['DF2'][0] * bmultip
        self['PHYS']['XIAB'] = abs(EQDSK['CURRENT']*mu0/bcentr/bndfour.amin)
        self['PHYS']['RVAC'] = bndfour.r0
        self['PHYS']['EPS'] = bndfour.amin/bndfour.r0
        self['PHYS']['BVAC'] = bcentr
        self['PHYS']['ALFA'] = bndfour.amin*bndfour.amin*abs(bcentr/(EQDSK['SIBRY']-EQDSK['SIMAG']))

        def is_power_of_two(n):
            """Return True if n is a power of two."""
            if n <= 0:
                return False
            else:
                return n & (n - 1) == 0

        if symmetric:
            if is_power_of_two(self['NUM']['NCHI']):
                self['NUM']['NCHI'] += 1
        else:
            if not is_power_of_two(self['NUM']['NCHI']):
                self['NUM']['NCHI'] -= 1

        if boundary_plot:
            (rf,zf)=bndfour.reconstruct_boundary()
            pyplot.plot(rf,zf,'b-o')
            pyplot.plot(rb,zb,'r')
            pyplot.plot(EQDSK['RBBBS'],EQDSK['ZBBBS'],'k')
            pyplot.axis('equal')
            pyplot.draw()

    def read_from_gato(self,dskgato, nf=256,bmultip=1.0, dskbalfile=None):
        '''
        Reads a dskgato file, extracts the global parameters and the
        boundary shape from that. Calculates HELENA parameters and
        reconstructs the boundary using the fourier representation.
        '''

        mu0=4e-7*np.pi

        rb=dskgato['RBBBS']
        zb=dskgato['ZBBBS']

        bndfour = fourier_boundary(nf,rb,zb,symmetric=True)

        print('GATO Rvac = %f, Rgeo from boundary = %f'%(dskgato['RCENTR'],bndfour.r0))
        bcentr=dskgato['BCENTR']/bndfour.r0*dskgato['RCENTR']

        self['SHAPE']['MHARM'] = int(nf/2)
        self['SHAPE']['MFM'] = nf
        self['SHAPE']['IAS'] = 0

        self['SHAPE']['FM'] = np.zeros(nf)
        self['SHAPE']['FM'] = bndfour.realfour

        # The PROFILE part of the namelist
        gato_psinorm = (dskgato['PSI']-dskgato['PSI'][0])/(dskgato['PSI'][-1]-dskgato['PSI'][0])
        self['PROFILE']['NPTS'] = dskgato['NSURF']
        self['PROFILE']['ICUR'] = 0
        self['PROFILE']['IPAI'] = 7
        self['PROFILE']['IGAM'] = 7
        splined_ffp=interp1d(gato_psinorm,dskgato['FFPRIM'],kind='cubic')
        splined_pp=interp1d(gato_psinorm,dskgato['PPRIME'],kind='cubic')
        psinorm = np.linspace(0,1,dskgato['NSURF'])

        if dskbalfile:
            dskbal_psinorm=(dskbalfile['poloidal flux--psiv']-dskbalfile['poloidal flux--psiv'][0])/\
            (dskbalfile['poloidal flux--psiv'][-1]-dskbalfile['poloidal flux--psiv'][0])
            splined_ne=interp1d(dskbal_psinorm,dskbalfile['electron density (cm^-3)']/1e13,kind='cubic')
            splined_te=interp1d(dskbal_psinorm,dskbalfile['electron temperature (eV)']/1e3,kind='cubic')
            splined_ti=interp1d(dskbal_psinorm,dskbalfile['ion temperature (eV)']/1e3,kind='cubic')

            self['PROFILE']['NEPROF'] = splined_ne(psinorm)
            self['PROFILE']['TEPROF'] = splined_te(psinorm)
            self['PROFILE']['TIPROF'] = splined_ti(psinorm)
            self['PHYS']['IDETE'] = 10

        self['PROFILE']['DPR'] = splined_pp(psinorm)
        self['PROFILE']['DF2'] = splined_ffp(psinorm)
        if self['PROFILE']['DF2'][0] == 0.0:
             self['PROFILE']['DF2'][0] = self['PROFILE']['DF2'][1]  /2.0

        # The PHYS part of the self
        if 'BETAP' in self['PHYS']:
            del self['PHYS']['BETAP']

        self['PHYS']['B'] = bndfour.r0*bndfour.r0*mu0*dskgato['PPRIME'][0]/dskgato['FFPRIM'][0] * bmultip
        self['PHYS']['XIAB'] = dskgato['CURRENT']*mu0/bcentr/bndfour.amin
        self['PHYS']['RVAC'] = bndfour.r0
        self['PHYS']['EPS'] = bndfour.amin/bndfour.r0
        self['PHYS']['BVAC'] = bcentr
        self['PHYS']['ALFA'] = bndfour.amin*bndfour.amin*abs(bcentr/(dskgato['SIBRY']-dskgato['SIMAG']))