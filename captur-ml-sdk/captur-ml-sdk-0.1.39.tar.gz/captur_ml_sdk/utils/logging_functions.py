import json
import os
from google.cloud import pubsub_v1


def publish_debug_logs(message, publisher, environment_suffix):
    payload = {
        "webhook_event": "DebugLogsGenerated",
        "content": message
    }

    data = json.dumps(payload).encode("utf-8")

    topic_path = publisher.topic_path(
        "capturpwa", f"ml-webhooks{environment_suffix or ''}"
    )

    # publish byte string predictions filepath to the chosen topic
    publisher.publish(
        topic_path, data
    )


def record_errors(payload):
    publisher = pubsub_v1.PublisherClient()
    environment_suffix = os.environ.get("ENVIRONMENT_SUFFIX", "-development")

    topic_path = publisher.topic_path(
        "capturpwa", f"ml-webhooks{environment_suffix or ''}")

    # construct message
    message = {
        "webhook_event": "ErrorLogsGenerated",
        "content": payload
    }

    data = json.dumps(message).encode("utf-8")

    publisher.publish(
        topic_path, data
    )
