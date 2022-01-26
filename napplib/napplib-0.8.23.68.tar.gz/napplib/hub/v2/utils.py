from dataclasses 	import dataclass

# build-in imports
from enum import Enum


class Environment(Enum):
	STAGING		= 'http://backend-napphubv2-int.napphubv2-staging.svc.cluster.local:9090/v2'
	PRODUCTION 	= 'http://backend-napphubv2-int.napphubv2-production.svc.cluster.local:9090/v2'
	DEVELOPMENT	= 'http://localhost:9091/v2'
