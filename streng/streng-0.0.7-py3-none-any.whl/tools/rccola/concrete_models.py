from dataclasses import dataclass


@dataclass
class Kappos91:
    fc: float
    fy: float
    bc: float
    s: float
    ρw: float
    α: float = 1.0
    β: float = 1.0
    εc0: float = 0.002
    ρsx: float = 0.003334

    def __post_init__(self):
        self.ωw = self.ρw * self.fy / self.fc
        self.k = 1 + self.α * self.ωw ** self.β
        self.fcc = self.k * self.fc
        self.εcc0 = self.εc0 * self.k * self.k
        self.ε50c = 0.75 * self.ρw * (self.bc / self.s) ** 0.5 + (3. + 0.29 * self.fc / self.k) / (
                    145 * self.fc / self.k - 1000.)
        self.u = 0.5 / (self.ε50c - self.εc0)
        self.εcult = self.εcc0 + (self.k - 0.85) / (self.k * self.u)

        self.ε25c = (0.75 + self.u * self.εcc0) / self.u

        self.fcc_ec8 = self.fc * (1 + 3.7 * (self.α * self.ρsx * self.fy / self.fc)**0.86)

    def σc(self, εc):
        if εc <= self.εcc0:
            _σc = self.fcc * (2 * (εc / self.εcc0) - (εc / self.εcc0) ** 2)
        else:
            _σc = max(self.fcc * (1 - self.u * (εc - self.εcc0)), 0.25 * self.fcc)
        return _σc


@dataclass
class KentPark71:
    fc: float
    bc: float
    s: float
    ρw: float
    nsp: int = 0
    εc0: float = 0.002

    def __post_init__(self):
        self.ε50u = (3. + 0.29 * self.fc) / (145. * self.fc - 1000.)
        self.ε50h = 0.75 * self.ρw * (self.bc / self.s)**0.5
        self.ε50c = self.ε50u + self.ε50h
        self.z = 0.5 / (self.ε50c - self.εc0)
        self.ε20c = self.εc0 + 1.6 * (self.ε50c - self.εc0)

    def σc(self, εc):
        if εc <= self.εc0:
            _σc = self.fc * (2 * (εc / self.εc0) - (εc / self.εc0) ** 2)
        else:
            _σc = max(self.fc * (1 - self.z * (εc - self.εc0)), 0.2 * self.fc)
            if self.nsp > 0 and εc > self.ε50u:
                _σc = 0.
        return _σc
