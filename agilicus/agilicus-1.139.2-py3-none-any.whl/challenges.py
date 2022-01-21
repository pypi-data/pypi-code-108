import agilicus

from . import context
from .input_helpers import strip_none
from .output.table import (
    format_table,
    metadata_column,
    spec_column,
    status_column,
)


def create_challenge(ctx, user_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    challenge_endpoints = [
        agilicus.ChallengeEndpoint(*endpoint)
        for endpoint in kwargs.pop("challenge_endpoint", [])
    ]
    spec = agilicus.ChallengeSpec(
        user_id=user_id, challenge_endpoints=challenge_endpoints, **kwargs
    )
    challenge = agilicus.Challenge(spec=spec)
    resp = apiclient.challenges_api.create_challenge(challenge)
    return resp


def replace_challenge(ctx, challenge_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    existing = apiclient.challenges_api.get_challenge(challenge_id)

    spec_as_dict = existing.spec.to_dict()
    spec_as_dict.update(kwargs)
    spec = agilicus.ChallengeSpec(**spec_as_dict)
    existing.spec = spec

    resp = apiclient.challenges_api.replace_challenge(challenge_id, existing)
    return resp


def get_challenge(ctx, challenge_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    kwargs = strip_none(kwargs)
    resp = apiclient.challenges_api.get_challenge(challenge_id)
    return resp


def delete_challenge(ctx, challenge_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    resp = apiclient.challenges_api.delete_challenge(challenge_id)
    return resp


def get_challenge_answer(
    ctx, challenge_id, challenge_answer, challenge_uid, allowed, challenge_type, **kwargs
):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    resp = apiclient.challenges_api.get_answer(
        challenge_id, challenge_answer, challenge_uid, allowed, challenge_type
    )
    return resp


def create_challenge_enrollment(ctx, user_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    spec = agilicus.TOTPEnrollmentSpec(user_id=user_id, **kwargs)
    model = agilicus.TOTPEnrollment(spec=spec)

    resp = apiclient.challenges_api.create_totp_enrollment(model)
    return resp


def update_challenge_enrollment(ctx, enrollment_id, user_id, answer, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    model = agilicus.TOTPEnrollmentAnswer(user_id=user_id, answer=answer)
    resp = apiclient.challenges_api.update_totp_enrollment(enrollment_id, model)
    return resp


def get_challenge_enrollment(ctx, enrollment_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs = strip_none(kwargs)
    resp = apiclient.challenges_api.get_totp_enrollment(enrollment_id, **kwargs)
    return resp


def delete_challenge_enrollment(ctx, enrollment_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    resp = apiclient.challenges_api.delete_totp_enrollment(enrollment_id, **kwargs)
    return resp


def list_totp_enrollments(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs = strip_none(kwargs)
    results = apiclient.challenges_api.list_totp_enrollment(**kwargs)
    return results.totp


def format_totp_enrollments(ctx, details):
    columns = [
        metadata_column("id", "ID"),
        metadata_column("created", "Created"),
        metadata_column("updated", "Updated"),
        spec_column("user_id", "User ID"),
        status_column("state", "State"),
    ]
    return format_table(ctx, details, columns)


def list_webauthn_enrollments(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs = strip_none(kwargs)
    results = apiclient.challenges_api.list_webauthn_enrollments(**kwargs)
    return results.webauthn


def format_webauthn_enrollments(ctx, details):
    columns = [
        metadata_column("id", "ID"),
        metadata_column("created", "Created"),
        metadata_column("updated", "Updated"),
        spec_column("user_id", "User ID"),
        spec_column("relying_party_id", "Relying Party ID"),
        spec_column("attestation_format", "Attestation Format"),
        spec_column("attestation_conveyance", "Attestation Conveyance"),
        spec_column("user_verification", "User Verification"),
        status_column("transports", "Transports"),
    ]
    return format_table(ctx, details, columns)
