#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import json
import logging

from django.conf import settings

from .api_handler import ApiHandler
from .docusign_helper import process_docusign_webhook

LOGGER = logging.getLogger("root")


class DocuSignClient:
    def __init__(self, access_token: str):
        self.account_id = settings.DOCUSIGN_API_ACCOUNT_ID
        self.api_key = f"Bearer {access_token}"

    def generate_docusign_preview_url(self, params: dict, log_config: dict = None):
        LOGGER.info("Generating Docusign Preview Url")
        if not (
            "envelope_id" in params
            and params["envelope_id"] is not None
            or "authentication_method" in params
            and params["authentication_method"] is not None
            or "email" in params
            and params["email"] is not None
            or "user_name" not in params
            and params["user_name"] is not None
            or "client_user_id" not in params
            and params["client_user_id"] is not None
            or "return_url" not in params
            and params["return_url"] is not None
        ):
            raise Exception("Invalid input dict for generate_docusign_preview_url")
            LOGGER.error("Invalid input dict for generate_docusign_preview_url")

        envelope_id = params["envelope_id"]
        authentication_method = params["authenticationMethod"]
        email = params["email"]
        user_name = params["userName"]
        client_user_id = params["clientUserId"]
        return_url = params["returnUrl"]

        url = settings.DOCUSIGN_API_ENDPOINT

        preview_resource_path = (
            f"{self.account_id}/envelopes/{envelope_id}/views/recipient"
        )
        preview_url = url + preview_resource_path
        preview_data = {
            "authenticationMethod": authentication_method,
            "email": email,
            "userName": user_name,
            "clientUserId": client_user_id,
            "returnUrl": return_url,
        }
        LOGGER.info(
            "Calling API Handler's send request for generate_docusign_preview_url"
        )
        docusign_handler = ApiHandler(preview_url, self.api_key)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(preview_data), log_config=log_config
        )

        LOGGER.debug(
            f"generate_docusign_preview_url completed for envelope {envelope_id} with status; {envelope_result.status_code}. Preview Url Data: {envelope_result.text}"
        )
        return envelope_result

    def create_envelope(self, payload, log_config: dict = None):
        url = settings.DOCUSIGN_API_ENDPOINT

        resource_path = self.account_id + "/envelopes"
        envelope_url = url + resource_path
        LOGGER.info("Creating envelope for given payload")
        docusign_handler = ApiHandler(envelope_url, self.api_key)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(payload), log_config=log_config
        )

        LOGGER.debug(
            f"create_envelope completed with status; {envelope_result.status_code}. Envelope Creation Data: {envelope_result.text}"
        )
        return envelope_result

    def download_docusign_document(self, params: dict, log_config: dict = None):
        LOGGER.info("Docusign Document Download")
        envelopeId = params["envelope_id"]
        # Value can be combined, archive
        document_download_option = params["doc_download_option"]

        account_id = settings.DOCUSIGN_API_ACCOUNT_ID
        headers = None
        if document_download_option == "archive":
            resource_path = f"{account_id}/envelopes/{envelopeId}/documents/archive"
            headers = {}
            headers["Accept"] = "application/zip, application/octet-stream"
        elif document_download_option == "combined":
            resource_path = f"{account_id}/envelopes/{envelopeId}/documents/combined"

        url = settings.DOCUSIGN_API_ENDPOINT
        doc_url = url + resource_path

        docusign_handler = ApiHandler(doc_url, self.api_key)
        doc_download_result = docusign_handler.send_request(
            method="GET", log_config=log_config
        )
        LOGGER.info(
            f"download_docusign_document completed with status: {doc_download_result.status_code} for envelope id: {envelopeId}"
        )
        return doc_download_result

    def process_docusign_notification(self, xml_string: str):
        return process_docusign_webhook(xml_string)
