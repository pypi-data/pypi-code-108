client_schema = {
    'type': 'object',
    'required': ['type'],
    'properties': {
        'name': {
          'type': 'string',
        },
        'logo': {
          'type': 'string',
          'readOnly': True,
          'description': 'The link to the logo is created by the backend. The logo of the company has to be added to the s3 in the folder client_logos with the following name: company_name_white.svg',
        },
        'logo_white': {
          'type': 'string',
          'readOnly': True,
          'description': 'The link to the logo is created by the backend. The white logo of the company has to be added to the s3 in the folder client_logos with the following name: company_name_white.svg',
        },
    }
}
