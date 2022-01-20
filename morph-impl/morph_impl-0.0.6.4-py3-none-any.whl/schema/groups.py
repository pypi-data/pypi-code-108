{
    'morpheusComponent': {
        'type': 'string',
        'required': True
    },
    'groups': {
        'valuesrules': {
        'required': True,
        'type': 'dict',
        'schema':{
            'name':{
                'required': True,
                'type': 'string'
            },
            'description':{
                'required': True,
                'type': 'string'
            },
            'location': {
                'required': True,
                'type': 'string'
            },
            'code':{
                'required': True,
                'type': 'string'
            }
        }
        }
    }
}