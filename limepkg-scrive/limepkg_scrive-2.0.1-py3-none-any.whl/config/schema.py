from marshmallow import Schema, fields


def create_schema(application):
    class ConfigSchema(Schema):
        scriveHost = fields.URL(
            title="Scrive - Host",
            description="The host of this add-on. E.g. https://lime.scrive.com",
            default="https://lime.scrive.com",
            required=True)

        class Meta:
                ordered = True

    return ConfigSchema()
