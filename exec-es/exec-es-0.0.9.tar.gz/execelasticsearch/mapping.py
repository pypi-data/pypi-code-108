class MappingMethod:
    class SearchBody:
        Template = dict(
            exists={"query": {"bool": {"must": {"exists": {"field": "<<field>>"}}}}},
            not_exists={"query": {"bool": {"must_not": {"exists": {"field": "<<field>>"}}}}},
            match={"query": {"match": {"<<field>>": "<<value>>"}}},
        )

        @classmethod
        def update(cls, body_type, target_key, replace_value):
            data = cls.__upack(cls.Template[body_type])
            while True:
                if data['key'] == target_key:
                    data['data'][data['key']] = replace_value
                    break
                data = cls.__upack(data['value'])

        @classmethod
        def __upack(cls, data):
            data_key, = data
            return {'key': data_key, 'value': data[data_key], 'data': data}


if __name__ == '__main__':
    MappingMethod.SearchBody.update('match', 'match', {"<<field>>": {"query": "<<value>>"}})
    print(MappingMethod.SearchBody.Template)
