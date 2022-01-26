from enum import Enum

class ShopifyProductStatus(Enum):
	ACTIVE = 'active'
	ARCHIVED = 'archived'
	DRAFT = 'draft'

class ShopifyProductPublishedStatus(Enum):
	ANY = 'any'
	PUBLISHED = 'published'
	UNPLISHED = 'unpublished'