from streng.common.io.output import OutputTable
from cached_property import cached_property


class RectangularSectionGeometry:

    __cached_props_list = ['area', 'moment_of_inertia_yy', 'moment_of_inertia_xx',
                           'torsional_constant',
                           'shear_area_2', 'shear_area_3',
                           'section_modulus_2', 'section_modulus_3',
                           'plastic_modulus_2', 'plastic_modulus_3',
                           'radius_of_gyration_2', 'radius_of_gyration_3',
                           'x_g', 'y_g']

    def __init__(self, b, h):
        self.b = b
        self.h = h

    def invalidate_cache(self, keys_list):
        for key in keys_list:
            if key in self.__dict__.keys():
                del self.__dict__[key]

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._b = value

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value):
        self.invalidate_cache(self.__cached_props_list)
        self._h = value

    @cached_property
    def area(self):
        return self.b * self.h

    @cached_property
    def moment_of_inertia_yy(self) -> float:
        return self.b ** 3 * self.h / 12

    @cached_property
    def moment_of_inertia_xx(self) -> float:
        return self.h ** 3 * self.b / 12

    @cached_property
    def torsional_constant(self) -> float:
        return self.b ** 3 * self.h * (1 / 3 - 0.21 * self.b / self.h * (1 - self.b ** 4 / (12 * self.h ** 4)))

    @cached_property
    def shear_area_2(self) -> float:
        return 5 / 6 * self.area

    @cached_property
    def shear_area_3(self) -> float:
        return 5 / 6 * self.area

    @cached_property
    def section_modulus_2(self) -> float:
        return self.b ** 2 * self.h / 6

    @cached_property
    def section_modulus_3(self) -> float:
        return self.h ** 2 * self.b / 6

    @cached_property
    def plastic_modulus_2(self) -> float:
        return self.b ** 2 * self.h / 4

    @cached_property
    def plastic_modulus_3(self) -> float:
        return self.h ** 2 * self.b / 4

    @cached_property
    def radius_of_gyration_2(self) -> float:
        return self.b / 12 ** 0.5

    @cached_property
    def radius_of_gyration_3(self) -> float:
        return self.h / 12 ** 0.5

    @cached_property
    def x_g(self) -> float:
        return self.b / 2

    @cached_property
    def y_g(self) -> float:
        return self.h / 2

    @property
    def all_quantities(self):
        out = OutputTable()
        out.data.append({'quantity': 'b', 'value': self.b})
        out.data.append({'quantity': 'h', 'value': self.h})
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
