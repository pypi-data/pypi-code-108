def set_credentials(tecton_api_key: str) -> None:
    """
    Explicitly override tecton credentials settings.

    Typically, Tecton credentials are set in environment variables, but if your
    Tecton SDK setup requires another type of setup, you can use this function
    to set the Tecton API Key secret during an interactive Python session.

    :param tecton_api_key: Tecton API Key
    """
    # Import this lazily so we don't trigger initialization that happens on importing conf module.
    from tecton import conf

    conf.set("TECTON_API_KEY", tecton_api_key)
