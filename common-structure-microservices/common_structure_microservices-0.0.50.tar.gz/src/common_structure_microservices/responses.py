from common_structure_microservices.messages import Messages


def response(data=[], message=Messages.SUCCESSFUL_MESSAGE, status=True):
    return {
        'status': status,
        'message': message,
        'data': data
    }
