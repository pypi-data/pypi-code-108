# class Config(object):
#     S3_REGION="us-east-1"
#     STUDIO_BUCKET="flow360-studio-v1"
#     WEB_API_ENDPONT="https://webapi-dev.flexcompute.com"
#     SOLVER_VERSION="release-22.1.1"
#     WORKER_GROUP=None

#     # auth info
#     auth = None
#     user = None

#     #other
#     auth_retry = 0

class Config(object):

    S3_REGION="us-gov-west-1"
    STUDIO_BUCKET="flow360studio"
    WEB_API_ENDPONT="https://webapi.flexcompute.com"
    SOLVER_VERSION="release-22.1.1"
    WORKER_GROUP=None

    # auth info
    auth = None
    user = None

    #other
    auth_retry = 0
