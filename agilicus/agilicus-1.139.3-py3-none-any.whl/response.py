def validate(resp, _continue_on_error=False):
    # 409 is a special case -- it means that the entry existed.
    # Our API handles that nicely.
    if resp.status_code == 409:
        return

    if resp.status_code >= 400:
        if _continue_on_error:
            print(f"Error {resp.status_code}")
            print(resp.text)
        else:
            raise Exception(
                f"Error: Status code {resp.status_code} Response: {resp.text}"
            )
