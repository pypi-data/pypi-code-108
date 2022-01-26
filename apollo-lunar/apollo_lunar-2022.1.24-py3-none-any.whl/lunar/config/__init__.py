import requests

CONFIG = {
    "LOCAL": {
        "LOCAL": {
            "TEST_URL": "http://127.0.0.1:8080",
            "LUNAR_REC_URL": "http://127.0.0.1:8080",
            "LUNAR_DATA_URL": "http://127.0.0.1:8081",
        },
    },
    "DEV": {
        "LOCAL": {
            "TEST_URL": "https://rec.dev.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.dev.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.dev.apollo-lunar.com",
        },
        "BAP": {
            "TEST_URL": "http://rec.lunar.apollo",
            "LUNAR_REC_URL": "http://rec.lunar.apollo",
            "LUNAR_DATA_URL": "http://data.lunar.apollo",
        },
    },
    "STG": {
        "EDD": {
            "TEST_URL": "http://150.6.13.63:8081",
            "LUNAR_REC_URL": "https://rec.stg.bap.apollo-ai.io",
            "LUNAR_DATA_URL": "https://data.stg.bap.apollo-ai.io",
            "COPY_DATABASE_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_database",
            "COPY_FILES_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_files",
            "JOB_STATUS_URL": "http://150.6.13.9:31771/edd_to_lunar/job_status",
        },
        "LOCAL": {
            "TEST_URL": "https://rec.stg.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.stg.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.stg.apollo-lunar.com",
        },
        "BAP": {
            "TEST_URL": "http://rec.lunar.apollo",
            "LUNAR_REC_URL": "http://rec.lunar.apollo",
            "LUNAR_DATA_URL": "http://data.lunar.apollo",
        },
    },
    "PRD": {
        "EDD": {
            "TEST_URL": "http://150.6.13.63:8081",
            "LUNAR_REC_URL": "https://rec.bap.apollo-ai.io",
            "LUNAR_DATA_URL": "https://data.bap.apollo-ai.io",
            "COPY_DATABASE_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_database",
            "COPY_FILES_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_files",
            "JOB_STATUS_URL": "http://150.6.13.9:31771/edd_to_lunar/job_status",
        },
        "LOCAL": {
            "TEST_URL": "https://rec.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.apollo-lunar.com",
        },
        "BAP": {
            "TEST_URL": "http://rec.lunar.apollo",
            "LUNAR_REC_URL": "http://rec.lunar.apollo",
            "LUNAR_DATA_URL": "http://data.lunar.apollo",
        },
    },
}


class Config:
    def __init__(self, env: str, apikey: str, runtime_env: str = None):
        assert env in CONFIG.keys(), f"`env` must be in {CONFIG.keys()}"

        setattr(self, "ENV", env)
        setattr(self, "APIKEY", apikey)

        if runtime_env:
            setattr(self, "RUNTIME_ENV", runtime_env)
            try:
                for key, url in CONFIG[env][runtime_env].items():
                    setattr(self, key, url)
            except KeyError:
                raise Exception(f"BAP {env} does not support this {runtime_env} environment.")

            return

        if env == "LOCAL":
            setattr(self, "RUNTIME_ENV", "LOCAL")
            for key, url in CONFIG[env]["LOCAL"].items():
                setattr(self, key, url)
            return

        for runtime_env, urls in CONFIG[env].items():
            try:
                requests.get(url=urls["TEST_URL"], timeout=0.5)
                setattr(self, "RUNTIME_ENV", runtime_env)
                for key, url in urls.items():
                    setattr(self, key, url)
                break
            except Exception:
                continue

        if not hasattr(self, "RUNTIME_ENV"):
            raise Exception(f"BAP {env} does not support this runtime environment.")
