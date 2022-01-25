import os, datetime, logging
from struct import unpack
import numpy as np

from aug_sfutils import sfdics, sfh_rw, sfobj, manage_ed, parse_kwargs, str_byt, libddc, getlastshot

PPGCLOCK = [1e-6, 1e-5, 1e-4, 1e-3]

logger = logging.getLogger('aug_sfutils.sfread')
date_fmt = '%Y-%m-%d'
logger.setLevel(logging.INFO)

for key, val in sfdics.obj_name.items():
    exec('%s=%d' %(val, key))
for key, val in sfdics.cal_type.items():
    exec('%s=%d' %(val, key))
for key, val in sfdics.fmt2descr.items():
    exec('%s=%d' %(val, key))
for key, val in sfdics.tbtype_d.items():
    exec('%s=%d' %(val, key))


def read_other_sf(*args, **kwargs):

    return SFREAD(*args, **kwargs)


def getcti_ts06(nshot):
    """
    Gets the absolute time (ns) of a discharge trigger 
    """
    diag = 'CTI'
    cti = SFREAD(nshot, diag)
    try:
        cdev = cti.getdevice('LAM')
        ts06 = cdev['PhyReset']
        if ts06 == 0:
            ts06 = cdev['TS06']
        if ts06 == 0:
            ts06 = cdev['CT_TS06']
    except: # shot < 35318
        cdev = cti.getdevice('TS6')
        ts06 = cdev['TRIGGER']
        logger.debug('getcti_ts06 %d', ts06)
    if ts06 < 1e15:
        ts06 = None
    return ts06


def getgc(nshot=30136):
    """
    Returns first wall contours for plotting
    """
    ygc_sf = [1996, 8646, 8650, 9401, 11300, 11301, 11320, 12751, 13231, 14051, 14601, 16310, 16315, 18204, 19551, 21485, 25891, 30136]
    ygc_sf = np.array(ygc_sf)
    nshot = np.max(ygc_sf[ygc_sf <= nshot])
    ygc = SFREAD(nshot, 'YGC')
    if ygc is not None:
        rrgc     = ygc.getobject('RrGC')
        zzgc     = ygc.getobject('zzGC')
        inxlen   = ygc.getobject('inxlen')
        flag_use = ygc.getobject('ixplin')
        gcnames  = ygc.getobject('chGCnm')

    comp_d = {}

    inxbeg = np.cumsum(np.append(0, inxlen))

    if gcnames is None:
        for jcom, leng in enumerate(inxlen):
            comp_d[jcom] = type('', (), {})() # empty object
            comp_d[jcom].r = rrgc[inxbeg[jcom]: inxbeg[jcom+1]]
            comp_d[jcom].z = zzgc[inxbeg[jcom]: inxbeg[jcom+1]]
    else:
        for jcom, lbl in enumerate(gcnames):
            lbl = str_byt.to_str(lbl)
            if flag_use[jcom] > 0:
                comp_d[lbl] = type('', (), {})()
                comp_d[lbl].r = rrgc[inxbeg[jcom]: inxbeg[jcom+1]]
                comp_d[lbl].z = zzgc[inxbeg[jcom]: inxbeg[jcom+1]]
    
    return comp_d


class SFREAD:
    """
    Class for reading ASDEX Upgrade shotfile data
    """

    def __init__(self, *args, **kwargs):
        """
        Opens a shotfile, reads the header
        """

        self.shot = None
        self.diag = None
        self.exp = None
        self.status = False
        self.open(*args, **kwargs)
        if len(args) > 2:
            logger.warning('More than 2 explicit arguments: only the first two (diag, shot) are retained')


    def open(self, *args, **kwargs):

        if 'sfh' in kwargs.keys():
            self.sfile = kwargs['sfh']
        if 'sf' in kwargs.keys():
            self.sfile = kwargs['sf']
        if hasattr(self, 'sfile'):
            self.shot = 0
            self.ed = 0
            self.diag = os.path.basename(self.sfile)[:3]

        else:

            n_args = len(args) 
            if n_args == 0:
                logger.warning('No argument given, need at least diag_name')
                return
            if isinstance(args[0], str) and len(args[0].strip()) == 3:
                diag = args[0].strip()
                if n_args > 1: 
                    if isinstance(args[1], (int, np.integer)):
                        nshot = args[1]
            elif isinstance(args[0], (int, np.integer)):
                nshot = args[0]
                if n_args > 1:
                    if isinstance(args[1], str) and len(args[1].strip()) == 3:
                        diag = args[1].strip()
            if 'nshot' not in locals(): 
                logger.warning('No argument is a shot number (int), taking last AUG shot')
                nshot = getlastshot.getlastshot()
            if 'diag' not in locals():
                diag = input('Please enter a diag_name (str(3), no delimiter):\n')

            exp = parse_kwargs.parse_kw( ('exp', 'experiment'), kwargs, default='AUGD')
            ed  = parse_kwargs.parse_kw( ('ed', 'edition'), kwargs, default=0)
            logger.debug('%d %s %s %d', nshot, diag, exp, ed)
            self.sfile, self.ed = manage_ed.sf_path(nshot, diag, exp=exp, ed=ed)
            if self.sfile is None:
                logger.error('Shotfile not found for %s:%s(%d) #%d', exp, diag, ed, nshot)
                return
            else:
                self.shot = nshot
                self.diag = diag.upper()
                self.exp  = exp  # unused herein, but useful docu

        logger.debug('Shotfile path: %s', self.sfile)
        if os.path.isfile(self.sfile):
            self.time = datetime.datetime.fromtimestamp(os.path.getctime(self.sfile))
            with open(self.sfile, 'rb') as f:
                byt_str = f.read(128000)
                if len(byt_str) < 128:
                    logger.error('Error: shotfile %s has < 128 bytes, ignored' %(self.sfile))
                    return
                self.sfh = sfh_rw.read_sfh(byt_str)
                self.status = True
        else:
            logger.error('Shotfile %s not found' %self.sfile)
            return

        logger.info('Fetching SF %s', self.sfile)
        self.objects = [ lbl for lbl, sfo in self.sfh.items() if sfo.obj_type in [SignalGroup, Signal, TimeBase, AreaBase] ]
        self.parsets = [ lbl for lbl, sfo in self.sfh.items() if sfo.obj_type in [Device, ParamSet] ]
        if 'ADDRLEN' in self.sfh.keys():
            size_fac = sfdics.addrsizes[self.sfh['ADDRLEN'].addrlen]
            for obj in self.sfh.keys():
                if hasattr(self.sfh[obj], 'address'):
                    self.sfh[obj].address *= size_fac
        self.cache = {}


    def __call__(self, name):

        if not self.status:
            return None
        if name not in self.cache.keys():
            if name in self.objects:
                self.cache[name] = self.getobject(name)
            elif name in self.parsets:
                self.cache[name] = self.getparset(name)
            else:
                logger.error('Signal %s:%s not found for shot #%d', self.diag, name, self.shot)
                return None
        return self.cache[name]


    def getchunk(self, start, length):
        """
        Reads the requested byteblock from the actual file, not the byt_str
        """
        rdata = None
        with open(self.sfile, 'rb') as f:
            f.seek(start)
            rdata = f.read(length)
        return rdata


    def gettimebase(self, obj):
        """
        Reads the timebase of a given SIG, SGR or AB
        """

        obj = str_byt.to_str(obj)
        if obj not in self.sfh.keys():
            logger.error('Sig/TB %s:%s not found for #%d', self.diag, obj, self.shot)
            return None
        sfo = self.sfh[obj]
        otyp = sfo.obj_type
        if otyp == TimeBase:
            return self.getobject(obj)
        elif otyp in (SignalGroup, Signal, AreaBase):
            for rel in sfo.relations:
                if self.sfh[rel].obj_type == TimeBase:
                    return self.getobject(rel)
        return None


    def getareabase(self, obj):
        """
        Reads the areabase of a given SIG or SGR
        """

        obj = str_byt.to_str(obj)
        if obj not in self.sfh.keys():
            logger.error('Sig/AB %s:%s not found for #%d', self.diag, obj, self.shot)
            return None
        sfo = self.sfh[obj]
        otyp = sfo.obj_type
        if otyp == AreaBase:
            return self.getobject(obj)
        elif otyp in (SignalGroup, Signal):
            for rel in sfo.relations:
                if self.sfh[rel].obj_type == AreaBase:
                    return self.getobject(rel)
        return None


    def getobject(self, obj, cal=False, nbeg=None, nend=None, tbeg=None, tend=None):
        """
        Reads the data of a given TB, AB, SIG or SGR
        """

        obj = str_byt.to_str(obj)
        data = None
        if obj not in self.sfh.keys():
            logger.error('Signal %s:%s not found for #%d', self.diag, obj, self.shot)
            return None

# Keep commented, to allow 1 cal and 1 uncal reading
#        if obj in self.cache.keys(): 
#            return cache[obj]

        sfo = self.sfh[obj]
        if sfo.status != 0:
            logger.error('Status of SF object %s is %d' %(obj, sfo.status))
            return None
        otyp = sfo.obj_type

        if tbeg is not None or tend is not None:
            if tend is None:
                tend = 10.
            if tbeg is None:
                tbeg = 0.
            tb = self.gettimebase(obj)
            jt_beg, jt_end = tb.searchsorted((tbeg, tend))
            if otyp in (Signal, TimeBase) or self.time_last(obj):
                return self.getobject(obj, nbeg=jt_beg, nend=jt_end)
            elif self.time_first(obj):
                return self.getobject(obj)[jt_beg: jt_end]
            else:
                logger.error('tbeg, tend keywords supported only when time is first or last dim')
                return None

        if otyp in (SignalGroup, Signal):
            shape_arr = np.array(sfo.index[::-1][:sfo.num_dims])
        elif otyp == TimeBase:
            shape_arr = np.array([sfo.n_steps])
        elif otyp == AreaBase:
            x = np.array([sfo.size_x, sfo.size_y, sfo.size_z, sfo.n_steps])
            shape_arr = x[x != 0]
        else:
            logger.error('Object %s is no signal, signalgroup, timebase nor areabase, skipping')
            return None

        dfmt = sfo.data_format
        logger.debug('TB %s %d %d %d', obj, otyp, sfo.length, dfmt)
        if otyp == TimeBase and sfo.length == 0:
            if sfo.tbase_type == PPG_prog: # e.g. END:T-LM_END
                data = self.ppg_time(obj)
            else:   # ADC_intern, e.g. DCN:T-ADC-SL
                data = (np.arange(sfo.n_steps, dtype=np.float32) - sfo.n_pre)/sfo.s_rate
            dout = sfobj.SFOBJ(data, sfho=sfo) # Add metadata
        else:
            if dfmt in sfdics.fmt2len.keys(): # char variable
                dlen = sfdics.fmt2len[dfmt]
                bytlen = np.prod(shape_arr) * dlen
                data = np.chararray(shape_arr, itemsize=dlen, buffer=self.getchunk(sfo.address, bytlen), order='F')
            else: # numerical variable
                sfmt = sfdics.fmt2struc[dfmt]
                type_len = np.dtype(sfmt).itemsize
                addr = sfo.address
                bytlen = np.prod(shape_arr) * type_len
                if otyp in (Signal, TimeBase) or self.time_last(obj):
                    if nbeg is None:
                        nbeg = 0
                    else:
                        byt_beg = nbeg*np.prod(shape_arr[:-1])
                        addr   += byt_beg*type_len
                        bytlen -= byt_beg*type_len
                        shape_arr[-1] -= nbeg
                    if nend is not None:
                        bytlen = (nend - nbeg)*np.prod(shape_arr[:-1])*type_len
                        shape_arr[-1] = nend - nbeg
                data = np.ndarray(shape_arr, '>%s' %sfmt, self.getchunk(addr, bytlen), order='F')

# LongLong in [ns] and no zero at TS06
            if otyp == TimeBase and dfmt == LONGLONG: # RMC:TIME-AD0, SXS:Time
                logger.debug('Before getts06 dfmt:%d addr:%d len:%d data1:%d, %d', dfmt, addr, bytlen, data[0], data[1])
                data = 1e-9*(data - self.getts06(obj))
                logger.debug('%d',  self.getts06(obj))

            dout = sfobj.SFOBJ(data, sfho=sfo) # Add metadata
            dout.calib = False
# Calibrated signals and signal groups
            if otyp in (SignalGroup, Signal):
                if cal:
                    dout = self.raw2calib(dout)
                    if self.diag in ('DCN', 'DCK', 'DCR'):
                        dout.phys_unit = '1/m^2'

        return dout


    def ppg_time(self, tbobj): # Bug MAG:27204
        """
        Returns the time-array in [s] for TB of type PPG_prog
        """

        for rel in self.sfh[tbobj].relations:
            if self.sfh[rel].obj_type == Device:
                ppg = self.getdevice(rel)
                npt = self.sfh[tbobj].n_pre
                nsteps = self.sfh[tbobj].n_steps
                if not 'PRETRIG' in ppg.keys():
                    continue
                if npt > 0:
                    if ppg['PRETRIG'] > 0:
                        dt = ppg['RESOLUT'][15] * PPGCLOCK[ppg['RESFACT'][15]] + 1e-6
                    else:
                        dt = 0.
                    start_time = -dt*npt #ppg['PULSES'][0]
                else:
                    start_time = 0.
                dtyp = sfdics.fmt2np[self.sfh[tbobj].data_format]
                start_phase = start_time
                if npt > 0:
                    time_ppg = dt*np.arange(npt, dtype=dtyp) + start_phase
                    start_phase = time_ppg[-1] + dt
                else:
                    time_ppg = []
                for jphase in range(16):
                    if ppg['PULSES'][jphase] > 0:
                        dt = ppg['RESOLUT'][jphase]*PPGCLOCK[ppg['RESFACT'][jphase]]
                        tb_phase = dt*np.arange(ppg['PULSES'][jphase], dtype=dtyp) + start_phase
                        time_ppg = np.append(time_ppg, tb_phase)
                        start_phase = time_ppg[-1] + dt
                        logger.debug('Start time %d %d %d %d %.4f %.4f', jphase, ppg['PULSES'][jphase], ppg['RESOLUT'][jphase], ppg['RESFACT'][jphase], dt, start_phase)
                if len(time_ppg) == 0:
                    return None
                else:
                    return time_ppg[:nsteps]
        return None


    def raw2calib(self, data):
        """
        Calibrates an uncalibrated signal or SignalGroup
        """
# Calibrated signals and signal groups
        obj = str_byt.to_str(data.objnam)
        if data.obj_type not in (SignalGroup, Signal):
            logging.error('Calibration failed for %s: no Sig, no SGR', obj)
            return data

        pscal = self.lincalib(obj)
        if pscal is None:
            return data

        for j in range(10):
            mult = 'MULTIA0%d' %j
            shif = 'SHIFTB0%d' %j
            if mult in pscal.keys():
# we need to fix the content of pscal for signagroups
# assuming first entry wins
                if j == 0:
                    dout = data*1. # Creates a copy of a read-only array, only once
                    dout.calib = True
                multi = np.atleast_1d(pscal[mult])
                shift = np.atleast_1d(pscal[shif])
                if data.obj_type == Signal or len(multi) == 1:
                    dout *= multi[0] # MXR
                    dout += shift[0]
                else:
                    n_pars = dout.shape[1]
                    if n_pars != len(multi):
                        logger.warning('Inconsitent sizes in calibration PSet %s', obj)
                    if n_pars <= len(multi):
                        dout *= multi[: n_pars] # BLB
                        dout += shift[: n_pars]
                    else:
                        dout *= multi[0]
                        dout += shift[0]
            else:
                break
        if 'dout' in locals():
            return dout
        else:
            return data


    def lincalib(self, obj):
        """
        Returns coefficients for signal(group) calibration
        """
        obj = str_byt.to_str(obj)
        for rel in self.sfh[obj].relations:
            if self.sfh[rel].obj_type == ParamSet:
                caltyp = self.sfh[rel].cal_type
                if caltyp == LinCalib:
                    logger.info('PSet for calib: %s' %rel)
                    return self.getparset(rel)
                elif caltyp == extCalib:
                    diag_ext = self.getparset(rel)['DIAGNAME']
                    diag_ext = ''.join([str_byt.to_str(x) for x in diag_ext])
                    shot_ext = libddc.previousshot(diag_ext, shot=self.shot)
                    ext = read_other_sf(shot_ext, diag_ext)
                    return ext.getparset(rel) # same name in external shotfile
        return None


    def getparset(self, pset):
        """
        Returns data and metadata of a Parameter Set
        """

        pset = str_byt.to_str(pset)
        sfo = self.sfh[pset]
        otyp = sfo.obj_type
        if otyp not in (Device, ParamSet):
            return None

        buf = self.getchunk(sfo.address, sfo.length)

        j0 = 0
        par_d = {}
        logger.debug('Diag: %s, PS: %s, addr: %d, length: %d', self.diag, pset, sfo.items, sfo.length)
        for j in range(sfo.items):
            pname = str_byt.to_str(buf[j0: j0+8])
            unit, dfmt, n_items = unpack('>3h', buf[j0+8:  j0+14])
            meta = type('', (), {})()
            meta.physunit = unit
            if unit in sfdics.unit_d.keys():
                meta.phys_unit = sfdics.unit_d[unit]
            meta.n_items = n_items
            meta.data_format = dfmt
            meta.status = unpack('>h', buf[j0+14:  j0+16])[0]
            logger.debug('PN: %s, j0: %d, unit: %d dfmt: %d n_items: %d, status: %d', pname, j0, unit, dfmt, n_items, meta.status)
            j0 += 16

            if dfmt in sfdics.fmt2len.keys(): # char variable
                dlen = sfdics.fmt2len[dfmt]
                bytlen = n_items * dlen
                data = np.chararray((n_items,), itemsize=dlen, buffer=buf[j0+2: j0+2+bytlen])
                dj0 = 8 * ( (bytlen + 9)//8 )
                j0 += dj0
            elif dfmt in sfdics.fmt2typ.keys(): # number
                sfmt = sfdics.fmt2struc[dfmt]
                val_len = n_items + 2
                bytlen = val_len * np.dtype(sfmt).itemsize
                if dfmt == 7: # logical, bug if n_items > 1?
                    data = unpack(sfmt, buf[j0+5: j0+6])[0]
                else:
                    data = np.ndarray((val_len, ), '>%s' %sfmt, buf[j0: j0+bytlen], order='F').copy()
                    data = np.squeeze(data[2:])
                dj0 = 8 * ( (bytlen + 7)//8 )
                j0 += dj0
            else: # faulty dfmt
                break
            par_d[pname] = sfobj.SFOBJ(data, sfho=meta)

            if j0 >= sfo.length:
                break
        return par_d


    def getlist(self, obj=None):
        """
        Returns a list of data-objects of a shotfile
        """
        if obj is None:
            obj = 'SIGNALS'
        else:
            obj = str_byt.to_str(obj)
        sfo = self.sfh[obj]
        otyp = sfo.obj_type
        dfmt = sfo.data_format
        if otyp != List:
            return None
        buf = self.getchunk(sfo.address, sfo.length)
        sfmt = sfdics.fmt2struc[dfmt]
        list_ids = unpack('>%d%s' %(sfo.items, sfmt), buf)

        return [self.getobjname(jid) for jid in list_ids]


    def getlist_by_type(self, obj_type=Signal):
        """
        Returns a list of names of all SF-objects of a given type (Signal, TimeBase)
        """
        return [lbl for lbl, sfo in self.sfh.items() if sfo.obj_type == obj_type]


    def getobjname(self, jobj):
        """
        Returns the object name for an inpur object ID
        """

        for lbl, sfo in self.sfh.items():
            if sfo.objid == jobj:
                return lbl


    def getdevice(self, lbl):
        """
        Returns a DEVICE object
        """

        return self.getparset(lbl)


    def get_ts06(self):
# Look anywhere in the diagsnostic's Devices
        ts06 = None
        for obj in self.parsets:
            if self.sfh[obj].obj_type == Device:
                ps = self.getparset(obj)
                if 'TS06' in ps.keys():
                    ts6 = ps['TS06']
                    if ts6 > 1e15:
                        ts06 = ts6
                        break
        return ts06


    def getts06(self, obj):
        """
        Reads the diagnostic internal TS06 from parameter set
        """
        ts06 = None
        if self.sfh[obj].obj_type == TimeBase:
            tb = obj
        else:
            for rel_obj in self.sfh[obj].relations:
                if self.sfh[rel_obj].obj_type == TimeBase: # related TB
                    tb = rel_obj
                    break
        if 'tb' in locals(): # No TB related
            obj2 = tb
        else: # try a direct relation
            obj2 = obj

        for rel_obj in self.sfh[obj2].relations:
            if self.sfh[rel_obj].obj_type == Device: # related device
                ps = self.getparset(rel_obj)
                if 'TS06' in ps.keys():
                    ts6 = ps['TS06']
                    if ts6 > 1e15:
                        ts06 = ts6
                        break

        logger.debug('getts06 %s %d', rel_obj, ts06)
        if ts06 is None:
            ts06 = self.get_ts06()
        if ts06 is None:
            ts06 = getcti_ts06(self.shot)
        return ts06


    def time_dim(self, obj):
        """
        Tells which SigGroup dimension is a time dimension
        """

        obj = str_byt.to_str(obj)
        sfo = self.sfh[obj]
        otyp = sfo.obj_type
        if otyp != SignalGroup:
            return None # Objects other than sig, sgr, tbase

        for rel in sfo.relations:
            if self.sfh[rel].obj_type == TimeBase:
                shape_arr = sfo.index[::-1][:sfo.num_dims]
                nt = self.sfh[rel].n_steps
                if shape_arr.count(nt) == 1:
                    return shape_arr.index(nt)
                else:
                    return None
        return None # If there is no timebase among the relations


    def time_first(self, obj):
        """
        Tells whether a SigGroup has time as first coordinate
        by comparing with the size of the related TBase
        """

        return (self.time_dim(obj) == 0)


    def time_last(self, obj):
        """
        Tells whether a SigGroup has time as first coordinate
        by comparing with the size of the related TBase
        """

        obj = str_byt.to_str(obj)
        sfo = self.sfh[obj]
        
        return (self.time_dim(obj) == sfo.num_dims-1)
