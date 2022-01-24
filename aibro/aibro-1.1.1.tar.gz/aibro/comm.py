from aibro.tools.auth import check_authentication
from aibro.tools.service.api_service import AIbroClient


aibro_client = AIbroClient()


class Comm(object):
    @staticmethod
    def send_message(email: str, feedback_message: str, category: str = "random"):
        """[reference]
        https://doc.aipaca.ai/#send_message
        """
        return send_message(email, feedback_message, category)

    @staticmethod
    def available_machines():
        """[reference]
        https://doc.aipaca.ai/#available_machines
        """
        return available_machines()


def send_message(email: str, feedback_message: str, category: str = "random"):
    if category not in set(["random", "feature_request", "bug report"]):
        raise Exception(
            "Message category has to be one of the ['random', 'feature_request', 'bug report']"
        )
    user_id = check_authentication()
    data = {
        "email": email,
        "user_id": user_id,
        "message": feedback_message,
        "category": category,
    }
    aibro_client.post_with_json_data("v1/feedback_email", data)
    print("Thanks for your feedback!")


def available_machines():
    resp = aibro_client.get("v1/marketplace_machines")
    print("Available Resources:")
    for name, spec in resp.json().items():
        limit = spec["CAPACITY"]
        if limit <= 0:
            continue

        GPU_type = spec["GPU"]
        num_vCPU = spec["CPU CORES"]
        pricing = spec["PRICING"]
        availability = spec["AVAILABILITY"]
        print(
            f"{f'Machine Id: {name}' : <26} {f'GPU Type: {GPU_type}' : <18} {f'num_vCPU: {num_vCPU}' : <15} "
            f"{f'cost: {pricing}' : <15} {f'capacity: {limit}' : <10} {f'availability: {availability * 100}%' : <15}"
            # noqa
        )
