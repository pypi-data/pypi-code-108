
""" FOD core motifs """

class CoreMotifs:
    """
        CoreMotifs class 
        ----------------
    """
    def __init__(self,C,atom,symbols,positions,elec_symbols=['X','He']):
        """
            __init__
            ---------
            Initialize an instance of this class. 
        """
        self.C = C
        self.symbol = atom.symbol
        self.position = atom.position
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = 0.002
        self.symbols = symbols
        self.positions = positions
        self._Na = 0
        self._Nb = 0

    def _count_e(self,symbol):
        """
            _count_e
            --------
            Count electrons (e). 
        """
        if symbol == self.sym_fod1:
            self._Na += 1
        if symbol == self.sym_fod2:
            self._Nb += 1

    def _set_e(self,symbol,offset=0):
        """
            _set_e
            ------
            Set a electron (e) position.
        """
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.append(self.position+offset)

    def kernel(self):
        """
            kernel 
            ------
            Main function for this class. 
        """
        if self.C == 1:
            # 1s 
            self._set_e(self.sym_fod1)
        if self.C == 2:
            # two 1s 
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
        if self.C == 3:
            # triangle
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*4])
        if self.C == 4:
            # tetrahedron 
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*(+40)])
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*(-40)])
