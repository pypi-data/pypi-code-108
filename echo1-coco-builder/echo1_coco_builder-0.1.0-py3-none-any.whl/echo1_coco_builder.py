import json, re
from marshmallow import Schema, fields


def obj_dict(obj):
    return obj.__dict__


##########
### Schema
##########
class ImageSchema(Schema):
    id = fields.Int()
    image_name = fields.Str()
    width = fields.Int()
    height = fields.Int()


class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()


class InfoSchema(Schema):
    year = fields.Int()
    version = fields.Str()
    contributor = fields.Str()


class AnnotationSchema(Schema):
    id = fields.Int()
    image_id = fields.Int()
    category_id = fields.Int()
    bbox = fields.List(fields.Int)
    segmentation = fields.List(fields.String)


class CocoSchema(Schema):
    images = fields.Nested(ImageSchema())


################
### Coco Classes
################
class CocoImage:
    def __init__(self, id, image_name, width, height):
        self.width = width
        self.height = height
        self.id = id
        self.image_name = image_name


class CocoCategory:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class CocoInfo:
    def __init__(self, year, version, contributor):
        self.year = year
        self.version = version
        self.contributor = contributor


class CocoAnnotation:
    def __init__(
        self, id, image_id, category_id, bbox, segmentation, ignore, iscrowd, area
    ):
        self.id = id
        self.image_id = image_id
        self.category_id = category_id
        self.bbox = bbox
        self.segmentation = segmentation
        self.ignore = ignore
        self.iscrowd = iscrowd
        self.area = area


class CocoGenerator:
    def __init__(self):
        self.images = []
        self.categories = []
        self.info = {}
        self.annotations = []

    def add_annotation(
        self, id, image_id, category_id, bbox, segmentation, ignore, iscrowd, area
    ):
        annotation = CocoAnnotation(
            id, image_id, category_id, bbox, segmentation, ignore, iscrowd, area
        )
        schema = AnnotationSchema()
        result = schema.dump(annotation)
        self.annotations.append(result)

    def add_image(self, id, image_name, width, height):

        # Validate the image schema
        image = CocoImage(id, image_name, width, height)
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

    def add_info(self, year, version, contributor):
        info = CocoInfo(year, version, contributor)
        schema = InfoSchema()
        result = schema.dump(info)
        self.info = result

    def get(self):
        return str(self)

    def __str__(self):
        return json.dumps(self, default=obj_dict)
