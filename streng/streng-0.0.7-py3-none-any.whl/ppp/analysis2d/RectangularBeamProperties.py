class RectangularBeamProperties:
    def __init__(self, b, h):
        self.b = b
        self.h = h

    def area(self):
        return self.b * self.h

    def moment_of_inertia_yy(self):
        return self.b ** 3 * self.h / 12

    def moment_of_inertia_xx(self):
        return self.h ** 3 * self.b / 12

    def torsional_constant(self):
        return self.b ** 3 * self.h * (1 / 3 - 0.21 * self.b / self.h * (1 - self.b ** 4 / (12 * self.h ** 4)))

    def shear_area_2(self):
        return 5 / 6 * self.area()

    def shear_area_3(self):
        return 5 / 6 * self.area()

    def section_modulus_2(self):
        return self.b ** 2 * self.h / 6

    def section_modulus_3(self):
        return self.h ** 2 * self.b / 6

    def plastic_modulus_2(self):
        return self.b ** 2 * self.h / 4

    def plastic_modulus_3(self):
        return self.h ** 2 * self.b / 4

    def radius_of_gyration_2(self):
        return self.b / 12 ** 0.5

    def radius_of_gyration_3(self):
        return self.h / 12 ** 0.5

    def x_g(self):
        return self.b / 2

    def y_g(self):
        return self.h / 2

    def __str__(self):
        _str = 'Rectangular beam geometric properties\n'
        _str += f'b={self.b:.3f} [m]\n'
        _str += f'h={self.h:.3f} [m]\n'
        _str += f'A={self.area():.3f} [m2]\n'
        _str += f'Iyy={self.moment_of_inertia_yy():.3E} [m4]\n'
        _str += f'Ixx={self.moment_of_inertia_xx():.3E} [m4]\n'
        _str += f'J={self.torsional_constant():.3E} [m4]\n'
        _str += f'ShearArea2={self.shear_area_2():.4f} [m2]\n'
        _str += f'ShearArea3={self.shear_area_3():.4f} [m2]\n'
        _str += f'SectionModulus2={self.section_modulus_2():.4f} [m3]\n'
        _str += f'SectionModulus3={self.section_modulus_3():.4f} [m3]\n'
        _str += f'PlasticModulus2={self.plastic_modulus_2():.4f} [m3]\n'
        _str += f'PlasticModulus3={self.plastic_modulus_3():.4f} [m3]\n'
        _str += f'RadiusOfGyration2={self.radius_of_gyration_2():.4f} [m]\n'
        _str += f'RadiusOfGyration3={self.radius_of_gyration_3():.4f} [m]\n'
        _str += f'xG={self.x_g():.3f} [m]\n'
        _str += f'yG={self.y_g():.3f} [m]\n'
        return _str
