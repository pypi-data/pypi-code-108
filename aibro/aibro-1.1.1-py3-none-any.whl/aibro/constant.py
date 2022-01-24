import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")

IS_LOCAL = os.environ.get("IS_LOCAL", "false") == "true"

IS_DEMO = os.environ.get("IS_DEMO", "false") == "true"

# TODO: move this limitation check to aibro server
INPUT_DATA_SIZE_LIMIT_MB = 1024 * 1.5

INF_HOST = os.environ.get("SERVER_HOST", "http://api.aipaca.ai")
