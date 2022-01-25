"""Template functions for CIDC email bodies."""
import html
import base64
from functools import wraps

from cidc_schemas.prism import generate_analysis_configs_from_upload_patch

from . import gcloud_client
from ..config.settings import ENV, GOOGLE_ACL_DATA_BUCKET, GOOGLE_DATA_BUCKET

CIDC_MAILING_LIST = "cidc@jimmy.harvard.edu"


def sendable(email_template):
    """
    Adds the `send` kwarg to an email template. If send_email=True, 
    send the email on function call.
    """

    @wraps(email_template)
    def wrapped(*args, send_email=False, **kwargs):
        email = email_template(*args, **kwargs)
        if send_email:
            gcloud_client.send_email(**email)
        return email

    return wrapped


@sendable
def confirm_account_approval(user) -> dict:
    """Send a message to the user confirming that they are approved to use the CIDC."""

    subject = "CIDC Account Approval"

    html_content = f"""
    <p>Hello {user.first_n},</p>
    <p>
        Your CIMAC-CIDC Portal account has been approved! 
        To begin browsing and downloading data, visit https://portal.cimac-network.org.
    </p>
    <p>
        <strong>Note:</strong> If you haven't already, please email cidc@jimmy.harvard.edu to request permission to view data for the trials and assays relevant to your work.</p>
    <p>Thanks,<br/>The CIDC Project Team</p>
    """

    email = {
        "to_emails": [user.email],
        "subject": subject,
        "html_content": html_content,
    }

    return email


@sendable
def new_user_registration(email: str) -> dict:
    """Alert the CIDC admin mailing list to a new user registration."""

    subject = "New User Registration"

    html_content = (
        f"A new user, {email}, has registered for the CIMAC-CIDC Data Portal ({ENV}). If you are a CIDC Admin, "
        "please visit the accounts management tab in the Portal to review their request."
    )

    email = {
        "to_emails": [CIDC_MAILING_LIST],
        "subject": subject,
        "html_content": html_content,
    }

    return email


@sendable
def new_upload_alert(upload, full_metadata) -> dict:
    """Alert the CIDC administrators that an upload succeeded."""
    pipeline_configs = generate_analysis_configs_from_upload_patch(
        full_metadata,
        upload.metadata_patch,
        upload.upload_type,
        GOOGLE_DATA_BUCKET if ENV == "prod" else GOOGLE_ACL_DATA_BUCKET,
    )

    subject = (
        f"[UPLOAD SUCCESS]({ENV}) {upload.upload_type} uploaded to {upload.trial_id}"
    )

    html_content = f"""
    <ul>
        <li><strong>upload job id:</strong> {upload.id}</li>
        <li><strong>trial id:</strong> {upload.trial_id}</li>
        <li><strong>type:</strong> {upload.upload_type}</li>
        <li><strong>uploader:</strong> {upload.uploader_email}</li>
    </ul>
    """

    email = {
        "to_emails": [CIDC_MAILING_LIST],
        "subject": subject,
        "html_content": html_content,
    }

    if pipeline_configs:
        email["attachments"] = [
            {
                # converting to base64 email attachment format (en/decode due to b64 expecting bytes)
                "content": base64.b64encode(conf.encode()).decode(),
                "type": "application/yaml",
                "filename": conf_name,
            }
            for conf_name, conf in pipeline_configs.items()
        ]

    return email


@sendable
def intake_metadata(
    user, trial_id: str, assay_type: str, description: str, xlsx_gcp_url: str
) -> dict:
    """
    Send an email containing a metadata xlsx file and description of that file to the
    CIDC Admin mailing list.
    """
    subject = (
        f"[METADATA SUBMISSION]({ENV}) {user.email} submitted {trial_id}/{assay_type}"
    )
    html_content = f"""
    <p><strong>user:</strong> {user.first_n} {user.last_n} ({user.email})</p>
    <p><strong>contact email:</strong> {user.contact_email}</p>
    <p><strong>protocol identifier:</strong> {html.escape(trial_id)}</p>
    <p><strong>assay type:</strong> {html.escape(assay_type)}</p>
    <p><strong>metadata file:</strong> <a href={xlsx_gcp_url}>{xlsx_gcp_url}</a></p>
    <p><strong>description:</strong> {html.escape(description)}</p>
    """

    email = {
        "to_emails": [CIDC_MAILING_LIST],
        "subject": subject,
        "html_content": html_content,
    }

    return email
