{
    'cloudType': {
        'type': 'string',
        'required': True
    },
    'clouds': {
        'valuesrules':{
        'required': True,
        'type': 'dict',
        'schema': {
            'name': {
                'required': True,
                'type': 'string'
            },
            'description': {
                'required': True,
                'type': 'string'
            },
            'groupID': {
                'required': True,
                'keysrules':{
                    'required': True,
                    'type': 'dict'
                }
            },
            'code': {
                'required': True,
                'type': 'string'
            },
            'certificateProvider': {
                'required': True,
                'type': 'string'
            },
            'importExisting': {
                'required': True,
                'type': 'string'
            },
            'endpoint': {
                'required': True,
                'type': 'string'
            },
            'accessKey': {
                'required': True,
                'type': 'string'
            },
            'secretKey': {
                'required': True,
                'type': 'string'
            },
            'code1': {
                'required': True,
                'type': 'string'
            },
            'location': {
                'required': True,
                'type': 'string'
            },
            'visibility': {
                'required': True,
                'type': 'string'
            }
        }   
    }
    }
}
