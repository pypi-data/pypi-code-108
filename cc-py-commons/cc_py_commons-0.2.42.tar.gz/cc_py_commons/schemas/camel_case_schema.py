from marshmallow import Schema, fields

class CamelCaseSchema(Schema):
  """Schema that uses camel-case for its external representation
  and snake-case for its internal representation.
  """

  def on_bind_field(self, field_name, field_obj):
      field_obj.data_key = self.__camelcase(field_obj.data_key or field_name)

  def __camelcase(self, s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)