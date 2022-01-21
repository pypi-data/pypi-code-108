{
    'morpheusComponent': {
        'type': 'string',
        'required': True
    },
    'info': {
        'required': True,
        'type': 'dict',
        'schema':{
            'rolename':{
                'required': True,
                'type': 'string'
            },
            'desc':{
                'required': True,
                'type': 'string'
            },
            'roletype': {
                'required': True,
                'type': 'string'
            }
        }
    },
    'groups': {
        'valuesrules':{
            'required': True,
            'type': 'dict',
            'schema':{
                'name':{
                    'required': True,
                    'type': 'string'
                },
                'access':{
                    'required': True,
                    'type': 'string',
                    'allowed':['full', 'read', 'none']
                }
            }
        }
    },
    'roleprivs': {
        'valuesrules':{
            'required': True,
            'type': 'dict',
            'schema':{
                'name': {
                    'required': True,
                    'type': 'string'
                },
                'description': {
                    'required': True,
                    'type': 'string'
                },
                'code':{
                    'required': True,
                    'type': 'string'
                },
                'access': {
                    'required': True,
                    'type': 'string',
                    'allowed':['full', 'read', 'none', 'user', 'group', 'no', 'yes', 'provisioned']
                } 
            }
        }
    }
}