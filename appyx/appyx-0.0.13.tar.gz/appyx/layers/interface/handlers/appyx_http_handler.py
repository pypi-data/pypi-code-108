from typing import Dict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from appyx import Result
from appyx.layers.interface.exceptions.parameters_required import ParametersRequiredException
from appyx.layers.interface.handler_parameters import HandlerParameters
from appyx.layers.interface.presenters.standard_response_content import StandardResponseContentPresenter


class AppyxHttpHandler(APIView):
    """
    Models a HTTP request handler for an application made by Eryx.
    Defines abstract methods on how to handle it.

    Assumes that a interaction will be responsible for performing the logic of the request.
    Handles a basic parameter check prior to delegating the proper handling of parameters to the interaction.
    """

    # class attributes is the way django allows us to pass parameters to view instances through `as_view()` and
    # receive them as kwargs on the __init__
    authenticators = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._authenticators = kwargs.get("authenticators", [])
        self._parameters = HandlerParameters(initial_parameters=self._initial_parameters(),
                                             initial_required_parameter_names=self._initial_required_parameter_names())

    # --- handling ---

    def handle_get(self, request, **kwargs):
        interaction = self._get_interaction_for_GET(request, kwargs)
        result = interaction.execute()
        return self._response_for(result)

    def handle_post(self, request, **kwargs):
        try:
            self._check_for_required_parameters_in(request)
            interaction = self._get_interaction_for_POST(request, kwargs)
            result = interaction.execute()
            response = self._response_for(result)
            self._notify_post_request(request, interaction, result)
            return response
        except ParametersRequiredException as exception:
            error_from_exception = self._error_factory().request_error(error_text=str(exception))
            result = self._result_with_error(error_from_exception)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=self._trimmed_result(result))

    # --- authentication ---

    def get_authenticators(self):
        return self._authenticators

    # --- self description ---

    def description(self):
        return "Description not implemented. Override method `description()` in your handler class"

    def parameters(self):
        """
        :return: the parameter list
        """
        return self._parameters.parameters()

    def required_parameter_names(self):
        return self._parameters.required_parameter_names()

    # --- private methods ---

    def _error_factory(self):
        raise NotImplementedError('Subclass responsibility')

    def _get_interaction_for_GET(self, request, kwargs):
        raise NotImplementedError('Subclass responsibility')

    def _check_for_required_parameters_in(self, request):
        parameters = self._parameters_from(request)
        missing_parameters = []
        for required_parameter in self._parameters.required_parameter_names():
            if required_parameter not in parameters.keys():
                missing_parameters.append(required_parameter)

        if missing_parameters:
            raise ParametersRequiredException('%s parameters are required.' % missing_parameters)

    def _initial_required_parameter_names(self):
        return set()

    def _initial_parameters(self):
        return []

    def _parameters_from(self, request):
        return request.data or {}

    def _status_http_code_for(self, result):
        if result.is_successful():
            return self._status_code_for_successful_result(result)
        else:
            return self._status_code_for_unsuccessful_result(result)

    def _get_interaction_for_POST(self, request, kwargs):
        raise NotImplementedError('Subclass responsibility')

    def _status_code_for_unsuccessful_result(self, result):
        raise NotImplementedError('Subclass responsibility')

    def _status_code_for_successful_result(self, result):
        raise NotImplementedError('Subclass responsibility')

    def _response_for(self, result):
        status_http_code = self._status_http_code_for(result)
        data = self._response_content_for(result)
        return Response(status=status_http_code, data=data)

    def _trimmed_errors(self, result):
        trimmed_errors = []
        errors = result.errors()
        error_renderer = self._error_renderer()
        for error in errors:
            trimmed_error = error_renderer.render(error)
            trimmed_errors.append(trimmed_error)

        return trimmed_errors

    def _trimmed_result(self, result):
        shallow_object = self._trimmed_object(result)
        shallow_errors = self._trimmed_errors(result)
        return StandardResponseContentPresenter(an_object=shallow_object, errors=shallow_errors).present()

    def _trimmed_object(self, result):
        raise NotImplementedError('Subclass responsibility')

    def _error_renderer(self):
        raise NotImplementedError('Subclass responsibility')

    def _response_content_for(self, result):
        response_content = self._default_response_content()
        self._add_result_response_content(result, response_content)
        self._add_extra_response_content(response_content)
        return response_content

    def _default_response_content(self):
        return {}

    def _add_result_response_content(self, result, response_content):
        data = self._trimmed_result(result)
        response_content.update(data)
        return response_content

    def _add_extra_response_content(self, response_content):
        data = self._extra_data()
        response_content.update(data)
        return response_content

    def _notify_post_request(self, request, interaction, result):
        """
        Override this method if you want this handler to notify its execution to an announcer
        """
        pass

    def _extra_data(self) -> Dict[object, object]:
        """
            Override this method if you want to add additional data to the response.
             examples: App notifications, session status, the API version, endpoint deprecation warnings.
        """
        return {}

    def _result_with_error(self, error):
        result = Result()
        result.add_error(error)
        return result
