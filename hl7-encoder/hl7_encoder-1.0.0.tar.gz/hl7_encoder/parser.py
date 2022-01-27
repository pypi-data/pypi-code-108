import re
from constants import segment_name_dict, element_group, observation_id, suffixes

class Parser:

    def __init__(self, char_encoding=''):
        self.char_encoding = char_encoding

    char_encoding = ''
    field_limiter = '|'

    def message_formatter(self, raw):

        try:
            message = re.sub(r'\\u00[0-1][A-D|a-d]', '', raw)
            message = re.split(r"\\r\\n|\r\n|\\r|\r|\\n|\n", message)
            message = [segment.replace("\\", '') for segment in message]
            message = [segment.split(self.field_limiter) for segment in message]
            message = [segment for segment in message if len(segment[0]) == 3]

            def msh_exists():
                for index, segment in enumerate(message):
                    if (segment[0] == 'MSH'):
                        msh_exists.location = index
                        return True
                        break
                return False

            if msh_exists():
                if (msh_exists.location != 0):
                    message.insert(0, message.pop(msh_exists.location))
                delimiter = message[0][1]
                message[0].insert(1, self.field_limiter)

            message = [{index:
                            {value: splitted for value, splitted in enumerate(component.split('^'), 1)}
                            if re.search(r'\^', component) and component != delimiter
                            else component for index, component in enumerate(position)}
                       for position in message]

            segment_groups = list({position[0]: position[0] for position in message})

            message = {segment_name:
                           [segment for segment in message if segment[0] == segment_name]
                       for segment_name in segment_groups}

            message = {segment_name:
                           {count: dict(list(segment.items())[1:])
                            for count, segment in enumerate(message[segment_name], 1)}
                       for segment_name in segment_groups}

            return message
        except IndexError:
            return ''

    def parser(self, message):
        if (isinstance(message, str)):
            message = self.message_formatter(message)

        def flatten(field):
            if isinstance(field, dict):  # Flatten if field is a dict
                field = ' '.join(field[component] for component in field)
            if not isinstance(field, str):
                str(field)
            return field  # Always returns a string

        message = {segment_group:
                       {"name": segment_name_dict[segment_group]} |
                       {"segments": {segment: {
                           element_group[segment_group][field - 1]: flatten(message[segment_group][segment][field])
                           for field in message[segment_group][segment]
                           if (len(message[segment_group][segment][field]) != 0)}
                                     for segment in message[segment_group]}}
                   for segment_group in message}

        return message

    def service_field_results(self, message):

        if (isinstance(message, str)):
            message = self.message_formatter(message)

        try:
            message = message['OBX']
        except KeyError:
            message = ''

        def service_field_formatter(field):

            suffix_list = []
            for suffix in suffixes:
                if re.search(suffix, field):
                    suffix_list.append(suffixes[suffix])
                suffix_string = '_'.join(
                    item for item in suffix_list)

            for diagnostic_class in observation_id:

                for name in observation_id[
                    diagnostic_class]:
                    if re.search(name, field):
                        field = observation_id[diagnostic_class][name]

                    service_field_id = '_'.join(
                        [field, suffix_string])
                    service_field_id = service_field_id.replace(' ', '_')
                    service_field_id = service_field_id.rstrip('_' or ' ')

                try:
                    if list(observation_id[diagnostic_class].keys())[
                        list(observation_id[diagnostic_class].values()).index(field)]:
                        service_id = diagnostic_class
                except ValueError:
                    service_id = field

            return {"service_id": service_id, "service_field_id": service_field_id}

        def flatten(field):
            if isinstance(field, dict):
                field = ' '.join(field[component] for component in field)
            if not isinstance(field, str):
                str(field)
            return field

        results = [{
            "serviceId": service_field_formatter(flatten(message[result][3]))['service_id'],
            "serviceFieldId": service_field_formatter(flatten(message[result][3]))['service_field_id'],
            "quantitativeValue": flatten(message[result][5]),
            "unit": flatten(message[result][6]),
            "refRange": flatten(message[result][7]),
        } for result in message]

        return results