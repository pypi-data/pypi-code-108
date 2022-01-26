# build-in imports
from enum import Enum


class Environment(Enum):
	STAGING		= 'http://mule-mmchub-app.ir-e1.cloudhub.io/retailer'
	PRODUCTION 	= 'http://prod-mmchub-v1.ir-e1.cloudhub.io/retailer'
