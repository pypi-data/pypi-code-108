from __future__ import annotations
from marshmallow import Schema, fields


##########
### Schema
##########
class ImageSchema(Schema):
    id = fields.Int(required=True)
    file_name = fields.Str(required=True)
    width = fields.Int(required=True)
    height = fields.Int(required=True)
    license = fields.Str()
    flickr_url = fields.Str()
    coco_url = fields.Str()


class CategorySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)


class InfoSchema(Schema):
    year = fields.Int()
    version = fields.Str()
    contributor = fields.Str()
    description = fields.Str()
    url = fields.Str()


class AnnotationSchema(Schema):
    id = fields.Int(required=True)
    image_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    bbox = fields.List(fields.Int)
    segmentation = fields.List(fields.List(fields.Int))
    iscrowd = fields.Int()
    area = fields.Float()


class CocoBuilderSchema(Schema):
    info = fields.Nested(InfoSchema)
    images = fields.List(fields.Nested(ImageSchema))
    annotations = fields.List(fields.Nested(AnnotationSchema))
    categories = fields.List(fields.Nested(CategorySchema))


################
### Coco Classes
################
class CocoImage:
    def __init__(self, id, file_name, width, height, license, flickr_url, coco_url):
        self.width = width
        self.height = height
        self.id = id
        self.file_name = file_name
        self.license = license
        self.flickr_url = flickr_url
        self.coco_url = coco_url


class CocoCategory:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class CocoInfo:
    def __init__(self, year, version, contributor, description, url):
        self.year = year
        self.version = version
        self.contributor = contributor
        self.description = description
        self.url = url


class CocoAnnotation:
    def __init__(self, id, image_id, category_id, bbox, segmentation, iscrowd, area):
        self.id = id
        self.image_id = image_id
        self.category_id = category_id
        self.bbox = bbox
        self.segmentation = segmentation
        self.iscrowd = iscrowd
        self.area = area


class CocoBuilder:
    def __init__(self):
        self.images = []
        self.categories = []
        self.info = {}
        self.annotations = []

    def add_annotation(
        self, id, image_id, category_id, bbox, segmentation, iscrowd, area
    ):
        annotation = CocoAnnotation(
            id, image_id, category_id, bbox, segmentation, iscrowd, area
        )
        schema = AnnotationSchema()
        result = schema.dump(annotation)
        self.annotations.append(result)

    def add_image(
        self, id, file_name, width, height, license="", flickr_url="", coco_url=""
    ):

        # Validate the image schema
        image = CocoImage(id, file_name, width, height, license, flickr_url, coco_url)
        schema = ImageSchema()
        result = schema.dump(image)

        # Skip if the image has been added already
        for added_image in self.images:
            if added_image["id"] == image.id:
                return

        # Add to the images list if it does not exist
        self.images.append(result)

    def add_category(self, id, name):
        category = CocoCategory(id, name)
        schema = CategorySchema()
        result = schema.dump(category)

        # Skip if the category has been added already
        for added_category in self.categories:
            if added_category["id"] == category.id:
                return

        # Add to the categories list if it does not exist
        self.categories.append(result)

    def add_info(self, year, version, contributor, description, url):
        info = CocoInfo(year, version, contributor, description, url)
        schema = InfoSchema()
        result = schema.dump(info)
        self.info = result

    def get(self):
        schema = CocoBuilderSchema()
        return schema.dumps(self)

    def __str__(self):
        return self.get()
