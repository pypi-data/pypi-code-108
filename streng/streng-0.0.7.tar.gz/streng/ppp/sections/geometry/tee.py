from streng.common.io.output import OutputTable
from streng.ppp.sections.geometry.rectangular import RectangularSectionGeometry as Rect
from cached_property import cached_property


class TeeSectionGeometry:

    __cached_props_list = ['area', 'moment_of_inertia_yy', 'moment_of_inertia_xx',
                           'torsional_constant',
                           'shear_area_2', 'shear_area_3',
                           'section_modulus_2', 'section_modulus_3',
                           'plastic_modulus_2', 'plastic_modulus_3',
                           'radius_of_gyration_2', 'radius_of_gyration_3',
                           'x_g', 'y_g']

    def __init__(self, bw, h, beff, hf):
        self.bw = bw
        self.h = h
        self.beff = beff
        self.hf = hf

    def invalidate_cache(self, keys_list):
        for key in keys_list:
            if key in self.__dict__.keys():
                del self.__dict__[key]

    @property
    def bw(self):
        return self._bw

    @bw.setter
    def bw(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._bw = value

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._h = value

    @property
    def hf(self):
        return self._hf

    @hf.setter
    def hf(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._hf = value

    @property
    def beff(self):
        return self._beff

    @beff.setter
    def beff(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._beff = value

    @cached_property
    def area(self) -> float:
        return self.bw * (self.h - self.hf) + self.beff * self.hf

    @cached_property
    def moment_of_inertia_yy(self) -> float:
        return (self.h - self.hf) * self.bw ** 3 / 12 + self.hf * self.beff ** 3 / 12

    @cached_property
    def moment_of_inertia_xx(self) -> float:
        Ix0 = self.bw * self.h ** 3 / 3.0 + \
            (self.beff - self.bw) * self.hf ** 3 / 3.0
        return Ix0 - self.area * self.y_g ** 2

    @cached_property
    def x_g(self) -> float:
        return self.beff / 2.0

    @cached_property
    def y_g(self) -> float:
        """Υπολογισμένο ξεκινώντας από την πλευρά της πλάκας.
        https://calcresource.com/cross-section-tee.html"""
        return (1.0 / self.area) * ((self.bw * self.h ** 2 / 2.0) + ((self.beff - self.bw) * self.hf ** 2 / 2.0))

    @cached_property
    def torsional_constant(self) -> float:
        """Δεν το έχω υπολογίσει ακόμα...κρατώ αποτέλεσμα ορθογωνικής δοκού"""
        r = Rect(self.bw, self.h)
        return r.torsional_constant
        # return self.bw ** 3 * self.h * (1 / 3 - 0.21 * self.bw / self.h * (1 - self.bw ** 4 / (12 * self.h ** 4)))

    @cached_property
    def shear_area_2(self) -> float:
        return self.bw * self.h

    @cached_property
    def shear_area_3(self) -> float:
        return 5. / 6. * self.beff * self.hf

    @cached_property
    def section_modulus_2(self) -> float:
        return self.moment_of_inertia_yy / self.x_g

    @cached_property
    def section_modulus_3(self) -> float:
        return self.moment_of_inertia_xx / (self.h - self.y_g)

    @cached_property
    def plastic_modulus_2(self) -> float:
        return (self.beff**2 * self.hf / 4.0) + ((self.h - self.hf)*self.bw**2)/4.0

    @cached_property
    def plastic_modulus_3(self) -> float:
        """Δεν το έχω υπολογίσει ακόμα...κρατώ αποτέλεσμα ορθογωνικής δοκού"""
        r = Rect(self.bw, self.h)
        return r.plastic_modulus_3
        # _pm3 = 0
        # if self.y_g()>self.hf:
        #     _pm3 = 0
        # else:
        #     _pm3 = 0
        #
        # return _pm3

    @cached_property
    def radius_of_gyration_2(self) -> float:
        return (self.moment_of_inertia_yy/self.area) ** 0.5

    @cached_property
    def radius_of_gyration_3(self) -> float:
        return (self.moment_of_inertia_xx/self.area) ** 0.5

    @property
    def all_quantities(self):
        out = OutputTable()
        out.data.append({'quantity': 'bw', 'value': self.bw})
        out.data.append({'quantity': 'h', 'value': self.h})
        out.data.append({'quantity': 'beff', 'value': self.beff})
        out.data.append({'quantity': 'hf', 'value': self.hf})
        out.data.append({'quantity': 'area', 'value': self.area})
        out.data.append(
            {'quantity': 'Iyy', 'value': self.moment_of_inertia_yy})
        out.data.append(
            {'quantity': 'Ixx', 'value': self.moment_of_inertia_xx})
        out.data.append({'quantity': 'J', 'value': self.torsional_constant})
        out.data.append({'quantity': 'ShearArea2', 'value': self.shear_area_2})
        out.data.append({'quantity': 'ShearArea3', 'value': self.shear_area_3})
        out.data.append({'quantity': 'SectionModulus2',
                         'value': self.section_modulus_2})
        out.data.append({'quantity': 'SectionModulus3',
                         'value': self.section_modulus_3})
        out.data.append({'quantity': 'PlasticModulus2',
                         'value': self.plastic_modulus_2})
        out.data.append({'quantity': 'PlasticModulus3',
                         'value': self.plastic_modulus_3})
        out.data.append({'quantity': 'RadiusOfGyration2',
                         'value': self.radius_of_gyration_2})
        out.data.append({'quantity': 'RadiusOfGyration3',
                         'value': self.radius_of_gyration_3})
        out.data.append({'quantity': 'xG', 'value': self.x_g})
        out.data.append({'quantity': 'yG', 'value': self.y_g})
        return out

    def __str__(self):
        return self.all_quantities.to_markdown

