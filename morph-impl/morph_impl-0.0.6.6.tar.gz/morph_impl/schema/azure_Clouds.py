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
            'cloudType': {
                'required': True,
                'type': 'string'
            },
            'importExisting': {
                'required': True,
                'type': 'string'
            },
            'subscriberId': {
                'required': True,
                'type': 'string'
            },
            'tenantId': {
                'required': True,
                'type': 'string'
            },
            'clientId': {
                'required': True,
                'type': 'string'
            },
            'clientSecret': {
                'required': True,
                'type': 'string'
            },
            'regionCode': {
                'required': True,
                'type': 'string'
            },
            'accountType': {
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
