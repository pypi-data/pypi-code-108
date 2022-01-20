'''Main module of etherbase-predeployed

Classes:
  - EtherbaseGenerator

Values:
  - ETHERBASE_ADDRESS
'''

from .address import ETHERBASE_ADDRESS, ETHERBASE_IMPLEMENTATION_ADDRESS
from .etherbase_generator import EtherbaseGenerator
from .etherbase_upgradeable_generator import UpgradeableEtherbaseUpgradeableGenerator
