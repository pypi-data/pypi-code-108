# -*- coding: utf-8 -*-
import inspect
from typing import Callable, TypeVar

import yaml

from _pistar.utilities.constants import ACTION_WORD_KEYS as KEYS
from _pistar.utilities.constants import ACTION_WORD_STATUS as STATUS
from _pistar.utilities.exceptions import DeprecatedActionWordException
from _pistar.utilities.exceptions import DisabledActionWordException
from _pistar.utilities.exceptions import DocumentError
from _pistar.utilities.exceptions import MissingArgumentSchemaException
from _pistar.utilities.exceptions import MissingFieldInActionWordException
from _pistar.utilities.exceptions import MissingReturnSchemaException
from _pistar.utilities.exceptions import UnknownStatusException
from _pistar.utilities.match_schema import instantiate_assertion
from _pistar.utilities.match_schema import match_schema

ActionWordFunction = TypeVar("ActionWordFunction", bound=Callable[..., object])


class ActionWordChecker:
    """
    description: this class is used to check the action word.
    """

    def __init__(self, aw: ActionWordFunction):
        """
        description: this is the constructor of the class ActionWordChecker.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
            action_word:
                type: function
                description: the action word
        return: None
        """
        doc = inspect.getdoc(aw)
        if doc is None:
            msg = f"action word {aw.__name__} has no document"
            raise DocumentError(msg)
        # catch errors from yaml parse.
        try:
            self.__doc = yaml.load(doc, Loader=yaml.SafeLoader)
        except BaseException as e:
            msg = f"action word document has yaml syntax error.see details:\n{str(e)}"
            raise DocumentError(msg) from e

        self.__aw = aw

        spec = inspect.getfullargspec(aw)
        self.__args = spec.args.copy()
        if spec.varargs:
            self.__args.append(spec.varargs)
        if spec.varkw:
            self.__args.append(spec.varkw)
        if spec.kwonlyargs:
            self.__args += spec.kwonlyargs

    def check_fields(self):
        """
        description: this function is used to check the field of action word
                     docstring.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
        return:
            type:
                - MissingFieldInActionWordException
                - None
            description: if there is no missing field, return None,
                         else return MissingFieldInActionWordException.
        """

        required_fields = [
            KEYS.DESCRIPTION,
            KEYS.ARGUMENTS,
            KEYS.RETURN,
            KEYS.AUTHOR,
            KEYS.MODIFY_RECORDS,
            KEYS.STATUS
        ]

        for field_name in required_fields:
            if field_name in self.__doc:
                continue
            return MissingFieldInActionWordException(field_name=field_name, action_word_name=self.__aw.__name__)
        return None

    def check_status(self):
        """
        description: this function is used to check the status of action word.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
        return:
            type:
                - DisabledActionWordException
                - DeprecatedActionWordException
                - UnknownStatusException
                - None
            description: |
                if there is no missing field, return None,
                else return DisabledActionWordException,
                DeprecatedActionWordException, or UnknownStatusException.
        """

        status = self.__doc[KEYS.STATUS]

        if status == STATUS.DISABLE:
            return DisabledActionWordException(action_word_name=self.__aw.__name__)

        if status == STATUS.DEPRECATED:
            return DeprecatedActionWordException(action_word_name=self.__aw.__name__)

        if status == STATUS.ENABLE:
            return None

        return UnknownStatusException(status=status, action_word_name=self.__aw.__name__)

    def check_argument_schemata(self):
        """
        description: this function is used to
                     check the argument schemata of action word.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
        return:
            type:
                - MissingArgumentSchemaException
                - None
            description: |
                if there is no missing schema, return None,
                else return MissingArgumentSchemaException.
        """

        for argument_name in self.__args:
            if isinstance(self.__doc[KEYS.ARGUMENTS], dict) and argument_name in self.__doc[KEYS.ARGUMENTS]:
                continue

            return MissingArgumentSchemaException(argument_name=argument_name, action_word_name=self.__aw.__name__)
        return None

    def check_return_schema(self):
        """
        description: this function is used to
                     check the return schema of action word.
        argument:
            self:
                type: ActionWordChecker
                description: itself
        return:
            type:
                - MissingReturnSchemaException
                - None
            description: |
                if there is schema of return, return None,
                else return MissingReturnSchemaException.
        """

        if isinstance(self.__doc[KEYS.RETURN], dict):
            return None
        return MissingReturnSchemaException(action_word_name=self.__aw.__name__)

    def check_arguments(self, *args, **kwargs):
        """
        description: this function is used to
                     check the argument value of action word.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
        return:
            type:
                - Exception
                - None
            description: |
                if there is any argument value that does not match its schema,
                 return Exception, elss return None.
        """

        # get the argument dictionary.use Signature.bind().
        try:
            ba = inspect.signature(self.__aw).bind(*args, **kwargs)
            ba.apply_defaults()
            argument_dictionary = ba.arguments
        except BaseException as exception:
            return exception

        # for each argument
        for argument_name, argument_value in argument_dictionary.items():
            exception = match_schema(
                value=argument_value, schema=self.__doc[KEYS.ARGUMENTS][argument_name], name=argument_name
            )
            if exception is not None:
                return self.format_exception(exception)

        return None

    def format_exception(self, exception):
        """
        description: this function is used to format the exception message.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
            exception:
                type: Exception
                description: the exception
        return:
            type:
                - TypeMismatchException
                - AssertionFailureException
                - EnumerationFailureException
                - MissingPropertyException
            description: the formatted exception.
        """

        # add message into the exception.
        module = self.__aw.__module__
        name = self.__aw.__name__

        exception.args = (f"in action word '{module}.{name}':{exception.args[0]}",) + exception.args[1:]

        return exception

    def check_return_value(self, return_value):
        """
        description: this function is used to
                     check whether return value does match the schema.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
            return_value:
                type: any
                description: the return value
        return:
            type:
                - Exception
                - None
            description: if the return value match its schema, return None,
                         else return Exception.
        """

        exception = match_schema(name=KEYS.RETURN, value=return_value, schema=self.__doc[KEYS.RETURN])

        if exception:
            return self.format_exception(exception)
        return None

    def instantiate_assertions(self):
        """
        description: this function is used to
                     instantiate the assertions in action word docstring.
        arguments:
            self:
                type: ActionWordChecker
                description: itself
        return: None
        """

        if self.__doc[KEYS.ARGUMENTS]:
            for argument_name in self.__doc[KEYS.ARGUMENTS]:
                self.__doc[KEYS.ARGUMENTS][argument_name] = instantiate_assertion(
                    self.__doc[KEYS.ARGUMENTS][argument_name]
                )

        self.__doc[KEYS.RETURN] = instantiate_assertion(self.__doc[KEYS.RETURN])
