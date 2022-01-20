from __future__ import absolute_import
from typing import List, Dict, Union, Any, Optional, BinaryIO
from datetime import datetime

from .countries_cache import CountriesCache
from .crypto_utils import (
    hash_object_record_keys,
    decrypt_record,
    encrypt_record,
    get_salted_hash,
    normalize_key,
    sanitize_obj_for_model,
)
from .exceptions import (
    StorageCryptoException,
    StorageServerException,
    StorageConfigValidationException,
    SecretsValidationException,
)
from .incountry_crypto import InCrypto
from .http_client import HttpClient
from .models import (
    AttachmentCreate,
    AttachmentMetaUpdate,
    AttachmentRequest,
    BatchDeleteFilter,
    Country,
    CustomEncryptionValidation,
    FindFilter,
    FindFilterNonHashed,
    FIND_LIMIT,
    Record,
    RecordNonHashed,
    RecordListForBatch,
    RecordListNonHashedForBatch,
    RequestOptions,
    SortFilter,
    StorageWithEnv,
    StorageOptions,
    SecretsValidation,
    USER_KEYS,
    USER_DATE_KEYS,
)
from .secret_key_accessor import SecretKeyAccessor
from .token_clients import StaticTokenClient, OAuthTokenClient
from .types import TDebugHTTPResponse, TIntFilter, TStringFilter, TRecord, TSortFilter
from .validation import validate_model, validate_encryption_enabled


class Storage:
    HTTP_DEBUG_KEY = "http_response"

    @validate_model(StorageWithEnv, exclude_to_dict={"options"}, validation_exception=StorageConfigValidationException)
    @validate_model(SecretsValidation, validation_exception=SecretsValidationException)
    @validate_model(CustomEncryptionValidation, validation_exception=StorageConfigValidationException)
    def __init__(
        self,
        environment_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        oauth_token: Optional[str] = None,
        endpoint: Optional[str] = None,
        debug: Optional[bool] = False,
        options: Optional[Dict[str, Any]] = {},
        encrypt: Optional[bool] = True,
        secret_key_accessor: Optional[SecretKeyAccessor] = None,
        custom_encryption_configs: Optional[List[dict]] = None,
    ):
        """Returns a client to talk to the InCountry storage network.

        Args:
            environment_id:
                The id of the environment you want to store records in. Defaults to None.
                Can also be set via INC_ENVIRONMENT_ID environment variable.
            client_id:
                Client Id used for oAuth authorization. Defaults to None.
                Can also be set via INC_CLIENT_ID environment variable.
            client_secret:
                Client Secret used for oAuth authorization. Defaults to None.
                Can also be set via INC_CLIENT_SECRET environment variable.
            oauth_token:
                OAuth token acquired prior to Storage initialization.
                Mutually exclusive with client_id, client_secret.
            endpoint:
                Custom storage server endpoint to use. Defaults to None.
                Can also be set via INC_ENDPOINT environment variable.
            encrypt:
                Whether to encrypt data before storing in InCountry. Defaults to True.
            secret_key_accessor:
                SecretKeyAccessor class instance which provides encryption keys details. Defaults to None.
            custom_encryption_configs:
                List of custom encryption configurations. Defaults to None.
            debug:
                Pass True to enable some debug logging. Defaults to False.
            options:
                Options dict to tweak various Storage instance aspects. Defaults to {}.

        Raises:
            StorageClientException: in case constructor param validation fails,
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases
        """

        self.debug = debug
        self.env_id = environment_id
        self.encrypt = encrypt
        self.options = StorageOptions(**options)
        self.crypto = InCrypto(secret_key_accessor, custom_encryption_configs) if self.encrypt else InCrypto()

        if oauth_token is not None:
            token_client = StaticTokenClient(token=oauth_token)
        else:
            token_client = OAuthTokenClient(
                client_id=client_id,
                client_secret=client_secret,
                scope=self.env_id,
                auth_endpoints=self.options.auth_endpoints,
                options=self.options.http_options,
            )
        self.http_client = HttpClient(
            env_id=self.env_id,
            token_client=token_client,
            endpoint=endpoint,
            debug=self.debug,
            endpoint_mask=self.options.endpoint_mask,
            countries_cache=CountriesCache(
                countries_endpoint=self.options.countries_endpoint, options=self.options.http_options
            ),
            options=self.options.http_options,
        )

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(
        {
            "condition": ("options", "hash_search_keys"),
            "values": [
                {"value": True, "model": Record},
                {"value": False, "model": RecordNonHashed},
            ],
        }
    )
    def write(
        self, country: str, record_key: str, request_options: dict = {}, **record_data: Union[str, int]
    ) -> Dict[str, TRecord]:
        """Writes record to InCountry storage network.

        Args:
            country: Country to write record to
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **record_data: Various record attributes.
                Available String attributes:
                - body, precommit_body, profile_key, service_key1, service_key2, key1, ..., key20.
                Available Int attributes:
                - range_key1, ..., range_key10

        Returns:
            Dict[str, TRecord]:
                A dict with record data you just wrote {"record": {"record_key": record_key, **record}}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """
        record = sanitize_obj_for_model({"record_key": record_key, **record_data}, Record)
        data_to_send = self.encrypt_record(record)
        (data, http_response) = self.http_client.write(
            country=country, data=data_to_send, request_options=request_options
        )
        decrypted_record = self.decrypt_record(data)
        self.validate_write_response(original_record_data=record, received_record_data=decrypted_record)
        res = {"record": decrypted_record}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(
        {
            "condition": ("options", "hash_search_keys"),
            "values": [
                {"value": True, "model": RecordListForBatch},
                {"value": False, "model": RecordListNonHashedForBatch},
            ],
        }
    )
    def batch_write(self, country: str, records: List[TRecord], request_options: dict = {}) -> Dict[str, List[TRecord]]:
        """Writes multiple records to InCountry storage network.

        Args:
            country: Country to write records to
            records: List of records. See Storage.write() for details on record attributes
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, List[TRecord]]:
                A dict with record data you just wrote {"record": {"record_key": record_key, **record}}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """

        records = [sanitize_obj_for_model(record, Record) for record in records]
        encrypted_records = [self.encrypt_record(record) for record in records]
        data_to_send = {"records": encrypted_records}
        (data, http_response) = self.http_client.batch_write(
            country=country, data=data_to_send, request_options=request_options
        )
        decrypted_records = [self.decrypt_record(r) for r in data["records"]]
        self.validate_batch_write_response(original_records_data=records, received_records_data=decrypted_records)

        res = {"records": decrypted_records}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(Record)
    def read(self, country: str, record_key: str, request_options: dict = {}) -> Dict[str, TRecord]:
        """Reads record for the given record_key

        Args:
            country: Country to search record in
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, TRecord]:
                A dict with record data {"record": TRecord}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (data, http_response) = self.http_client.read(
            country=country, record_key=record_key, request_options=request_options
        )

        res = {"record": self.decrypt_record(data)}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(SortFilter)
    @validate_model(RequestOptions)
    @validate_model(
        {
            "condition": ("options", "hash_search_keys"),
            "values": [
                {"value": True, "model": FindFilter},
                {"value": False, "model": FindFilterNonHashed},
            ],
        }
    )
    def find(
        self,
        country: str,
        limit: Optional[int] = FIND_LIMIT,
        offset: Optional[int] = 0,
        sort: Optional[List[TSortFilter]] = None,
        request_options: dict = {},
        **filters: Union[TIntFilter, TStringFilter],
    ) -> Dict[str, Any]:
        """Finds records that satisfy provided filters

        Args:
            country: Country to search records in
            limit: Maximum amount of records to be returned. Max limit is 100. Defaults to 100.
            offset: Search offset. Should be non-negative int. Defaults to 0.
            sort: Sort filter.
                An array of single-key dicts allowing to sort result data, e.g:
                [{"key1": "asc"}, {"key2": "desc"}]
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **filters: Various filters to tweak the search query.
                Available String filter keys:
                - profile_key, service_key1, service_key2, key1, ..., key20.
                Available String filter types:
                - single value: Storage.find(..., key1="v1"),
                - list of values: Storage.find(..., key1=["v1", "v2"]),
                - with $not operator: Storage.find(..., key1={"$not": "v1"}, key2={"$not":["v1", "v2"]}).

                Available Int filter keys:
                - version, range_key1, ..., range_key10.
                Available Int filter types:
                - single value: Storage.find(..., range_key1=1),
                - list of values: Storage.find(..., range_key1=[1, 2]),
                - with $not operator: Storage.find(..., range_key1={"$not": 1}, range_key2={"$not":[1, 2]}),
                - with $gt operator: Storage.find(..., range_key1={"$gt": 1}),
                - with $gte operator: Storage.find(..., range_key1={"$gte": 1}),
                - with $lt operator: Storage.find(..., range_key1={"$lt": 1}),
                - with $lte operator: Storage.find(..., range_key1={"$lte": 1}),
                - with comparison operators combination: Storage.find(..., range_key1={"$gt": 1, $lte": 10}),

        Returns:
            Dict[str, Any]:
                Found records with some meta information and errors data (if any) as dict:
                    {
                        "meta": {
                            "count": int,
                            "limit": int,
                            "offset": int,
                            "total": int,
                        },
                        "records": List[TRecord],
                        "errors": List,
                    }

                In case of any error occurs during records decryption, method will not raise StorageCryptoException
                but rather add raw record and the exception itself to "errors" list in reponse dict
                ({"errors": [..., {"rawData": TRecord, "error": StorageCryptoException}]})

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageException: in any other cases.
        """
        filter_params = hash_object_record_keys(
            sanitize_obj_for_model(filters, FindFilter, omit_none=False),
            self.env_id,
            normalize_keys=self.options.normalize_keys,
            hash_search_keys=self.options.hash_search_keys,
        )

        options = {"limit": limit, "offset": offset}

        if sort is not None and len(sort) > 0:
            options["sort"] = sort

        (data, http_response) = self.http_client.find(
            country=country, data={"filter": filter_params, "options": options}, request_options=request_options
        )

        decoded_records = []
        undecoded_records = []
        for record in data["data"]:
            try:
                decoded_records.append(self.decrypt_record(record))
            except StorageCryptoException as error:
                undecoded_records.append({"rawData": record, "error": error})

        res = {
            "meta": data["meta"],
            "records": decoded_records,
        }
        if len(undecoded_records) > 0:
            res["errors"] = undecoded_records
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(SortFilter)
    @validate_model(
        {
            "condition": ("options", "hash_search_keys"),
            "values": [
                {"value": True, "model": FindFilter},
                {"value": False, "model": FindFilterNonHashed},
            ],
        }
    )
    def find_one(
        self,
        country: str,
        offset: Optional[int] = 0,
        sort: Optional[List[TSortFilter]] = None,
        request_options: dict = {},
        **filters: Union[TIntFilter, TStringFilter],
    ) -> Union[None, Dict[str, Dict]]:
        """Finds record that satisfies provided filters

        Args:
            country: Country to search record in
            offset: Search offset. Should be non-negative int. Defaults to 0.
            sort: Sort filter.
                An array of single-key dicts allowing to sort result data, e.g:
                [{"key1": "asc"}, {"key2": "desc"}]
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **filters: Various filters to tweak the search query.
                Available String filter keys:
                - profile_key, service_key1, service_key2, key1, ..., key20,
                - search_keys - for partial match search on key1, ..., key20.
                Available String filter types:
                - single value: Storage.find_one(..., key1="v1"),
                - list of values: Storage.find_one(..., key1=["v1", "v2"]),
                - with $not operator: Storage.find_one(..., key1={"$not": "v1"}, key2={"$not":["v1", "v2"]}).

                Available Int filter keys:
                - version, range_key1, ..., range_key10.
                Available Int filter types:
                - single value: Storage.find_one(..., range_key1=1),
                - list of values: Storage.find_one(..., range_key1=[1, 2]),
                - with $not operator: Storage.find_one(..., range_key1={"$not": 1}, range_key2={"$not":[1, 2]}),
                - with $gt operator: Storage.find_one(..., range_key1={"$gt": 1}),
                - with $gte operator: Storage.find_one(..., range_key1={"$gte": 1}),
                - with $lt operator: Storage.find_one(..., range_key1={"$lt": 1}),
                - with $lte operator: Storage.find_one(..., range_key1={"$lte": 1}),
                - with comparison operators combination: Storage.find_one(..., range_key1={"$gt": 1, $lte": 10}).

        Returns:
            Union[None, Dict[str, Dict]]:
                Found record (if any) or None:
                    {
                        "record": TRecord,
                    }

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageException: in any other cases.
        """

        find_res = self.find(
            country=country, limit=1, offset=offset, sort=sort, request_options=request_options, **filters
        )

        res = {"record": find_res["records"][0] if len(find_res["records"]) else None}
        if self.debug:
            return self.add_http_response_debug(res, find_res[Storage.HTTP_DEBUG_KEY])
        return res if res["record"] else None

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(Record)
    def delete(self, country: str, record_key: str, request_options: dict = {}) -> Dict[str, bool]:
        """Deletes record for the given record_key

        Args:
            country:  Country to search record in
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, bool]:
                {"success": True} in case the record is successfully deleted

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageException: in any other cases.
        """

        record_key_hashed = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (_, http_response) = self.http_client.delete(
            country=country, record_key=record_key_hashed, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(BatchDeleteFilter)
    def batch_delete(self, country: str, record_key: List[str], request_options: dict = {}) -> Dict[str, bool]:
        """Deletes records for the given list of 'record_key's

        Args:
            country:  Country to search record in
            record_key: List of record primary keys
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, bool]:
                {"success": True} in case records are successfully deleted

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for one of the given 'record_key's).
            StorageException: in any other cases.
        """

        filter_params = hash_object_record_keys(
            sanitize_obj_for_model({"record_key": record_key}, BatchDeleteFilter, omit_none=False),
            self.env_id,
            normalize_keys=self.options.normalize_keys,
            hash_search_keys=self.options.hash_search_keys,
        )

        (_, http_response) = self.http_client.batch_delete(
            country=country, data={"filter": filter_params}, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    @validate_encryption_enabled
    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(FindFilter)
    def migrate(self, country: str, limit: Optional[int] = FIND_LIMIT, request_options: dict = {}) -> Dict[str, int]:
        """Migrates records in InCountry storage to the latest encryption key.

        Unavailable when encrypt=False is passed to Storage constructor

        Args:
            country: Country to migrate records in
            limit: Maximum amount of records to be migrated at once. Max limit is 100. Defaults to 100
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, int]:
                Migration result - total amount of successfully migrated records and total records left to migrate
                (total records left with other encryption key versions):
                {
                    "migrated": int,
                    "total_left": int,
                }

        Raises:
            StorageClientException: in case method param validation fails (or in case encryption is disabled).
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageException: in any other cases.
        """
        current_secret_version = self.crypto.get_current_secret_version()
        find_res = self.find(
            country=country, limit=limit, version={"$not": current_secret_version}, request_options=request_options
        )
        records_to_migrate_count = len(find_res["records"])

        batch_write_res = None

        if records_to_migrate_count > 0:
            batch_write_res = self.batch_write(
                country=country, records=find_res["records"], request_options=request_options
            )

        res = {
            "migrated": records_to_migrate_count,
            "total_left": find_res["meta"]["total"] - records_to_migrate_count,
        }
        if "errors" in find_res:
            res["errors"] = find_res["errors"]

        if not self.debug:
            return res

        return self.add_http_response_debug(
            res,
            [find_res[Storage.HTTP_DEBUG_KEY], batch_write_res[Storage.HTTP_DEBUG_KEY]]
            if batch_write_res
            else [find_res[Storage.HTTP_DEBUG_KEY]],
        )

    @validate_model(Country)
    @validate_model(RequestOptions)
    def health_check(
        self,
        country: str,
        request_options: dict = {},
    ) -> Dict[str, bool]:
        (data, http_response) = self.http_client.health_check(
            country=country,
            request_options=request_options,
        )

        res = {"result": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(AttachmentCreate)
    def add_attachment(
        self,
        country: str,
        record_key: str,
        file: Union[BinaryIO, str],
        mime_type: str = None,
        upsert: bool = False,
        request_options: dict = {},
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (data, http_response) = self.http_client.add_attachment(
            country=country,
            record_key=record_key,
            file=file,
            upsert=upsert,
            mime_type=mime_type,
            request_options=request_options,
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(AttachmentRequest)
    def get_attachment_file(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, Dict]:
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (data, http_response) = self.http_client.get_attachment_file(
            country=country, record_key=record_key, file_id=file_id, request_options=request_options
        )

        res = {
            "attachment_data": data,
        }
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(AttachmentRequest)
    def get_attachment_meta(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (data, http_response) = self.http_client.get_attachment_meta(
            country=country, record_key=record_key, file_id=file_id, request_options=request_options
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(AttachmentRequest)
    @validate_model(AttachmentMetaUpdate)
    def update_attachment_meta(
        self,
        country: str,
        record_key: str,
        file_id: str,
        filename: str = None,
        mime_type: str = None,
        request_options: dict = {},
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        meta = {}
        if filename is not None:
            meta["filename"] = filename
        if mime_type is not None:
            meta["mime_type"] = mime_type
        (data, http_response) = self.http_client.update_attachment_meta(
            country=country, record_key=record_key, file_id=file_id, meta=meta, request_options=request_options
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country)
    @validate_model(RequestOptions)
    @validate_model(AttachmentRequest)
    def delete_attachment(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, bool]:
        record_key = get_salted_hash(self.normalize_key(record_key), self.env_id)
        (_, http_response) = self.http_client.delete_attachment(
            country=country, record_key=record_key, file_id=file_id, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    ###########################################
    # Common functions
    ###########################################
    def add_http_response_debug(
        self,
        data: dict,
        http_response_data: TDebugHTTPResponse,
    ) -> dict:
        if self.debug:
            data[Storage.HTTP_DEBUG_KEY] = http_response_data
        return data

    def log(self, *args):
        if self.debug:
            print("[incountry] ", args)

    def encrypt_record(self, record):
        return encrypt_record(
            self.crypto,
            record,
            self.env_id,
            normalize_keys=self.options.normalize_keys,
            hash_search_keys=self.options.hash_search_keys,
        )

    def decrypt_record(self, record):
        return decrypt_record(self.crypto, record)

    def validate_write_response(self, original_record_data, received_record_data):
        for key in USER_KEYS:
            if key not in original_record_data and key not in received_record_data:
                continue
            has_missing_keys = (
                key not in original_record_data
                and key in received_record_data
                or key in original_record_data
                and key not in received_record_data
            )
            has_different_user_date = not has_missing_keys and (
                key in USER_DATE_KEYS and original_record_data[key] != received_record_data[key].isoformat()
            )
            has_different_non_date_key = not has_missing_keys and (
                key not in USER_DATE_KEYS and original_record_data[key] != received_record_data[key]
            )
            if has_missing_keys or has_different_user_date or has_different_non_date_key:
                raise StorageServerException(
                    f"response validation failed. Return data doesn't match the one sent. Key mismatch: {key}"
                )

    def validate_batch_write_response(self, original_records_data, received_records_data):
        for original_record_data in original_records_data:
            received_record_data = next(
                (
                    item
                    for item in received_records_data
                    if item.get("record_key") == original_record_data.get("record_key")
                ),
                None,
            )
            self.validate_write_response(
                original_record_data=original_record_data, received_record_data=received_record_data
            )

    def normalize_key(self, key):
        return normalize_key(key, self.options.normalize_keys)
