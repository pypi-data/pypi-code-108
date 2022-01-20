import requests
from datetime import datetime
from logging import getLogger
from typing import Optional
from sumatra.config import CONFIG

logger = getLogger("sumatra.api")


class APIClient:
    def __init__(self, instance: Optional[str] = None):
        if instance:
            CONFIG.instance = instance

    def send(self, event):
        logger.info(f"Sending: {event}")
        if "_type" not in event:
            raise Exception("event payload missing mandatory '_type'")
        post_time = datetime.now()
        response = requests.post(
            f"{CONFIG.api_event_url}?features",
            headers={"x-api-key": CONFIG.api_key},
            json=event,
        )
        response_time = round((datetime.now() - post_time).total_seconds() * 1000)
        logger.info(f"Response Time: {response_time}ms")
        return self._check_response(response)

    def _check_response(self, response):
        resp_json = response.json()
        logger.info(f"Response: {resp_json}")
        if "event_id" not in resp_json:
            raise Exception(f"Response {response.status_code}: {resp_json}")
        if "errors" in resp_json:
            for feature, e in resp_json["errors"].items():
                logger.error(
                    f"{resp_json.get('_type','')} {resp_json['event_id']} feature '{feature}': {e}"
                )
        return resp_json
