from dataclasses import dataclass, field
from typing import Dict
import math

from streng.ppp.sections.concrete.typical_sections.slabs import Slab


@dataclass
class SlabLoadsToBeams(Slab):
    """

    .. code-block:: python
       :linenos:

       sl = SlabLoadsToBeams(l_max = 6.0,
                             l_min = 4.0,
                             slab_type = '4',
                             slab_load = 6.3)

       print(sl.beams_loads)

    """
    slab_load: float
    slab_areas: Dict = field(default_factory=dict)
    beams_loads: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.calc()

    def calc(self):
        if self.slab_type == '1' or self.slab_type == '6' or self.slab_type == 1 or self.slab_type == 6:
            areas = self.get_areas_1(self.l_max, self.l_min)
        elif self.slab_type == '2a':
            areas = self.get_areas_2a(self.l_max, self.l_min)
        elif self.slab_type == '2b':
            areas = self.get_areas_2b(self.l_max, self.l_min)
        elif self.slab_type == '3a':
            areas = self.get_areas_3a(self.l_max, self.l_min)
        elif self.slab_type == '3b':
            areas = self.get_areas_3b(self.l_max, self.l_min)
        elif self.slab_type == '4' or self.slab_type == 4:
            areas = self.get_areas_4(self.l_max, self.l_min)
        elif self.slab_type == '5a':
            areas = self.get_areas_5a(self.l_max, self.l_min)
        elif self.slab_type == '5b':
            areas = self.get_areas_5b(self.l_max, self.l_min)
        else:
            areas = 0., 0., 0., 0.

        for i in range(0, 4):
            self.slab_areas[i + 1] = areas[i]
            self.beams_loads[i + 1] = areas[i] * self.slab_load

        self.beams_loads[1] /= self.l_max
        self.beams_loads[2] /= self.l_max
        self.beams_loads[3] /= self.l_min
        self.beams_loads[4] /= self.l_min

    @staticmethod
    def get_areas_1(l1, l2):
        """
        .. image paths are relative to the shpinx source folder that calls this automodule/autoclass

        Υπολογισμός εμβαδών για πλάκες τύπου 1

        .. image:: ../img/slab_loads_to_beams/01.png
            :width: 45 %
        """
        e1 = 0.5 * (l1 + (l1 - l2)) * l2 / 2
        e2 = e1
        e3 = 0.25 * l2 * l2
        e4 = e3
        return e1, e2, e3, e4

    @staticmethod
    def get_areas_2a(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 2a

        .. image:: ../img/slab_loads_to_beams/02a.png
            :width: 45 %
        """
        l2b = l2 / (1 + math.tan(math.pi / 6) / math.tan(math.pi / 4))
        l2a = l2 - l2b
        l1a = l2a
        # l1c = l2a
        l1b = l1 - 2 * l2a

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = e3
        return e1, e2, e3, e4

    @staticmethod
    def get_areas_2b(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 2b

        .. image:: ../img/slab_loads_to_beams/02b1.png
            :width: 45 %

        .. image:: ../img/slab_loads_to_beams/02b2.png
            :width: 40 %
        """
        l1a = (l2 / 2) / math.tan(math.pi / 6)
        l1c = l2 / 2
        l2a = l1c
        l2b = l1c
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        if l1b < 0:
            l1a = l1 / (1 + math.tan(math.pi / 6))
            l1b = l1 - l1a
            l2a = l1b
            l2c = l1b
            l2b = l2 - l2a - l2c

            e1 = 0.5 * l1 * l2c
            e2 = 0.5 * l1 * l2a
            e3 = 0.5 * (l2 + l2b) * l1a
            e4 = 0.5 * (l2 + l2b) * l1b

        return e1, e2, e3, e4

    @staticmethod
    def get_areas_3a(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 3a

        .. image:: ../img/slab_loads_to_beams/03a.png
            :width: 45 %
        """
        l2a = l2 / 2
        l2b = l2a
        l1a = l2a / math.tan(math.pi / 3)
        l1c = l1a
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        return e1, e2, e3, e4

    @staticmethod
    def get_areas_3b(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 3b

        .. image:: ../img/slab_loads_to_beams/03b1.png
            :width: 45 %

        .. image:: ../img/slab_loads_to_beams/03b2.png
            :width: 40 %
        """
        l2a = l2 / 2
        l2b = l2a
        l1a = l2a / math.tan(math.pi / 6)
        l1c = l1a
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        if l1b < 0:
            l1a = l1 / 2
            l1b = l1a
            l2a = l1a * math.tan(math.pi / 6)
            l2c = l2a
            l2b = l2 - l2a - l2c

            e1 = 0.5 * l1 * l2c
            e2 = 0.5 * l1 * l2a
            e3 = 0.5 * (l2 + l2b) * l1a
            e4 = 0.5 * (l2 + l2b) * l1b

        return e1, e2, e3, e4

    @staticmethod
    def get_areas_4(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 4

        .. image:: ../img/slab_loads_to_beams/04.png
            :width: 45 %
        """
        l2a = l2 / (1 + math.tan(math.pi / 3) / math.tan(math.pi / 4))
        l2b = l2 - l2a
        l1a = l2b
        l1c = l2a
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        return e1, e2, e3, e4

    @staticmethod
    def get_areas_5a(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 5a

        .. image:: ../img/slab_loads_to_beams/05a.png
            :width: 45 %
        """
        l2a = l2 / 2
        l2b = l2 - l2a
        l1a = l2b
        l1c = l2a / math.tan(math.pi / 3)
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        return e1, e2, e3, e4

    @staticmethod
    def get_areas_5b(l1, l2):
        """
        Υπολογισμός εμβαδών για πλάκες τύπου 5b

        .. image:: ../img/slab_loads_to_beams/05b1.png
            :width: 45 %

        .. image:: ../img/slab_loads_to_beams/05b2.png
            :width: 40 %
        """
        l2b = l2 / (1 + math.tan(math.pi / 3) / math.tan(math.pi / 4))
        l2a = l2 - l2b
        l1a = l2a
        l1c = l2a
        l1b = l1 - l1a - l1c

        e1 = 0.5 * (l1 + l1b) * l2b
        e2 = 0.5 * (l1 + l1b) * l2a
        e3 = 0.5 * l2 * l1a
        e4 = 0.5 * l2 * l1c

        if l1b < 0:
            l1a = l1 / 2
            l1b = l1a
            l2a = l1a
            l2c = l2a * math.tan(math.pi / 6)
            l2b = l2 - l2a - l2c

            e1 = 0.5 * l1 * l2c
            e2 = 0.5 * l1 * l2a
            e3 = 0.5 * (l2 + l2b) * l1a
            e4 = 0.5 * (l2 + l2b) * l1b

        return e1, e2, e3, e4



