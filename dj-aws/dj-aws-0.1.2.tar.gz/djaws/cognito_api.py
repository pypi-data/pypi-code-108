import boto3
import jwt
from botocore.exceptions import ClientError

from djaws import decorators as aws_decorators
from djaws.cognito.exceptions import (CognitoError, CognitoUsernameExistsError, CognitoUserNotFoundError,
                                    CognitoUserPasswordValidationError, CognitoUserNotAuthorizedError,
                                    CognitoUserNotConfirmedError)
from djaws.utils import ClientErrorResponse
from djstarter import utils as core_utils


def new_cognito_client(*args, **kwargs):
    session = boto3.session.Session()
    return session.client('cognito-idp', *args, **kwargs,)


@aws_decorators.wrap_and_reraise_cognito_errors
def signup_new_user(cognito_client, client_id, name, username, password, phone_number):
    kwargs = {
        'ClientId': client_id,
        'Username': username,
        'Password': password,
        'UserAttributes': [
            {
                'Name': "name",
                'Value': name
            },
            {
                'Name': "phone_number",
                'Value': phone_number
            }
        ],
    }
    try:
        r_signup = cognito_client.sign_up(**kwargs)
    except ClientError as e:
        raise CognitoClientErrorResponse(e.response).to_cognito_exception
    else:
        return SignupNewUserResponse(r_signup)


class SignupNewUserResponse(core_utils.SerializerMixin):

    class CodeDeliveryDetails:
        def __init__(self, data):
            self.attribute_name = data.get('AttributeName')
            self.delivery_medium = data.get('DeliveryMedium')
            self.destination = data.get('Destination')

    def __init__(self, data):
        self.code_deliver_details = self.CodeDeliveryDetails(data.get('CodeDeliveryDetails', dict()))
        self.user_confirmed = data.get('UserConfirmed')
        self.user_sub = data.get('UserSub')


@aws_decorators.wrap_and_reraise_cognito_errors
def admin_confirm_sign_up(cognito_client, user_pool_id, username):
    try:
        r_confirm = cognito_client.admin_confirm_sign_up(
            UserPoolId=user_pool_id,
            Username=username
        )
    except ClientError as e:
        raise CognitoClientErrorResponse(e.response).to_cognito_exception
    else:
        return AdminConfirmNewUserResponse(r_confirm)


class AdminConfirmNewUserResponse(core_utils.SerializerMixin):
    class ResponseMetadata:
        class HTTPHeaders:
            def __init__(self, data):
                self.date = data.get('date')
                self.content_type = data.get('content-type')
                self.content_length = data.get('content-length')
                self.connection = data.get('connection')
                self.x_amzn_requestid = data.get('x-amzn-requestid')

        def __init__(self, data):
            self.request_id = data.get('RequestId')
            self.http_status_code = data.get('HTTPStatusCode')
            self.http_headers = self.HTTPHeaders(data.get('HTTPHeaders', dict()))
            self.retry_attempts = data.get('RetryAttempts')

    def __init__(self, data):
        self.response_metadata = self.ResponseMetadata(data.get('ResponseMetadata', dict()))


@aws_decorators.wrap_and_reraise_cognito_errors
def login(cognito_client, user_pool_client_id, username, password):
    try:
        r_login = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
            ClientId=user_pool_client_id
        )
    except ClientError as e:
        raise CognitoClientErrorResponse(e.response).to_cognito_exception
    else:
        return InitAuthResponse(r_login)


@aws_decorators.wrap_and_reraise_cognito_errors
def admin_login(cognito_client, user_pool_client_id, user_pool_id, username, password):
    try:
        r_login = cognito_client.admin_initiate_auth(
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            },
            ClientId=user_pool_client_id,
            UserPoolId=user_pool_id,
        )
    except ClientError as e:
        raise CognitoClientErrorResponse(e.response).to_cognito_exception
    return InitAuthResponse(r_login)


@aws_decorators.wrap_and_reraise_cognito_errors
def admin_refresh_access_token(cognito_client, user_pool_client_id, user_pool_id, refresh_token):
    """
    :param cognito_client:
    :param user_pool_client_id:
    :param user_pool_id:
    :param refresh_token:
    :return:
    :exception MarzUserNotAuthorizedError
    """
    try:
        r_refresh = cognito_client.admin_initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            },
            ClientId=user_pool_client_id,
            UserPoolId=user_pool_id,
        )
    except ClientError as e:
        raise CognitoClientErrorResponse(e.response).to_cognito_exception
    return InitAuthResponse(r_refresh)


class InitAuthResponse(core_utils.SerializerMixin):
    class AuthenticationResult:
        def __init__(self, data):
            self.access_token = data.get('AccessToken')
            self.expires_in = data.get('ExpiresIn')
            self.id_token = data.get('IdToken')
            self.refresh_token = data.get('RefreshToken')
            self.token_type = data.get('TokenType')

    def __init__(self, data):
        self.authentication_result = self.AuthenticationResult(data.get('AuthenticationResult', dict()))
        self.challenge_parameters = data.get('ChallengeParameters')

    @property
    def user_id(self):
        return jwt.decode(self.authentication_result.access_token, options={"verify_signature": False})['sub']

    @property
    def is_admin_user(self):
        scope = jwt.decode(self.authentication_result.access_token, options={"verify_signature": False})['scope']
        return scope == 'aws.cognito.signin.user.admin'

    @property
    def access_token(self):
        return self.authentication_result.access_token

    @property
    def refresh_token(self):
        return self.authentication_result.refresh_token


class CognitoClientErrorResponse(ClientErrorResponse):
    EXC_MAP = {
        'InternalErrorException': CognitoError,
        'InvalidPasswordException': CognitoUserPasswordValidationError,
        'NotAuthorizedException': CognitoUserNotAuthorizedError,
        'UsernameExistsException': CognitoUsernameExistsError,
        'UserNotConfirmedException': CognitoUserNotConfirmedError,
        'UserNotFoundException': CognitoUserNotFoundError,
    }

    @property
    def to_cognito_exception(self):
        return self.EXC_MAP.get(self.exception_class, CognitoError)(self.__dict__)
