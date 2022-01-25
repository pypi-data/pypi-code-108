import numpy as np

class gencls:
    def __init__(self, node_number, gen_id, sbase=100, H=1, Xdp=0.1):
        self.node_number = node_number
        self.gen_id = gen_id
        self.sbase = sbase
        self.H = H
        self.Xdp = Xdp
        self.nx = 2
        self.ny = 11
    
    def make_indices(self, wb, ix, iy):
        self.ix = ix
        self.iy = iy
        self.gbusi = wb.gen(self.node_number, self.gen_id).node.dyn_index
        return self.nx, self.ny
    
    def steady_state(self, wb, x, colx, y, coly):

        # Find generator and get initial terminal voltage, power, current
        gen = wb.gen(self.node_number, self.gen_id)
        Vterm = gen.bus.vpu * np.exp(1j*(gen.bus.vang/180*np.pi))
        Sterm = (gen.p + 1j * gen.q) / self.sbase
        Iri = np.conj(Sterm/Vterm)

        # Impedance and admittance
        Z = 1j*self.Xdp
        Y = 1/Z

        # Find delta and Ep from internal voltage
        Vri = Vterm + Iri*Z
        delta = np.angle(Vri)
        Ep = np.abs(Vri)

        # Get voltage and current on machine reference frame
        Vdq = 1j * Ep
        Idq = Iri * (np.sin(delta) + 1j*np.cos(delta))

        # Torque values come from internal voltage and current
        Te = (Vdq * np.conj(Idq)).real
        Tm = Te

        # Norton values based on 
        Inort = (Iri + Vterm * Y) * self.sbase / 100.0
        gr = gi = Y.real * self.sbase / 100.0
        br = bi = Y.imag * self.sbase / 100.0

        # Omega initializes to zero
        omega = 0
        
        # Transfer variables to arrays
        x[self.ix, colx] = delta
        x[self.ix+1, colx] = omega
        y[self.iy, coly] = gr
        y[self.iy+1, coly] = gi
        y[self.iy+2, coly] = br
        y[self.iy+3, coly] = bi
        y[self.iy+4, coly] = Inort.real
        y[self.iy+5, coly] = Inort.imag
        y[self.iy+6, coly] = Ep
        y[self.iy+7, coly] = Idq.real
        y[self.iy+8, coly] = Idq.imag
        y[self.iy+9, coly] = Te
        y[self.iy+10, coly] = Tm
        