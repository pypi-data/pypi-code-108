environments = {
    "production": {
        "abbrev": "prod",
        "color": "red",
        "network": {
            "name": "indico-production",
            "us-central1-f": "production-central1",
            "us-east4-c": "production-east4",
        },
    },
    "development": {
        "abbrev": "dev",
        "color": "green",
        "network": {
            "name": "indico-development",
            "us-central1-f": "development-central1",
            "us-east4-c": "development-default",
        },
    },
}
environments.update(
    {
        "staging": {
            "abbrev": "stage",
            "color": "blue",
            "network": environments["production"]["network"],
        },
        "feature": {
            "abbrev": "feat",
            "color": "yellow",
            "network": environments["development"]["network"],
        },
    }
)
