class ContentType:
    '''
    A class for parsing content-type headers.
    '''

    def __init__(self, **kwargs):
        '''
        Parse a string into a ContentType object.
        '''
        self.value = kwargs['value']
        self.type = kwargs['type']
        self.subtype = kwargs['subtype']
        self.prefix = kwargs.get('prefix')
        self.suffix = kwargs.get('suffix')
        self.parameters = kwargs.get('parameters')
        self.charset = kwargs.get('charset')

    def __str__(self):
        '''
        Return the ContentType as a string.
        '''

        return self.value

    def __repr__(self):
        '''
        Return the ContentType as a string.
        '''

        return self.__str__()

    def __eq__(self, other):
        '''
        Compare the ContentType to another object.
        '''

        return self.value == other.value

    def __ne__(self, other):
        '''
        Compare the ContentType to another object.
        '''

        return self.value != other.value

    def __hash__(self):
        '''
        Return the hash of the ContentType.
        '''

        return hash(self.value)

    def __bool__(self):
        '''
        Return True if the ContentType is not empty.
        '''

        return bool(self.value)

    def __len__(self):
        '''
        Return the length of the ContentType.
        '''

        return len(self.value)


    @classmethod
    def parse(cls, value):
        '''
        Parse a string into a ContentType object.
        '''
        value = value.strip().lower()
        if not value:
            raise 'Content-Type is empty.'

        parts = value.split(';')

        # Get the content type attributes.
        media_type = parts[0].strip()
        content_type, subtype = parts[0].split('/')
        prefix = None
        suffix = None

        if '.' in subtype:
            prefix, subtype = subtype.split('.')

        if '+' in subtype:
            subtype, suffix = subtype.split('+')

        # Parse content type parameters
        parameters = {}
        charset = None

        for parameter in parts[1:]:
            parameter = parameter.strip()
            if '=' in parameter:
                key, param_value = parameter.split('=', 1)
                parameters[key.strip()] = param_value.strip()
                if key.strip() == 'charset':
                    charset = param_value
            else:
                parameters[parameter] = True

        return cls(
            value=value,
            media_type=media_type,
            type=content_type,
            prefix=prefix,
            subtype=subtype,
            suffix=suffix,
            parameters=parameters,
            charset=charset
        )


def parse(value: str) -> ContentType:
    '''
    Parse a string into a ContentType object.
    '''
    return ContentType.parse(value)
