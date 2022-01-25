import json

TEST_STORED_CREDENTIAL_BACKEND_PATH = 'credentials.credential_backends.OAuthAccessToken'
TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS = {
    'access_token': 'access_token_data'
}
TEST_STORED_CREDENTIAL_BACKEND_DATA = json.dumps(
    obj=TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS
)
TEST_STORED_CREDENTIAL_LABEL = 'test credential'
TEST_STORED_CREDENTIAL_LABEL_EDITED = 'test credential edited'
