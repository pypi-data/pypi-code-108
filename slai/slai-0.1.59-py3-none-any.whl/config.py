from slai.modules.parameters import from_config


def get_api_base_urls():
    stage = from_config(
        key="STAGE",
        default="production",
    )

    if stage == "local":
        backend_base_url = from_config(
            key="BASE_URL",
            default="http://localhost:8080",
        )
        model_base_url = "models.slai.local"
    elif stage == "development":
        backend_base_url = "https://api.eng-dev.slai.io"
        model_base_url = "https://models.eng-dev.slai.io"
    elif stage == "staging":
        backend_base_url = "https://api.eng-stage.slai.io"
        model_base_url = "https://models.eng-staging.slai.io"
    else:
        backend_base_url = from_config(
            key="BASE_URL",
            default=f"https://api.slai.io",
        )
        model_base_url = "https://models.slai.io"

    return backend_base_url, model_base_url
