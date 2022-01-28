"""Editing shotfile headers"""

import shutil, os, logging
import ctypes as ct
import numpy as np
from aug_sfutils import sfdics, str_byt, sfread

sfhlib = '/afs/ipp/aug/ads/lib64/@sys/libsfh8.so.20201118'
if not os.path.isfile(sfhlib):
    sfhlib = '/afs/ipp/aug/ads/lib64/amd64_sles11/libsfh8.so.20201118'

libsfh = ct.cdll.LoadLibrary(sfhlib)

logger = logging.getLogger('aug_sfutils.sfh')

for key, val in sfdics.typ2descr.items():
    if key is not None:
        exec('%s=%d' %(val, key))


class SFH:

    def Open(self, fname):
        """Opens the shot file header name, reads it in a temporary memory buffer and records the last modification date."""

        fname = str_byt.to_byt(fname)
        c_name = ct.c_char_p(fname)
        self.c_sfid = ct.c_int32(0)
        _sfid = ct.byref(self.c_sfid)

        self.sfhead = sfread.SFREAD(sfh=fname)
        err = libsfh.sfhopen(c_name, _sfid, len(fname))
        libsfh.sfherror(err, 'Open')

        return err

    def Close(self):
        """This routine does the following things:
- checks if sfid is still valid
- checks if the original shot file header is unchanged, otherwise there will be an error
- copies the original shot file header to name.BAK
- writes the new shot file header."""

        err = libsfh.sfhclose(self.c_sfid)
        libsfh.sfherror(err, 'Close')

        return err

    def Mdarea(self, obj, nsteps, nx, ny, nz):
        """Modifes the size of an AreaBase object
        """

        bobj  = str_byt.to_byt(obj)
        c_obj = ct.c_char_p(bobj)
        c_nsteps = ct.c_uint32(nsteps)
        c_nx = ct.c_uint32(nx)
        c_ny = ct.c_uint32(ny)
        c_nz = ct.c_uint32(nz)

        err = libsfh.sfhmdarea(self.c_sfid, c_obj, c_nsteps, c_nx, c_ny, c_nz)
        libsfh.sfherror(err, 'mdarea')

    def Mdindex(self, obj, nx, ny, nz, qual=False):
        """Modifes the spatial index of an object
        """

        bobj  = str_byt.to_byt(obj)
        c_obj = ct.c_char_p(bobj)
        c_nx  = ct.c_uint32(nx)
        c_ny  = ct.c_uint32(ny)
        c_nz  = ct.c_uint32(nz)

        if qual:
            err = libsfh.sfhmdqualindex(self.c_sfid, c_obj, c_nx, c_ny, c_nz)
        else:
            err = libsfh.sfhmdindex24(self.c_sfid, c_obj, c_nx, c_ny, c_nz)
        libsfh.sfherror(err, 'mdindex24')

    def Modtim(self, obj, nt):
        """Modifes the size of the time dimension of an object
        """

        bobj  = str_byt.to_byt(obj)
        c_obj = ct.c_char_p(bobj)
        c_nt  = ct.c_uint32(nt)

        err = libsfh.sfhmodtim(self.c_sfid, c_obj, c_nt)
        libsfh.sfherror(err, 'modtim')

    def Modindex1(self, obj, nt):

        bobj  = str_byt.to_byt(obj)
        c_obj = ct.c_char_p(bobj)
        c_nt  = ct.c_uint32(nt)

        err = libsfh.sfhmdindex1(self.c_sfid, c_obj, c_nt)
        libsfh.sfherror(err, 'modindex1')

    def Modsgr(self, obj, dims, qual=False):
        """Modifes the dimenskions of a SigGroup
        """

        nx = 1 + np.zeros(4, dtype=int)
        for jdim in range(len(dims)):
            nx[jdim] = dims[jdim]
        self.Modtim(obj, nx[0])
        self.Mdindex(obj, nx[1], nx[2], nx[3], qual=qual)

    def Modpar(self, ps, pn, dat):
        """Modifies a parameter's size in ParSet
        """

        pss = str_byt.to_str(ps)
        pns = str_byt.to_str(pn)
        if pss not in self.sfhead.parsets:
            logger.debug('%s it not a parameter set', pss)
            return

        dfmt = self.sfhead(pss)[pn].data_format
        if dfmt in sfdics.fmt2len.keys():
            sf_dtype = CHAR
        else:
            sf_dtype = sfdics.fmt2typ[dfmt]
        pnlen = len(dat)
# Input
        bps   = str_byt.to_byt(ps)
        bpn   = str_byt.to_byt(pn)
        bdat  = str_byt.to_byt(dat)
        c_ps  = ct.c_char_p(bps)
        c_pn  = ct.c_char_p(bpn)
        c_typ = ct.c_uint32(sf_dtype)
        c_len = ct.c_uint32(pnlen)
        _typ  = ct.byref(c_typ)
        _len  = ct.byref(c_len)
# Output

        logger.debug('Modpar test: %s %d %d %d', pns, sf_dtype, pnlen, len(dat))
        if dfmt in sfdics.fmt2len.keys():
            name_len = sfdics.fmt2len[dfmt]
            c_len  = ct.c_uint32(pnlen)
            c_data = ct.c_char_p(bdat)
            err = libsfh.sfhmodpar(self.c_sfid, c_ps, c_pn, c_typ, c_len, c_data)
        else:
            err = libsfh.sfhmodpar(self.c_sfid, c_ps, c_pn, c_typ, c_len, dat.ctypes.data_as(ct.POINTER(ct.c_long)))
        libsfh.sfherror(err, 'Modpar')


    def newobj(self, objname, objtyp, subtyp):
        """Creates a new SFH object
        """

# objtyp: 6 SGR, 7 Signal, 8 Timebase, 13 Areabase
        objname = str_byt.to_byt(objname)
        c_obj = ct.c_char_p(objname)
        c_otyp = ct.c_uint16(objtyp)
        c_styp = ct.c_uint16(subtyp)
        err = libsfh.sfhnewobj(self.c_sfid, c_obj, c_otyp, c_styp)
        libsfh.sfherror(err, 'newobj')


    def newrel(self, objname, newrelname):
        """Adds a new relation to a given object
        """

        objname    = str_byt.to_byt(objname)
        newrelname = str_byt.to_byt(newrelname)
        c_obj = ct.c_char_p(objname)
        c_rel = ct.c_char_p(newrelname)
        err = libsfh.sfhstrel(self.c_sfid, c_obj, c_rel)
        libsfh.sfherror(err, 'newrel')


    def newrelt(self, objname, newreltb):
        """Adds a new TimeBase relation to a given object
        """

        objname  = str_byt.to_byt(objname)
        newreltb = str_byt.to_byt(newreltb)
        c_obj   = ct.c_char_p(objname)
        c_reltb = ct.c_char_p(newreltb)
        err = libsfh.sfhstreltb(self.c_sfid, c_obj, c_reltb)
        libsfh.sfherror(err, 'newrelt')


    def set_text(self, objname, newtext):
        """Replaces the description string of a given object
        """

        objname = str_byt.to_byt(objname)
        newtext = str_byt.to_byt(newtext)
        c_obj  = ct.c_char_p(objname)
        c_text = ct.c_char_p(newtext)
        err = libsfh.sfhmtext(self.c_sfid, c_obj, c_text)
        libsfh.sfherror(err, 'set_text')

#===============
#    New Methods
#===============

    def Mapping(self):
# Bug: use sfhread!
        objects = self.Lonam()
        if objects is None:
            return
        mapping = []

        for i in objects:
            if objects[i] == 6:
                indices = self.Rdindex24(i)
                for i2 in range(indices[2]):
                    for i3 in range(indices[3]):
                        for i4 in range(indices[4]):
                            mapping.append([i, [i2, i3, i4], \
                                self.Rdmap(i, i2 + 1 ,i3 + 1, i4 + 1)['chan']])

        return mapping

    def Channelmapping(self):
    
        raw_mapping = self.Mapping()
        mapping_array = np.array(len(raw_mapping), dtype=np.str)
        for raw_map in raw_mapping:
            mapping_array[raw_map[2]] = raw_map[0] + '_' + str(raw_map[1][0]) + '-' + str(raw_map[1][1]) + '-' + str(raw_map[1][2])

        return mapping_array

    def Signalmapping(self):
    
        raw_mapping = self.Mapping()
        mapping_table = {}
        for raw_map in raw_mapping:
            mapping_table[raw_map[0] + '_' + str(raw_map[1][0]) + '-' + str(raw_map[1][1]) + '-' + str(raw_map[1][2])] = raw_map[2]

        return mapping_table
