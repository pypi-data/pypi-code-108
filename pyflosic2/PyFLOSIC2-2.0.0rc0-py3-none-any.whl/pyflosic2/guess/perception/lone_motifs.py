import numpy 
from pyflosic2.guess.perception.utils import check_spin
from pyflosic2.guess.perception.utils import rotation_matrix, perpendicular_vector

""" FOD lone motifs """

class LoneMotifs:
    """
        LoneMotifs class 
        ----------------
        Determines lone motifs, e.g., FODs which 
        neither are bonded nor they are in the core of a atom.
    """
    def __init__(self,R,idx,atoms,nn,sp,symbols,positions,elec_symbols=['X','He']):
        """
             __init__
             ---------
             Initialize an instance of the class. 
        """
        self.R = R
        self.i = idx
        self.pos = atoms[idx].position
        self.atoms = atoms
        self.nn = nn
        self.sp = sp
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = 0 #0.002
        self.symbols = symbols
        self.positions = positions
        self._Na = 0
        self._Nb = 0

    def _count_e(self,symbol):
        if symbol == self.sym_fod1:
            self._Na += 1
        if symbol == self.sym_fod2:
            self._Nb += 1

    def _set_e(self,symbol,position,offset=0):
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.append(position+offset)

    def _get_ba(self):
        """
            Get ba
            ------
            Get direction/orientation 
            for lone electrons. 
        """
        idx_j = self.nn[self.i].nonzero()[0].tolist()
        ba = numpy.zeros_like(self.pos)
        BA = []
        for j in idx_j:
            tmp_ba = self.atoms[j].position - self.pos
            BA.append(tmp_ba)
            ba += tmp_ba
        print(f'lonemotif: pos: {self.pos} ba: {ba} sp {self.sp[j]} {self.sp[self.i]}')
        n = numpy.linalg.norm(ba)
        # Workaround for ZeroDevision 
        if n > 0:
            # sign choice depends on the defintion of ba (or ab) 
            ba = -1*ba/n
        ba /=2
        ba += self.pos
        return ba, BA
    
    def kernel(self):
        """
            kernel 
            ------
            Main function for this class.
        """
        ba, BA = self._get_ba()

        if self.R == 1 or self.R == 2:
            check1_sp = self.sp[self.i] == 3
            idx_j = self.nn[self.i].nonzero()[0].tolist()
            sp_j = self.sp[idx_j]
            print(f'check1_sp: {check1_sp} {sp_j}')
            if check1_sp:
                print('Lone: special case N sp3')
                # e.g., Conformer3D_CID_142199 
                # see https://stackoverflow.com/questions/4372556/given-three-points-on-a-tetrahedron-find-the-4th
                # Find a position for the lone electron on a tetrahedra.
                # Or in other words find the 4th point on a tetrahedra 
                # spanned by the nuclei around the current one. 
                idx_j = self.nn[self.i].nonzero()[0].tolist()
                pos_j = self.atoms[idx_j].positions
                sym_j = self.atoms[idx_j].symbols
                com = pos_j.mean(axis=0)
                axis = numpy.cross(pos_j[2] - pos_j[0],pos_j[1] - pos_j[0])
                n = numpy.linalg.norm(axis)
                axis /= n
                axis *= numpy.sqrt(2/3)
                # SS: [Question] : How to determine if top of bottom? 
                # top 
                # ba2 = com + axis 
                # botton 
                ba2 = com - axis
                # If ba2 is parallel to ba (and with the atom) 
                # the the original ba has the correct sign (top vs. bottom). 
                # If this case is fullfilled we stay with the original ba 
                # otherwise we take the new ba. 
                n = numpy.linalg.norm(numpy.cross(ba-self.pos,ba2-self.pos))
                check =  numpy.isclose(n,0,0,1e-3)
                if not check:
                    ba = ba2

        if self.R == 1:
            # We have one lone electron
            # We need to deside which spin channel the lone electrons belongs to.
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb:
                sym_X = self.sym_fod2
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,ba)

        if self.R == 2:
            # We have two lone electrons 
            self._set_e(self.sym_fod1,ba)
            self._set_e(self.sym_fod2,ba,offset=self.offset)

        if self.R == 3:
            # We have three lone electrons 
            if len(BA) == 2 or len(BA) == 3: # SS: 3? 
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            # We have two unpaired electron pairs and one lone electron. 
            # We need to deside which spin channel the lone electrons belongs to. 
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb:
                sym_X = self.sym_fod2
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,ba-app+[20*self.offset,0,0])

        if self.R == 4:
            # We have 4 lone electrons 
            print(f'len(BA): {BA}')
            if len(BA) == 2 or len(BA) == 3: # SS: 3 ? 
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)

        if self.R == 5:
            # We have 5 lone electrons 
            # Idea is the case as R == 6 - 1 
            if len(BA) == 2:
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
                app2 = perpendicular_vector(app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)
            # We have two unpaired electron pairs and one lone electron. 
            # We need to deside which spin channel the lone electrons belongs to. 
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb:
                sym_X = self.sym_fod2
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,self.pos+app2+[20*self.offset,0,20*self.offset])

        if self.R == 6:
            # We have 6 lone electrons 
            if len(BA) == 2:
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
                app2 = perpendicular_vector(app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,self.pos+app2+[20*self.offset,0,20*self.offset])
            self._set_e(self.sym_fod2,self.pos+app2+[20*self.offset,0,20*self.offset],offset=self.offset)

