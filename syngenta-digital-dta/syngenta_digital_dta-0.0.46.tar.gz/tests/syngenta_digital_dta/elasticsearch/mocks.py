class MockESAdapter:
    def __init__(self, **kwargs):
        self.index = 'test'
        self.endpoint = kwargs.get('endpoint')
        self.port = 9300
        self.connection = None
        self.authentication = kwargs.get('authentication')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')


def get_schema():
    return {
        'type': 'object',
        'properties': {
            'company_name': {
                'type': 'string',
                'minLength': 1
            },
            'company_email': {
                'type': 'string',
                'format': 'email'
            },
            'address1': {
                'type': 'string',
                'minLength': 1
            },
            'address2': {
                'type': 'string',
                'minLength': 1
            },
            'city': {
                'type': 'string',
                'minLength': 1
            },
            'state': {
                'type': 'string',
                'minLength': 1
            },
            'zipcode': {
                'type': 'string',
                'minLength': 1
            },

            'phone': {
                'type': 'string',
                'minLength': 1
            },
            'salesforce_id': {
                'type': 'string',
                'minLength': 1
            },
            'sap_id': {
                'type': 'string',
                'minLength': 1
            },
            'active': {
                'type': 'boolean'
            },
            'created': {
                'type': 'string',
                'format': 'date-time'
            },
            'modified': {
                'type': 'string',
                'format': 'date-time'
            },
            'company_type': {
                'type': 'string',
                'enum': [
                    'grain-receiver',
                    'reseller',
                    '3PO'
                ]
            },
            'geocodes': {
                'type': 'array',
            },
            'geojson': {
                'type': 'object',
                'properties': {
                    'thing': {
                        'type': 'string'
                    },
                    'shared': {
                        'type': 'string'
                    }
                }
            },
            'shared': {
                'type': 'string'
            },
            'unknown_obj': {
                'type': 'object'
            },
            'details': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'details_name': {
                            'type': 'string'
                        },
                        'details_value': {
                            'type': 'string'
                        }
                    }
                }
            }
        }
    }


def get_mapping(company_name_type = 'text'):
    return {
        'properties': {
            'company_name': {
                'type': company_name_type
            },
            'company_email': {
                'type': 'text',
                'analyzer': 'url_email_analyzer'
            },
            'address1': {
                'type': 'text'
            },
            'address2': {
                'type': 'text'
            },
            'city': {
                'type': 'text'
            },
            'state': {
                'type': 'text'
            },
            'zipcode': {
                'type': 'text'
            },
            'phone': {
                'type': 'text'
            },
            'salesforce_id': {
                'type': 'text'
            },
            'sap_id': {
                'type': 'text'
            },
            'active': {
                'type': 'boolean'
            },
            'created': {
                'type': 'date',
                'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||strict_date_optional_time"
            },
            'modified': {
                'type': 'date',
                'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||strict_date_optional_time"
            },
            'company_type': {
                'type': 'text'
            },
            'details': {
                'type': 'nested'
            }
        }
    }
