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

from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITtsc']


class OMFITtsc(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with TSC input files

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    naming = r'''
 00 &  Control &  IRST1 & IRST2 & IPEST & NCYCLE &  NSKIPR & NSKIPL &  IMOVIE
 01 &  Dimensions &  NX & NZ & ALX & ALZ & ISYM & CCON & IDATA
 02 &  Time step &  DTMINS & DTMAXS & DTFAC & LRSWTCH & IDENS & IPRES & IFUNC
 03 &  Numerical &  XLIM & ZLIM & XLIM2 & FFAC & NDIV & ICIRC & ISVD
 04 &  Surf. Ave. &  ISURF & NPSI & NSKIPSF & TFMULT &  ALPHAR & BETAR & ITRMOD
 05 &  Limiter &  I & XLIMA(I) & ZLIMA(I) & XLIMA(I+1) & ZLIMA(I+1) & XLIMA(I+2) & ZLIM(I+2)
 06 &  Divertor &  IDIV & PSIRAT & X1SEP & X2SEP & Z1SEP & Z2SEP & NSEPMAX
 07 &  Impurities &  IIMP & ILTE & IMPBND & IMPPEL & AMGAS & ZGAS & NTHE
 08 &  Obs. pairs &  J & XOBS(2J-1) & ZOBS(2J-1) & XOBS(2J) & ZOBS(2J) &  NPLOTOBS
 09 &  Ext. coils &  N & XCOIL(N) & ZCOIL(N) & IGROUPC(N) & ATURNSC(N) & RSCOILS(N) & AINDC(N)
 10 &  Int. coils &  M & XWIRE(M) & ZWIRE(M) & IGROUPW(M) & ATURNSW(M) & RSWIRES(M) & CWICS(M)
 11 &  ACOEF  &  ICO & NCO & ACOEF(ICO) & $\ldots$(ICO+1) & $\ldots$ & $\ldots$ &  $\ldots$(ICO+4)
 12 &  Tranport &  TEVV & DCGS & QSAW & ZEFF & IALPHA & IBALSW & ISAW
 13 &  Init. cond-1 &  ALPHAG & ALPHAP & NEQMAX & XPLAS & ZPLAS & GZERO & QZERO
 14 &  Init. cond-2 &  ISTART & XZERIC & AXIC & ZZERIC & BZIC
 15 &  Coil groups &  IGROUP & GCUR(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & GCUR(6)
 16 &  Plasma curr. &   -  & PCUR(1)  & $\ldots$ & $\ldots$ & $\ldots$  & $\ldots$ & PCUR(6)
 17 &  Plasma press. &   -  & PPRES(1)  & $\ldots$ & $\ldots$ & $\ldots$  & $\ldots$ & PPRES(6)
 18 &  Timing &   -  & TPRO(1)  & $\ldots$ & $\ldots$ & $\ldots$  & $\ldots$ &  TPRO(6)
 19 &  Feedback-1 &   L  & NRFB(L)  & NFEEDO(L) & FBFAC(L) & FBCON(L)  & IDELAY(L) & FBFACI(L)
 20 &  Feedback-2 &   L  & TFBONS(L)  & TFBOFS(L) & FBFAC1(L) & FBFACD(L) & IPEXT(L)
 21 &  Contour plot &   ICPLET  & ICPLGF & ICPLWF & ICPLPR & ICPLBV & ICPLUV & ICPLXP
 22 &  Vector plot &   IVPLBP  & IVPLVI  & IVPLFR & IVPLJP & IVPLVC & IVPLVT & -
 23 &  Aux. heat &   -  & BEAMP(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & BEAMP(6)
 24 &  Density &   -  & RNORM(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  RNORM(6)
 25 &  Dep. prof. &   ABEAM  & DBEAM  & NEBEAM & EBEAMKEV & AMBEAM  & FRACPAR & IBOOTST
 26 &  Anom. trans. &   - & FBCHIA(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  FBCHIA(6)
 27 &  Tor. field &   - & GZEROV(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & GZEROV(6)
 28 &  Loop volt. &   - & VLOOPV(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & VLOOPV(6)
 29 &  PEST output&   - & TPEST(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & TPEST(6)
 30 &  Mag. Axis(x) &   - & XMAGO(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & XMAGO(6)
 31 &  Mag. Axis(z) &   - & ZMAGO(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & ZMAGO(6)
 32 &  Divertor &  N & XLPLATE(N) & ZLPLATE(N) & XRPLATE(N) & ZRPLATE(N) & FPLATE(N,1) & FPLATE(N,2)
 33 &  Coil grp-2 & IGROUP & RESGS( )
 34 &  TEVV(t) &   -  & TEVVO(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & TEVVO(6)
 35 &  FFAC(t) &   -  & FFACO(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & FFACO(6)
 36 &  ZEFF(t) &   -  & ZEFFV(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & ZEFFV(6)
 37 &  Volt group &   IGROUP & GVOLT(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & GVOLT(6)
 38 &  LHDEP &   ILHCD & VILIM  & FREQLH & AION & ZION & CPROF & IFK
 39 &  Ext. coil-2 &   N & DXCOIL(N)  & DZCOIL(N) & FCU(N) & FSS(N) & TEMPC(N) & CCICS(N)
 40 &  Noplot &  NOPLOT(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & NOPLOT(7)
 41 &  Ripple &   IRIPPL & NTFCOIL & RIPMAX & RTFCOIL & NPITCH & RIPMULT & IRIPMOD
 42 &  Major rad. &  - &  RZERV(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & RZERV(6)
 43 &  Minor rad. &  - &  AZERV(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & AZERV(6)
 44 &  Ellipticity &  - & EZERV(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & EZERV(6)
 45 &  Triangularity &  - & DZERV(1)& $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & DZERV(6)
 46 &  LH heating &  - &  PLHAMP(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & PLHAMP(6)
 47 &  Dens. exp-1 &  - &  ALPHARV(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & ALPHARV(6)
 48 &  Dens. exp-2 & - &  BETARV(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & BETARV(6)
 49 &  Multipole &  N & MULTN(N) & ROMULT(N) & IGROUPM(N) &  ATURNSM(N)
 50 &  CD &  - &  FRACPAR(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & FRACPAR(6)
 51 &  alh & -& A(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A(6)
 52 &  dlh & -& D(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & D(6)
 53 &  a1lh & -& A1(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & A1(6)
 54 &  a2lh & -& A2(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & A2(6)
 55 &  ac & -& AC(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & AC(6)
 56 &  dc & -& DC(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & DC(6)
 57 &  ac1 & -& AC1(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & AC1(6)
 58 &  ac2 & -& AC2(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & AC2(6)
 59 &  ICRH & -& PICRH(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  PICRH(6)
 60 &  Halo Temp & - &  TH(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ & TH(6)
 61 &  Halo Width & - &  AH(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  AH(6)
 62 &  X-Shape point & - &  XCON0(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  XCON0(6)
 63 &  Z-Shape point & - &  ZCON0(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  ZCON0(6)
 64 &  Fast Wave J & - &  FWCD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  FWCD(6)
 65 &  ICRH power profile &   &  A(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A(6)
 66 &  ICRH power profile &   &  D(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  D(6)
 67 &  ICRH power profile &   &  A1(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A1(6)
 68 &  ICRH power profile &   &  A2(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A2(6)
 69 &  ICRH current profile &   &  A(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A(6)
 70 &  ICRH current profile &   &  D(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  D(6)
 71 &  ICRH current profile &   &  A1(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A1(6)
 72 &  ICRH current profile &   &  A2(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A2(6)
 73 &  He conf. time & - &  HEACT(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  HEACT(6)
 74 &  UFILE output & - &  TUFILE(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  TUFILE(6)
 75 &  Sawtooth time & - &  SAWTIME(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  SAWTIME(6)
 76 &  Anom. ion trans. &   - & FBCHIIA(1)  & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  FBCHIIA(6)
 77 &  acoef(123) & - &  qadd(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  qadd(6)
 78 &  acoef(3003) & - &  fhmodei(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  fhmodei(6)
 79 &  acoef(3011) & - &  pwidthc(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  pwidthc(6)
 80 &  acoef(3006) & - &  chiped(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  chiped(6)
 81 &  acoef(3102) & - &  tped(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  tped(6)
 82 &  impurity fraction &  imptype &  frac(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  frac(6)
 83 &  acoef(3012) & - &  nflag(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  nflag(6)
 84 &  acoef(3013) & - &  expn1(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  expn1(6)
 85 &  acoef(3014) & - &  expn2(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  expn2(6)
 86 &  acoef(3004) & - &  firitb(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  firitb(6)
 87 &  acoef(3005) & - &  secitb(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  secitb(6)
 88 &  acoef(881) & - &  fracno(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  fracno(6)
 89 &  acoef(889) & - &  newden(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  newden(6)
 90 &  ECRH Power (MW) &  & PECRH(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  PECRH(6)
 91 &  ECCD Toroidal Current (MA) &  & ECCD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  ECCD(6)
 92 &  Sh. Par. "a" (ECCD H CD) &  & AECD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  AECD(6)
 93 &  Sh. Par. "d" (ECCD H CD) &  & DECD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  DECD(6)
 94 &  Sh. Par. "a1" (ECCD H CD) &  & A1ECD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A1ECD(6)
 95 &  Sh. Par. "a2" (ECCD H CD) &  & A2ECD(1) & $\ldots$ & $\ldots$ & $\ldots$ & $\ldots$ &  A2ECD(6)
 99 &
'''

    def __init__(self, filename, **kw):
        SortedDict.__init__(self, sorted=True)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        self.naming = [[x.strip().strip('$\\') for x in x.split('&')] for x in [_f for _f in self.naming.split('\n') if _f]]
        self.naming = dict(list(zip([int(x[0]) for x in self.naming], [x[1:] for x in self.naming])))

    @dynaLoad
    def load(self):
        lines = list(map(lambda x: str(x).strip(), open(self.filename, 'r').readlines()))

        fmt = 'i2,a8,a10,a10,a10,a10,a10,a10,a10'

        for k, line in list(enumerate(lines))[1:]:
            if line.startswith('c'):
                pass
            else:
                id = int(line[:2])
                if id not in self:
                    self[id] = []
                self[id].append(fortranformat.FortranRecordReader(fmt).read(line))

        for item in list(self.keys()):
            if not is_int(item):
                continue
            tmp = np.atleast_2d(self[item])
            for k, name in list(enumerate(['card'] + self.naming[item])):
                try:
                    if k == 1:
                        card = '%02d' % item + '-' + re.sub(r'[\."]', '', re.sub(' ', '_', name))
                        self.setdefault(card, {})
                        continue
                    if name.strip() in ['-', '', 'ldots', 'card']:
                        continue
                    if item == 11:
                        if not name.startswith('ACOEF'):
                            continue
                        for row in self[item]:
                            name = name.split('(')[0] + '(%d)' % int(eval(row[2]))
                            self[card][name] = np.array(list(map(float, [_f for _f in [x.strip() for x in row[4:]] if _f])))
                            if len(self[card][name]) == 1:
                                self[card][name] = self[card][name][0]
                    else:
                        tmp0 = np.array([_f for _f in [x.strip() for x in tmp[:, k:].flatten().tolist()] if _f])
                        if '(' in name:
                            self[card][name.split('(')[0]] = tmp0.astype(float)
                            break
                        else:
                            try:
                                self[card][name] = tmp0[:1].astype(float)
                            except Exception as _excp:
                                self[card][name] = tmp0[:1]
                            if len(self[card][name]) == 1:
                                self[card][name] = self[card][name][0]
                            elif not len(self[card][name]):
                                self[card][name] = None
                except Exception:
                    printe('Error at punchcard %s with name %s\n' % (item, name))
                    raise
            del self[item]

    @dynaSave
    def save(self):
        text = []
        for item in self:
            card = int(item[:2])
            n = np.sum([np.atleast_1d(self[item][key]).size for key in self[item]])
            if n == 0:
                continue
            if card == 11:
                for line in sorted(list(self[item].keys()), key=lambda line: int(line.split('(')[1][:-1])):
                    data = np.atleast_1d(self[item][line])
                    ltxt = (
                        ['%10d' % int(line.split('(')[1][:-1]), '%10d' % len(data)]
                        + ['%10g' % x for x in data.tolist()]
                        + [' ' * 10] * (5 - len(data))
                    )
                    text.append(''.join([str(card).ljust(10)] + ltxt))
                continue
            for line in range(int(n // 7)):
                ltxt = []
                for key in self.naming[card][1:]:
                    if key in ['-', '']:
                        txt = ' ' * 10
                        ltxt.append(txt)
                    elif '(' in key:
                        data = ['%10g' % x for x in self[item][key.split('(')[0]]]
                        txt = data[line * 7 : (line + 1) * 7 + 1]
                        ltxt.extend(txt)
                        break
                    else:
                        data = self[item][key]
                        if data is not None:
                            txt = '%10g' % data
                        else:
                            txt = ' ' * 10
                        ltxt.append(txt)
                text.append(''.join([str(card).ljust(10)] + ltxt))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(text))
