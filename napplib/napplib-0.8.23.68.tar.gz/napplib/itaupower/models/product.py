from typing import List


class CustomAttribute:
	attribute_code: str
	value: str

	def __init__(self, attribute_code: str, value: str) -> None:
		self.attribute_code = attribute_code
		self.value = value


class CategoryLink:
	position: int
	category_id: str

	def __init__(self, position: int, category_id: str) -> None:
		self.position = position
		self.category_id = category_id


class ExtensionAttributes:
	website_ids: List[int]
	category_links: List[CategoryLink]

	def __init__(self, website_ids: List[int] = None, category_links: List[CategoryLink] = None) -> None:
		if website_ids:
			self.website_ids = website_ids
		if category_links:
			self.category_links = category_links


class Content:
	base64_encoded_data: str
	type: str
	name: str

	def __init__(self, base64_encoded_data: str, type: str, name: str) -> None:
		self.base64_encoded_data = base64_encoded_data
		self.type = type
		self.name = name


class VideoContent:
	media_type: str
	video_provider: str
	video_url: str
	video_title: str
	video_description: str
	video_metadata: str

	def __init__(self, media_type: str, video_provider: str, video_url: str, video_title: str, video_description: str, video_metadata: str) -> None:
		self.media_type = media_type
		self.video_provider = video_provider
		self.video_url = video_url
		self.video_title = video_title
		self.video_description = video_description
		self.video_metadata = video_metadata


class MediaGalleryEntryExtensionAttributes:
	video_content: VideoContent

	def __init__(self, video_content: VideoContent) -> None:
		self.video_content = video_content


class MediaGalleryEntry:
	id: int
	media_type: str
	label: str
	position: int
	disabled: bool
	types: List[str]
	file: str
	content: Content
	extension_attributes: MediaGalleryEntryExtensionAttributes

	def __init__(self, media_type: str,
						label: str,
						position: int,
						disabled: bool,
						types: List[str],
						id: int = None,
						file: str = None,
						content: Content = None,
						extension_attributes: MediaGalleryEntryExtensionAttributes = None) -> None:
		self.media_type = media_type
		self.label = label
		self.position = position
		self.disabled = disabled
		self.types = types

		if id:
			self.id = id
		if file:
			self.file = file
		if content:
			self.content = content
		if extension_attributes:
			self.extension_attributes = extension_attributes


class Product:
	id: int
	sku: str
	name: str
	attribute_set_id: int
	price: int
	status: int
	visibility: int
	type_id: str
	created_at: str
	updated_at: str
	weight: int
	extension_attributes: ExtensionAttributes
	media_gallery_entries: List[MediaGalleryEntry]
	custom_attributes: List[CustomAttribute]

	def __init__(self, sku: str,
						id: int = None,
						name: str = None,
						attribute_set_id: int = None,
						price: int = None,
						status: int = None,
						visibility: int = None,
						type_id: str = None,
						weight: int = None,
						extension_attributes: ExtensionAttributes = None,
						media_gallery_entries: List[MediaGalleryEntry] = None,
						custom_attributes: List[CustomAttribute] = None) -> None:
		self.sku = sku
		if id:
			self.id = id
		if name:
			self.name = name
		if attribute_set_id:
			self.attribute_set_id = attribute_set_id
		if price:
			self.price = price
		if status:
			self.status = status
		if visibility:
			self.visibility = visibility
		if type_id:
			self.type_id = type_id
		if weight:
			self.weight = weight
		if extension_attributes:
			self.extension_attributes = extension_attributes
		if media_gallery_entries:
			self.media_gallery_entries = media_gallery_entries
		if custom_attributes:
			self.custom_attributes = custom_attributes


class ItauPowerProduct:
	product: Product
	save_options: bool

	def __init__(self, product: Product, save_options: bool = None) -> None:
		self.product = product
		if save_options:
			self.save_options = save_options
