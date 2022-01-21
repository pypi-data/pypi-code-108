def is_valid_oauth_credentials(client_id: str, client_secret: str):
    # sanity check for user convenience (even if it is obvious that those parameters cannot be empty)
    error = False
    if client_id is None or client_secret is None:
        error = True
    if len(client_id) == 0 or len(client_secret) == 0:
        error = True
    return error
