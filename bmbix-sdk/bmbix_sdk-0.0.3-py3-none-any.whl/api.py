"""Bmbix API for AI agents"""

from base64 import b64encode
import hashlib
import logging
from typing import NamedTuple

from oauthlib.oauth2 import BackendApplicationClient   # type:ignore
from requests_oauthlib import OAuth2Session  # type:ignore

from bmb_martlet_organization_client import (  # type: ignore
    ApiClient,
    Configuration,
    MessagesApi,
    MessageResponse as MessageResponseGW,
    Message as MessageGW,
    SubmissionResponse as SubmissionResponseGW,
    Submission as SubmissionGW,
)

import bmb_klondike_client as klondike


from .encrypt import (
    bmbix_fetch_public_key,
    encrypt_rubric,
    generate_symmetric_key,
    pack_rubric,
    encrypt_aes,
)

from .util import unscramble

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

Row = NamedTuple("Row", [("id", str), ("content", str)])


def build_token_manager(
    token_url,
    client_id,
    client_secret,
):
    def x():
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        return token
    return x


def fetch_message(
    credentials_func,
    context,
    message_id,
) -> MessageGW:

    logger.info(">>> received message_id: %s", message_id)

    bmbix_organization = context["bmbix_organization"]
    bmbix_address = context["bmbix_address"]

    try:
        token = credentials_func()
    except Exception:
        logger.exception("Getting bmbix credentials barfed")

    logger.info("token: %s", token)

    configuration = Configuration()
    configuration.access_token = token["access_token"]

    api_client = ApiClient(configuration)
    messages_api = MessagesApi(api_client)
    message_response: MessageResponseGW = messages_api.select(
            bmbix_organization,
            bmbix_address,
            message_id,
        )
    logger.info("<<<<<^^^^^>>>>>: %s", message_response)
    return message_response.message


def submit_message(
    token_manager,
    sender_bmbix_address,
    reference: str,
    document: str,
    bmbix_destination_address: str,
    content_media_type: str,
) -> str:

    bmbix_address = sender_bmbix_address

    configuration = Configuration()
    token = token_manager()
    configuration.access_token = token["access_token"]

    api_client = ApiClient(configuration)

    resource_public_key = bmbix_fetch_public_key(
        api_client=api_client,
        resource_type="addresses",
        resource_id=bmbix_destination_address,
    )
    logger.info("resource_public_key: %s", resource_public_key)

    symmetric_key: bytes = generate_symmetric_key(32)

    nonce, encrypted_content, tag = encrypt_aes(
        plaintext=document.encode("utf-8"),
        key=symmetric_key,
    )
    plain_rubric: bytes = pack_rubric(
        algorithm=b"AES",
        key=symmetric_key,
        nonce=nonce,
        tag=tag,
    )
    encrypted_rubric: bytes = encrypt_rubric(
        public_key=resource_public_key.public_key,
        rubric_plaintext=plain_rubric,
    )
    b64_encrypted_content: str = b64encode(encrypted_content).decode("utf-8")
    b64_encrypted_rubric: str = b64encode(encrypted_rubric).decode("utf-8")

    message = MessageGW(
        source_address_id=bmbix_address,
        destination_address_id=bmbix_destination_address,
        sender_reference=reference,
        content_media_type=content_media_type,
        checksum_algorithm="sha256",
        checksum=hashlib.sha256(document.encode("utf-8")).hexdigest(),
        content=b64_encrypted_content,
        decryption_rubric=b64_encrypted_rubric,
        recipient_public_key_fingerprint=resource_public_key.fingerprint,
    )
    logger.info("message_gw: %s", message)

    api = MessagesApi(api_client)
    submission_response: SubmissionResponseGW = api.insert(
        message,
    )
    submission: SubmissionGW = submission_response.submission
    logger.debug("submission: %s", submission)
    return submission


def submit_unaddressed_message(
    token_manager,
    sender_bmbix_address,
    reference: str,
    document: str,
    content_media_type: str,
    local_account: str,
    summary: str,
) -> str:

    bmbix_address = sender_bmbix_address

    configuration = klondike.Configuration()
    token = token_manager()
    configuration.access_token = token["access_token"]

    api_client = klondike.ApiClient(configuration)

    content: bytes = document.encode("utf-8")
    b64_content: str = b64encode(content).decode("utf-8")

    unaddressed_message = klondike.UnaddressedMessage(
        checksum=hashlib.sha256(document.encode("utf-8")).hexdigest(),
        checksum_algorithm="sha256",
        from_address_id=bmbix_address,
        message_content=b64_content,
        message_type=content_media_type,
        sender_reference=reference,
        local_account=local_account,
        summary=summary,
    )
    logger.info("unaddressed_message: %s", unaddressed_message)

    api = klondike.UnaddressedMessagesApi(api_client)
    unaddressed_message_response = api.insert_unaddressed_message(
        body=unaddressed_message,
        address_id=bmbix_address,
    )
    returned_unaddressed_message = unaddressed_message_response.unaddressed_message  # noqa
    return returned_unaddressed_message
