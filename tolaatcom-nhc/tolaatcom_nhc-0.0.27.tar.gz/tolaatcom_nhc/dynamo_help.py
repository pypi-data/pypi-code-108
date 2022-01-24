
class DynamoHelp:

    @classmethod
    def _type_value(cls, dynamo_value):
        if type(dynamo_value) != dict:
            raise Exception()
        return next(iter(dynamo_value.items()))

    @classmethod
    def field_to_value(cls, field):
        field_type, field_value = DynamoHelp._type_value(field)
        if field_type == 'N':
            return int(field_value)
        elif field_type == 'S':
            return field_value
        elif field_type == 'BOOL':
            return bool(field_value)
        elif field_type == 'SS':
            return [str(x) for x in field_value]
        elif field_type == 'NS':
            return [int(x) for x in field_value]
        elif field_type == 'M':
            new_map = {}
            for k2, v2 in field_value.items():
                new_map[k2] = DynamoHelp.field_to_value(v2)
            return new_map
        elif field_type == 'L':
            return [DynamoHelp.field_to_value(x) for x in field_value]
        elif field_type == 'B':
            return field_value
        else:
            raise Exception()

    @classmethod
    def item_to_obj(cls, item):
        m = {}
        for attribute_name, attribute_value in item.items():
            m[attribute_name] = DynamoHelp.field_to_value(attribute_value)

        return m

    @classmethod
    def obj_to_item(cls, obj):
        item = {}
        for k, v in obj.items():
            if type(v) == dict:
                item[k] = {'M': DynamoHelp.obj_to_item(v)}
            if type(v) == str:
                item[k] = {'S': v}
            if type(v) == list:
                item[k] = {'L': [DynamoHelp.obj_to_item(elem) for elem in v]}

        return item




