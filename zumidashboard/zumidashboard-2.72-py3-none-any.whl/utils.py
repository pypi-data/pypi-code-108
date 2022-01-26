from flask import current_app
import time


def log_info(msg):
    current_app.logger.info(time.strftime('{%Y-%m-%d %H:%M:%S} ') + msg)


def set_backend_language(language):
    print('set backend language ', language)
    korean_key = ["kr", "ko"]
    for item in korean_key:
        if item in language:
            current_app.config['LANGUAGE'] = "ko"
            return
    if "hu" in language:
        current_app.config['LANGUAGE'] = "hu"
    elif "zh" in language:
        current_app.config['LANGUAGE'] = "zh"
    else:
        current_app.config['LANGUAGE'] = "en"
    print(current_app.config['LANGUAGE'])
