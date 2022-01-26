from edc_randomization.randomizer import Randomizer as Base
from edc_randomization.site_randomizers import site_randomizers


class Randomizer(Base):
    assignment_map = {"integration": 1}
    is_blinded_trial = False


site_randomizers.register(Randomizer)
