from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        customized_response = {'status': False, 'errors': []}
        if isinstance(response.data, list):
            for error in response.data:
                customized_response['errors'].append(error)
        elif isinstance(response.data, dict):
            for key, value in response.data.items():
                error = {key: value}
                customized_response['errors'].append(error)

        response.data = customized_response

    return response
