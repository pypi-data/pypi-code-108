import logging
from struct import unpack, pack
import numpy as np
from aug_sfutils import sfdics, str_byt

n_rel = 8

logger = logging.getLogger('aug_sfutils.sfh_rw')
logger.setLevel(logging.INFO)

for key, val in sfdics.obj_name.items():
    exec('%s=%d' %(val, key))


def read_sfh(byt_str):
    """
    Reads a full shotfile header
    """

    sfhead = {}
    obj_names = []
    n_max = 1000
    n_obj = n_max
    for j in range(n_max):
        sfo = SFH_READ(byt_str[j*128: (j+1)*128])
        sfo.objid = j
        onam = str_byt.to_str(sfo.objnam.strip())
        if sfo.obj_type == Diagnostic:
            if n_obj == n_max: # There might be several diags objects in a SFH
                n_obj = sfo.num_objs
        sfhead[onam] = sfo
        obj_names.append(onam)
        if j == n_obj - 1:
            break

    for sfo in sfhead.values():
        sfo.relations = [obj_names[jid] for jid in sfo.rel if jid != 65535]

    return sfhead


def sfh2byt(sfo):

# SIGNALS list generated automatically, override input entry
    sigs = type('', (), {})()
    sigs.objnam = 'SIGNALS'
    sigs.objid = 1 # Always correct?
    sigs.data_format = 3
    sigs.obj_type = 2 # List
    sigs.level = 0
    sigs.status = 0
    sigs.errcode = 0
    sigs.rel = (65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535)
    sigs.ordering = 0
    sigs.list_type = 2
    sigs.descr = 'List of all SIGNAL, SIG_GROUP & TIME_BASE (built automatically)'.ljust(64)
    sigs.items = 0
    for key, val in sfo.sfh.items():
        if val.obj_type in (SignalGroup, Signal, TimeBase, AreaBase): # Include areabases too
            sigs.items += 1
    sigs.address = len(sfo.sfh)*128
    sigs.length = sigs.items*2

#    sfo.sfh['SIGNALS'] = sigs

    sfw_d = {}
    addr = sigs.address + sigs.length + 2

# ParSet first
    for sfobj in sfo.sfh.values():
        otyp = sfobj.obj_type
        if otyp in (Device, ParamSet): #Device, parSet
            sfobj.address = addr
            addr += sfobj.length # Todo: determine according to the parameters
            sfw_d[sfobj.objid] = SFH_WRITE(sfobj)

    for sfobj in sfo.sfh.values():
# order is consistently preserved, because of [sfobj.objid]
        otyp = sfobj.obj_type
        logger.debug('Obj: %s, type: %d, len: %d', sfobj.objnam, otyp, sfobj.length)
        logger.debug('Addr1: %d', sfobj.address)

        if otyp in (Device, ParamSet):
            continue

        if sfobj.objid < 2: # Diag, SIGNALS
            sfw_d[sfobj.objid] = SFH_WRITE(sfobj)
            if sfobj.objid == 1:
                logger.debug('Original len %d %d', sfobj.address, sfobj.length)
            continue

        if otyp in (SignalGroup, Signal, TimeBase, AreaBase):
            dfmt = sfobj.data_format
            if otyp in (Signal, SignalGroup):
                shape_arr = np.array(sfobj.index[::-1][:sfobj.num_dims])
            elif otyp == TimeBase:
                shape_arr = np.array([sfobj.n_steps])
            elif otyp == AreaBase:
                x = np.array([sfobj.size_x, sfobj.size_y, sfobj.size_z, sfobj.n_steps])
                shape_arr = x[x != 0]

            sfmt = sfdics.fmt2struc[dfmt]
            type_len = np.dtype(sfmt).itemsize
            bytlen = np.prod(shape_arr) * type_len
            logger.debug('Addr2: %d', addr)
            sfobj.length = bytlen

        sfobj.level = 0
        sfobj.status = 65535
        sfobj.address = addr

        sfw_d[sfobj.objid] = SFH_WRITE(sfobj)

        if otyp in (Signal, TimeBase):
            addr += 8*((bytlen + 7)//8)
        elif otyp in (AreaBase, ):
            addr += 8*((bytlen + 9)//8)
        elif otyp in (SignalGroup, ):
            n_block = 2*((bytlen + 7)//8)
            logger.debug('block %d type_len %d shape1 %d', n_block, type_len, shape_arr[-1])
#            addr += n_block*((bytlen + n_block+1)//n_block) # ok for TST0000.sfh
            addr += n_block*((bytlen + n_block-1)//n_block) + (shape_arr[1]-1)*2

    return sfw_d


def write_sfh(sfw_d, fout=None):

# Bytestring dividing header from data (PSet in case of a pure SFH)
    header_end = b'\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\t\x00\n\x00\x0b\x00\x0c\x00\r\x00\x0e\x00\x0f\x00\x10\x00\x11\x00\x12\x00\x13\x00\x14\x00\x15\x00\x16\x00\x17\x00\x18\x00\x19\x00\x1a\x00\x1b\x00\x1c\x00\x1d\x00\x1e\x00\x1f\x00 \x00!\x00"\x00#\x00$\x00%\x00&\x00\'\x00(  '

    f = open(fout, 'wb')
    for j in range(len(sfw_d)):
        f.write(sfw_d[j].bytstr[:128])
    f.write(header_end[:80])
    f.close()
    logger.info('Stored binary %s' %fout)


class SFH_READ:
    """
    Reads a generic object's metadata from the SFH's byte string
    """

    def __init__(self, byte_str):
        """
        Reads the SFH part of an object, common to all objects
        """
        self.objnam   = str_byt.to_str(byte_str[0:8].strip())
        self.obj_type, self.level, self.status = unpack('>3H', byte_str[ 8: 14])
        typ = self.obj_type
        if typ in sfdics.obj_name.keys():
            self.object_type = sfdics.obj_name[typ]
        else:
            self.object_type = 'Unknown'
        self.errcode  = unpack('>h', byte_str[14: 16])[0]
        fmt = '>%dH' %n_rel
        self.rel      = unpack(fmt,  byte_str[16        : 16+2*n_rel])
        self.address, self.length = unpack('>2I', byte_str[16+2*n_rel: 24+2*n_rel])
        self.val      = byte_str[40:  64]
        self.descr    = str_byt.to_str(byte_str[64: 128].strip())

        val_func = { \
            1 : self.diag, 2: self.list, 3: self.device, 4: self.parmset, \
            5 : self.mapping, 6: self.sig, 7: self.sig, 8: self.tbase, \
            9 : self.sf_list, 10: self.algorithm, 11: self.update_set, \
            12: self.loctimer, 13: self.abase, 14: self.qualifier, \
            15: self.modobj, 16: self.mapext, 17: self.resource, \
            18: self.addrlen }

        if typ in val_func.keys():
            val_func[typ]()
        else:
            logger.error('Object type %d not supported', sfo.obj_type)


    def diag(self):
        """
        Metadata of a DIAG object
        """
        self.diag_code = self.val[: 4]
        self.num_objs, self.diag_type  = unpack('>2H', self.val[4: 8])
        self.shot_nr , self.c_time     = unpack('>2I', self.val[8: 16])
        self.up_limit, self.exp, self.version, self.s_type = unpack('>4H', self.val[16: 24])


    def list(self):
        """
        Metadata of a LIST object
        """

        self.data_format, self.items, self.ordering, self.list_type = unpack('>4H', self.val[ : 8])


    def device(self):
        """
        Metadata of a DEVICE object
        """

        self.data_format, self.acquseq, self.items, self.dev_type = unpack('>4H', self.val[:8])
        self.dev_addr, self.n_chan  = unpack('>2I', self.val[ 8: 16])
        self.task    , self.dev_num = unpack('>2H', self.val[16: 20])
        self.n_steps                = unpack('>I' , self.val[20: 24])[0]  


    def parmset(self):
        """
        Metadata of a ParameterSet object
        """

        self.items, self.cal_type = unpack('>2H', self.val[4: 8])
        if self.cal_type in sfdics.cal_type.keys():
            self.calibration_type = sfdics.cal_type[self.cal_type]


    def mapping(self):
        """
        Metadata of a MAP object
        """

        self.items, self.map_type = unpack('>2H' , self.val[4: 8])
        self.task = unpack('>H' , self.val[16: 18])[0]


    def sig(self):
        """
        Metadata of a Signal or SignalGroup object
        """

        self.data_format, self.physunit, self.num_dims = unpack('>3H' , self.val[: 6])
        self.phys_unit = sfdics.unit_d[self.physunit]
        self.stat_ext = unpack('>h' , self.val[6: 8])[0]
        self.index    = unpack('>4I', self.val[8: 24])


    def tbase(self):
        """
        Metadata of a TIMEBASE object
        """

        self.data_format, self.burstcount, self.event, self.tbase_type = unpack('>4H', self.val[: 8])
        self.s_rate = unpack('>I', self.val[ 8: 12])[0] #Hz
        self.n_pre, self.n_steps = unpack('>2I', self.val[16: 24])
        if self.tbase_type in sfdics.tbtype_d.keys():
            self.timebase_type = sfdics.tbtype_d[self.tbase_type]


    def sf_list(self):
        """
        Metadata of a SF_LIST object
        """

        self.items = unpack('>H', self.val[2: 4])


    def algorithm(self):
        """
        Metadata of an ALGORITHM object
        """

        self.hostname = self.val[ 8: 16]
        self.date     = self.val[16: 24] 


    def update_set(self):
        """
        Metadata of an UPDATE_SET object
        """

        self.items =  unpack('>H' , self.val[ 2: 4])[0]
        self.input_vals = unpack('>i' , self.val[ 4: 8])[0]
        self.next_index, self.size = unpack('>I' , self.val[ 16: 24])


    def loctimer(self):
        """
        Metadata of an LOCTIMER object
        """

        self.data_format, self.resolution = unpack('>2H', self.val[: 4])
        self.size = unpack('>I', self.val[20: 24])[0]


    def abase(self):
        """
        Metadata of an AREABASE object
        """

        self.data_format = unpack('>H' , self.val[ : 2])[0]
        self.physunit    = unpack('>3H', self.val[2: 8])
        self.phys_unit = [sfdics.unit_d[x] for x in self.physunit]
        self.size_x, self.size_y, self.size_z, self.n_steps = unpack('>4I' , self.val[8: 24])


    def qualifier(self):
        """
        Metadata of an QUALIFIER object
        """

        self.data_format = unpack('>H' , self.val[ : 2])[0]
        self.num_dims, self.qsub_typ = unpack('>2H' , self.val[4: 8])
        self.index_4, self.index_3, self.index_2, self.max_sections = unpack('>4I' , self.val[8: 24])


    def modobj(self):
        """
        Metadata of a MODOBJ object
        """

        self.items = unpack('>H' , self.val[ : 2])[0]


    def mapext(self):
        """
        Metadata of a MAPEXT object
        """

        self.items, self.mapalg = unpack('>2H' , self.val[ : 4])
        self.tbeg , self.tend   = unpack('>2I', self.val[4: 12])
        self.val_0, self.val_1  = unpack('>2H', self.val[12: 16])
        self.val_2, self.val_3  = unpack('>2I', self.val[16: 24])


    def resource(self):
        """
        Metadata of a RESOURCE object
        """

        self.num_cpus, self.first_cpu = unpack('>2H' , self.val[ : 4])


    def addrlen(self):
        """
        Value of ADDRLEN object
        """

        self.addrlen = unpack('>H' , self.val[ : 2])[0]



class SFH_WRITE:
    """
    Writes a generic SFH object metadata to a byte string
    """

    def __init__(self, sfo):
        """
        Writes the SFH part of an object
        """
        self.sfo = sfo
        objnam   = str_byt.to_byt(sfo.objnam)
        obj_type = pack('>H', sfo.obj_type)
        level    = pack('>H', sfo.level)
        status   = pack('>H', sfo.status)
        errcode  = pack('>h', sfo.errcode)
        rel      = pack('>8H', *sfo.rel)
        address  = pack('>I', sfo.address)
        length   = pack('>I', sfo.length)
        self.val = bytearray(40)
        descr    = str_byt.to_byt(sfo.descr)

        val_func = { \
            1 : self.diag, 2: self.list, 3: self.device, 4: self.parmset, \
            5 : self.mapping, 6: self.sig, 7: self.sig, 8: self.tbase, \
            9 : self.sf_list, 10: self.algorithm, 11: self.update_set, \
            12: self.loctimer, 13: self.abase, 14: self.qualifier, \
            15: self.modobj, 16: self.mapext, 17: self.resource, \
            18: self.addrlen }

        if sfo.obj_type in val_func.keys():
#            logger.debug('%d %s %d', sfo.objid, sfo.objnam, sfo.obj_type)
            val_func[sfo.obj_type]()
        else:
            logger.warning('Object type %d not supported' %sfo.obj_type)

        self.bytstr = bytearray(128)
        self.bytstr[  :  8] = objnam.ljust(8)
        self.bytstr[ 8: 10] = obj_type
        self.bytstr[10: 12] = level
        self.bytstr[12: 14] = status
        self.bytstr[14: 16] = errcode
        self.bytstr[16: 32] = rel
        self.bytstr[32: 36] = address
        self.bytstr[36: 40] = length
        self.bytstr[40: 64] = self.val 
        self.bytstr[64:128] = descr.ljust(64)


    def diag(self):
        """
        Metadata of a DIAG object
        """
        self.val[  :  4] = self.sfo.diag_code
        self.val[ 4:  6] = pack('>H', self.sfo.num_objs)
        self.val[ 6:  8] = pack('>H', self.sfo.diag_type)
        self.val[ 8: 12] = pack('>I', self.sfo.shot_nr)
        self.val[12: 16] = pack('>I', self.sfo.c_time)
        self.val[16: 18] = pack('>H', self.sfo.up_limit)
        self.val[18: 20] = pack('>H', self.sfo.exp)
        self.val[20: 22] = pack('>H', self.sfo.version)
        self.val[22: 24] = pack('>H', self.sfo.s_type)


    def list(self):
        """
        Metadata of a LIST object
        """

        self.val[ : 2] = pack('>H', self.sfo.data_format)
        self.val[2: 4] = pack('>H', self.sfo.items)
        self.val[4: 6] = pack('>H', self.sfo.ordering)
        self.val[6: 8] = pack('>H', self.sfo.list_type)


    def device(self):
        """
        Metadata of a DEVICE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.acquseq)
        self.val[ 4:  6] = pack('>H', self.sfo.items)
        self.val[ 6:  8] = pack('>H', self.sfo.dev_type)
        self.val[ 8: 12] = pack('>I', self.sfo.dev_addr)
        self.val[12: 16] = pack('>I', self.sfo.n_chan)
        self.val[16: 18] = pack('>H', self.sfo.task)
        self.val[18: 20] = pack('>H', self.sfo.dev_num)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def parmset(self):
        """
        Metadata of a ParameterSet object
        """

        self.val[4: 6] = pack('>H', self.sfo.items)
        self.val[6: 8] = pack('>H', self.sfo.cal_type)


    def mapping(self):
        """
        Metadata of a MAP object
        """

        self.val[ 4:  6] = pack('>H', self.sfo.items)
        self.val[ 6:  8] = pack('>H', self.sfo.map_type)
        self.val[16: 18] = pack('>H', self.sfo.task)


    def sig(self):
        """
        Metadata of a Signal or SignalGroup object
        """

        self.val[  :  2] = pack('>H' , self.sfo.data_format)
        self.val[ 2:  4] = pack('>H' , self.sfo.physunit)
        self.val[ 4:  6] = pack('>H' , self.sfo.num_dims)
        self.val[ 6:  8] = pack('>h' , self.sfo.stat_ext)
        self.val[ 8: 24] = pack('>4I', *self.sfo.index)


    def tbase(self):
        """
        Metadata of a TIMEBASE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.burstcount)
        self.val[ 4:  6] = pack('>H', self.sfo.event)
        self.val[ 6:  8] = pack('>H', self.sfo.tbase_type)
        self.val[ 8: 12] = pack('>I', self.sfo.s_rate)
        self.val[16: 20] = pack('>I', self.sfo.n_pre)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def sf_list(self):
        """
        Metadata of a SF_LIST object
        """

        self.val[2: 4] = pack('>H', self.sfo.items)


    def algorithm(self):
        """
        Metadata of an ALGORITHM object
        """

        self.val[ 8: 16] = self.sfo.hostname
        self.val[16: 24] = self.sfo.date


    def update_set(self):
        """
        Metadata of an UPDATE_SET object
        """

        self.val[ 2:  4] = pack('>H', self.sfo.items) 
        self.val[ 4:  8] = pack('>i', self.sfo.input_vals) 
        self.val[16: 20] = pack('>I', self.sfo.next_index) 
        self.val[20: 24] = pack('>I', self.sfo.size) 


    def loctimer(self):
        """
        Metadata of an LOCTIMER object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.resolution)
        self.val[20: 24] = pack('>I', self.sfo.size)


    def abase(self):
        """
        Metadata of an AREABASE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  8] = pack('>3H', *self.sfo.physunit)
        self.val[ 8: 12] = pack('>I', self.sfo.size_x)
        self.val[12: 16] = pack('>I', self.sfo.size_y)
        self.val[16: 20] = pack('>I', self.sfo.size_z)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def qualifier(self):
        """
        Metadata of an QUALIFIER object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 4:  6] = pack('>H', self.sfo.num_dims)
        self.val[ 6:  8] = pack('>H', self.sfo.qsub_typ)
        self.val[ 8: 12] = pack('>I', self.sfo.index_4)
        self.val[12: 16] = pack('>I', self.sfo.index_3)
        self.val[16: 20] = pack('>I', self.sfo.index_2)
        self.val[20: 24] = pack('>I', self.sfo.max_sections)


    def modobj(self):
        """
        Metadata of a MODOBJ object
        """

        self.val[ : 2] = pack('>H', self.sfo.items)


    def mapext(self):
        """
        Metadata of a MAPEXT object
        """

        self.val[  :  2] = pack('>H', self.sfo.items)
        self.val[ 2:  4] = pack('>H', self.sfo.mapalg)
        self.val[ 4:  8] = pack('>I', self.sfo.tbeg)
        self.val[ 8: 12] = pack('>I', self.sfo.tend)
        self.val[12: 14] = pack('>H', self.sfo.val_0)
        self.val[14: 16] = pack('>H', self.sfo.val_1)
        self.val[16: 20] = pack('>I', self.sfo.val_2)
        self.val[20: 24] = pack('>I', self.sfo.val_3)


    def resource(self):
        """
        Metadata of a RESOURCE object
        """

        self.val[  :  2] = pack('>H', self.sfo.num_cpus)
        self.val[ 2:  4] = pack('>H', self.sfo.first_cpu)


    def addrlen(self):
        """
        Value of ADDRLEN object
        """

        self.val[ : 2] = pack('>H', self.sfo.addrlen)
