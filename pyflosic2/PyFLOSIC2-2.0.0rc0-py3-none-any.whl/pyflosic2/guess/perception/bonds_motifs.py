import numpy 
from pyflosic2.guess.perception.utils import check_spin 
from pyflosic2.guess.perception.utils import rotation_matrix, perpendicular_vector

""" FOD bonding motifs """

class BondMotifs:
    """
        BondMotifs class 
        ----------------
        Determines bonding motifs using bonding order (bo) information. 
    """
    def __init__(self,bo,bo_ref,sp,nn,i,j,atoms,symbols,positions,elec_symbols=['X','He']):
        self.bo = bo
        self.bo_ref = bo_ref
        self.sp = sp
        self.nn = nn
        self.i = i
        self.j = j
        self.posA = atoms[i].position
        self.posB = atoms[j].position
        self.atoms = atoms
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = numpy.array([0.0,0.0,0.0])
        self.symbols = symbols
        self.positions = positions
        self._Na = 0
        self._Nb = 0

    def _count_e(self,symbol):
        if symbol == self.sym_fod1:
            self._Na += 1/2.
        if symbol == self.sym_fod2:
            self._Nb += 1/2.


    def _set_e(self,symbol,position,offset=numpy.array([0,0,0])):
        """
            Set e
            -----
            "Set the electron" means 
            update symbols and positions. 
        """
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.extend([position+offset])

    def _get_bond_center(self):
        """
            Get bond center 
            ---------------
        """
        return (self.posA+self.posB)/2.

    def _get_posAB(self):
        """
            Get posAB
            ---------
            Get vector between points A and B. 
        """
        return self.posB - self.posA

    def kernel(self):
        """
            Kernel function 
            ---------------

            Rules
            -----
            bo = 1 and 1.41 is mapped to single bond 
            bo = 1.5 is mapped to LDQ (1,2) or (2,1) bond 
            bo = 2 is mapped to double bond 
            bo = 3 is mapped to triple bond 
        """
        bc = self._get_bond_center()
        posAB = self._get_posAB()
        n = numpy.linalg.norm(posAB)
        posAB /= n
        # Single bond 
        if self.bo == 1 or self.bo == 1.41:
            # Special rule for X-H, H-X bonds. 
            # The bonding electrons are placed closer to the H atom. 
            if self.atoms[self.i].symbol == 'H' or self.atoms[self.j].symbol == 'H':
                bc += posAB*0.3
            # Point motif: motif_1 
            self._set_e(self.sym_fod1,bc)
            self._set_e(self.sym_fod2,bc,offset=self.offset)

        # Double bond or 1.5 bond  
        if self.bo == 2 or self.bo == 1.5:
            # Line motif: motif_2 
            motif_2 = numpy.array([[0,0,+1.0],
                                   [0,0,-1.0]])*0.75
            # if z-component of posAB is close to zero -> 
            # no need to rotate (posAB automatically 
            # aligned with perpendicular direction of motif_2)
            if numpy.isclose(posAB[2],0,0,1e-3):
                v1 = motif_2[0,:]
                v2 = motif_2[1,:]
            else:
                # Rotate the motif such that its perpendicular direction 
                # aligns with the bond axis (posAB)
                axis = [0,1,0] # perpendicular axis for the motif
                n_axis = numpy.linalg.norm(axis)
                angle = numpy.arccos(numpy.dot(posAB,numpy.array(axis))/(n*n_axis))
                rot_axis = numpy.cross(numpy.array(axis),posAB)
                self.rot_mat = rotation_matrix(rot_axis,angle)
                v1 = numpy.dot(self.rot_mat,motif_2[0,:])
                v2 = numpy.dot(self.rot_mat,motif_2[1,:])

            # If the A and/or B are sp2 hybridized 
            # the bonding electrons have a rotational 
            # degree of freedom. 
            # We check for the hybridization of A/B 
            # and if one of them is sp2, 
            # we calculate the molecular plane 
            # and the bonding electrons are placed 
            # perpendicular to this plane
            check1_sp = self.sp[self.i] == 2 # posA 
            check2_sp = self.sp[self.j] == 2 # posB 
            if check1_sp:
                ref_idx = self.i
                idx_j = self.nn[ref_idx].nonzero()[0].tolist()
                if len(idx_j) < 2:
                    ref_idx = self.j
                    idx_j = self.nn[ref_idx].nonzero()[0].tolist()
            if check2_sp:
                ref_idx = self.j
                idx_j = self.nn[ref_idx].nonzero()[0].tolist()
                if len(idx_j) < 2:
                    ref_idx = self.i
                    idx_j = self.nn[ref_idx].nonzero()[0].tolist()
            if check1_sp or check2_sp:
                ## ref_idx 
                #rot_axis = numpy.cross(self.atoms[idx_j[0]].position-self.atoms[ref_idx].position,self.atoms[idx_j[1]].position-self.atoms[ref_idx].position)
                #v1v2 = v2 - v1
                #n1 = numpy.linalg.norm(rot_axis) 
                #n2 = numpy.linalg.norm(v1v2)
                #angle = numpy.arccos(numpy.dot(v1v2,rot_axis)/(n1*n2)) 
                ## rotate around posAB
                #self.rot_mat = rotation_matrix(posAB,angle) 
                #v1 = numpy.dot(self.rot_mat,v1) 
                #v2 = numpy.dot(self.rot_mat,v2)
                # Determine perpendicular vector to molecular plane
                # Place bond FODs at bond center using this vector
                #
                app = numpy.cross(self.atoms[idx_j[0]].position-self.atoms[ref_idx].position,self.atoms[idx_j[1]].position-self.atoms[ref_idx].position)
                n1 = numpy.linalg.norm(app)
                app /= n1 # normalize
                app *= 0.75 # scale down; shorten the lengths 
                v1 = app
                v2 = -1.0*app

        # Double bound 
        if self.bo == 2:
            self._set_e(self.sym_fod1,bc,offset=v1)
            self._set_e(self.sym_fod1,bc,offset=v2)
            self._set_e(self.sym_fod2,bc,offset=v1)
            self._set_e(self.sym_fod2,bc,offset=v2)

        # Trible bond 
        if self.bo == 3:
            # Triangle motif: motif_3 
            # motif_3: app =[0,1,0]
            motif_3 = numpy.array([[0,0,1.0],
                                   [numpy.sqrt(0.75),0,-0.5],
                                   [-1*numpy.sqrt(0.75),0,-0.5]])

            # if posAB is equal to the y-axis: No need to rotate
            axis = [0,1,0]
            if numpy.allclose(posAB,axis,0,1e-3):
                v1 = motif_2[0,:]
                v2 = motif_2[1,:]
                v2 = motif_3[2,:]
            else:
                angle = numpy.arccos(numpy.dot(posAB,numpy.array(axis))/n)
                rot_axis = numpy.cross(numpy.array(axis),posAB)
                self.rot_mat = rotation_matrix(rot_axis,angle)
                v1 = numpy.dot(self.rot_mat,motif_3[0,:])
                v2 = numpy.dot(self.rot_mat,motif_3[1,:])
                v3 = numpy.dot(self.rot_mat,motif_3[2,:])
            self._set_e(self.sym_fod1,bc,offset=v1)
            self._set_e(self.sym_fod1,bc,offset=v2)
            self._set_e(self.sym_fod1,bc,offset=v3)
            self._set_e(self.sym_fod2,bc,offset=v1)
            self._set_e(self.sym_fod2,bc,offset=v2)
            self._set_e(self.sym_fod2,bc,offset=v3)

        # For bo = 1.5 we use a Lewis reference bo 
        # to easy separate between (1,2) and (2,1) 
        # bonds. 

        print('>>>>>>>>>>>>>>>>>>> HANS PETER <<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(self.symbols,check_spin(self.symbols),self._Na, self._Nb)
        print(f'{self.i} {self.j} bo bonds: {self.bo} {self.bo_ref}')
        # Lewis aromatic single bond
        local_spin = check_spin(self.symbols)
        local_Na = self._Na #local_spin[0][0]
        local_Nb = self._Nb #local_spin[1][0]
        if local_Na >= local_Nb:
            sym_majority = self.sym_fod2
            sym_minority = self.sym_fod1
        if local_Nb > local_Na:
            sym_majority = self.sym_fod1
            sym_minority = self.sym_fod2
        if self.bo == 1.5:
            self._set_e(sym_majority,bc,offset=v1)
            self._set_e(sym_minority,bc)
            self._set_e(sym_majority,bc,offset=v2)
        #if self.bo == 1.5 and self.bo_ref == 1.0:
        #    #self._set_e(self.sym_fod1,bc,offset=[0,0,0.5])
        #    self._set_e(self.sym_fod1,bc,offset=v1)
        #    self._set_e(self.sym_fod2,bc)
        #    #self._set_e(self.sym_fod1,bc,offset=[0,0,-0.5])
        #    self._set_e(self.sym_fod1,bc,offset=v2)
        ## Lewis aromatic double bound 
        #if self.bo == 1.5 and self.bo_ref == 2.0:
        #    #self._set_e(self.sym_fod2,bc,offset=[0,0,0.5])
        #    self._set_e(self.sym_fod2,bc,offset=v1)
        #    self._set_e(self.sym_fod1,bc)
        #    #self._set_e(self.sym_fod2,bc,offset=[0,0,-0.5])
        #    self._set_e(self.sym_fod2,bc,offset=v2)


