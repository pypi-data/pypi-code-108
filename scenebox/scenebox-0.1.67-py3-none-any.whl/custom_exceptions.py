"""custom exceptions for the data platform Copyright 2020 Caliber Data Labs."""
#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#


class SearchError(Exception):
    pass


class InvalidFileError(Exception):
    pass


class FileSizeCheckError(Exception):
    pass


class AssetError(Exception):
    pass


class JobError(Exception):
    pass


class CredentialsError(Exception):
    pass


class ResponseError(Exception):
    pass


class SessionManagerError(Exception):
    pass


class InvalidURLError(Exception):
    pass


class IndexingException(Exception):
    pass


class InvalidArgumentsError(Exception):
    pass


class MetadataNotFoundError(Exception):
    pass


class InvalidAnnotationError(Exception):
    pass


class InvalidConfigError(Exception):
    pass


class ZippingError(Exception):
    pass


class SetsError(Exception):
    pass


class InvalidEventError(Exception):
    pass


class DataEnrichmentError(Exception):
    pass


class SessionError(Exception):
    pass


class InvalidTimeError(Exception):
    pass


class ProjectError(Exception):
    pass


class OperationError(Exception):
    pass


class InvalidAuthorization(Exception):
    pass


class CacheError(Exception):
    pass


class UserManagerError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class OwnershipAlreadyExistsError(Exception):
    pass


class IdentityError(Exception):
    pass


class AssetCompressionError(Exception):
    pass


class ThumbnailNotAvailableError(Exception):
    pass


class InvalidInfluenceTypeError(Exception):
    pass


class KafkaProducerError(Exception):
    pass


class KafkaConsumerError(Exception):
    pass


class UsageTrackerError(Exception):
    pass


class QuotaSystemError(Exception):
    pass


class QuotaExceedError(Exception):
    pass


class UploadError(Exception):
    pass


class SimilaritySearchError(Exception):
    pass

