DATASET_TYPES = [
    ('AdLogs',
     """Impressions or Clicks data from AdServer logs.  Each record represents an impression or click event and 
     contains an identity column and a timestamp column."""),
    ('Transaction',
     """Purchase or Order data with fields like Price, Quantity, and Transaction Date.  
     Used to understand busying behaviour and user segmentation with algorithms like R(ecency)F(requency)M(onetary)"""),
    ('CRM',
     """Categorical user data set with one row per user with one identity column and multiple columns, 
     each representing a user attribute from the CRM system (e.g., Gender, Household Income, MemberSince, etc.)"""),
    ('UserSegmentMap',
     """Denormalized dataset of user-segment membership.  
     Typically contains 3 columns - Identity column, AudienceSegmentId, AudienceSegmentName - with multiple records
     for a given identity (or user)"""),
    ('IDENTITY_GRAPH',
     """Identity Graph,
     Typically contains 3 columns - Identity column, Id type column, Parent Id"""),
]

DATASET_TYPE_NAMES = [dt[0] for dt in DATASET_TYPES]


def ls_datasets():
    for x in DATASET_TYPES:
        print('%s - %s' % (x[0], x[1]))


def valid_dataset(dataset_type: str):
    return dataset_type in DATASET_TYPE_NAMES


IDENTITY_TYPES = [
    ('SHA1', "Hashed emails using the SHA1 hashing algorithm"),
    ('SHA256', "Hashed emails using the SHA256 hashing algorithm"),
    ('MD5', "Hashed emails using the MD5 hashing algorithm"),
    ('MAID', "Mobile Ad Identifiers - Android (AAID) and/or iPhone (IDFA)"),
    ('Email', 'Plain text Email'),
    ('CUSTOMER_FIRST_PARTY_ID', 'First Party ID (Cookie, for example) provided by a partner'),
    ('HOUSEHOLD_ID', 'Household Identifier from ID graph provider'),
    ('PERSON_ID', 'Person (or People) Identifier from ID graph provider')
]

IDENTITY_TYPE_NAMES = [x[0] for x in IDENTITY_TYPES]


def ls_identity_types():
    for x in IDENTITY_TYPES:
        print('%s - %s' % (x[0], x[1]))


def valid_identity_type(identity_type: str):
    return identity_type in IDENTITY_TYPE_NAMES
