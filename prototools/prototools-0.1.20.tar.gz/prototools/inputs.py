import time
from builtins import input
from typing import Any, Callable, Optional, Sequence, Union

from prototools.validators import (
    TimeoutException,
    RetryLimitExecption,
    ValidatorsException,
    TimeoutException,
    _GenericValidate,
    validate_bool,
    validate_str,
    validate_int,
    validate_float,
    validate_choice,
    validate_yes_no,
    validate_date,
    validate_time,
)
try:
    import msvcrt
except ImportError:
    pass


def _(s: str, lang="en") -> str:
    """Translate string to another language."""
    if lang not in ("en", "es"):
        lang = "en"
    spanish = {
        "'prompt' must be a str":
            "'prompt' debe ser de tipo str",
        "'limit' must be an int":
            "'limit' debe ser de tipo int",
        "'validation' must be a function":
            "'validation' debe ser una función",
        "'function' must be a function":
            "'function' debe de ser una función",
        "Select one of: {}\n":
            "Seleccionar uno: {}\n",
        "Select one of the following:\n":
            "Seleccionar uno de los siguientes:\n",
        "yes": "sí",
        "no": "no",
        "True": "Verdadero",
        "False": "Falso",
    }
    if lang == "es":
        return spanish[s]
    else:
        return s


class _GenericInput:
    """Base generic Input.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        default (Any, optional): Default value to use.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
    """

    def __init__(self,
        prompt: Optional[str] = "",
        default: Optional[Any] = None,
        timeout: Optional[int] = None,
        limit: Optional[int] = None,
        function: Optional[Callable] = None,
        validation: Optional[Callable] = None,
        lang: str = "en",
    ) -> None:
        self.prompt = prompt
        self.default = default
        self.timeout = timeout
        self.limit = limit
        self.function = function
        self.validation = validation
        self.lang = lang
        self._validate_parameters()

    def _input(self) -> Any:
        """Used by the various inputs funcionts."""
        start = time.time()
        tries = 0

        while True:
            print(self.prompt, end="")
            user_input = input()
            tries += 1
            if self.function is not None:
                user_input = self.function(user_input)
            try:
                postvalidation_user_input = self.validation(user_input)
                if postvalidation_user_input is not None:
                    user_input = postvalidation_user_input
            except Exception as e:
                timeretrylimit_exc = self._validate_timeout_retrylimit(
                    start=start, 
                    timeout=self.timeout, 
                    tries=tries, 
                    limit=self.limit,
                )
                print(e)
                if isinstance(timeretrylimit_exc, Exception):
                    if self.default is not None:
                        return self.default
                    else:
                        raise timeretrylimit_exc
                else:
                    continue
            if (self.timeout is not None and 
                start + self.timeout < time.time()):
                if self.default is not None:
                    return self.default
                else:
                    raise TimeoutException()
            else:
                return user_input

    def _validate_parameters(self) -> None:
        """Check parameters."""
        if not isinstance(self.prompt, str):
            raise ValidatorsException(_("'prompt' must be a str", self.lang))
        if not isinstance(self.timeout, (int, float, type(None))):
            raise ValidatorsException(
                "'timeout' must be an int or float"
            )
        if not isinstance(self.limit, (int, type(None))):
            raise ValidatorsException(_("'limit' must be an int", self.lang))
        if not callable(self.validation):
            raise ValidatorsException(
                _("'validation' must be a function", self.lang)
            )
        if not (callable(self.function) or self.function is None):
            raise ValidatorsException(
                _("'function' must be a function", self.lang)
            )

    @staticmethod
    def _validate_timeout_retrylimit(
        start: int,
        timeout: int,
        tries: int,
        limit: int,
    ) -> Union[None, TimeoutException, RetryLimitExecption]:
        """Return exceptions instead of raising them so the caller can
        display the original validation exception message.

        Args:
            start (int): Unix epoch time when was first called.
            timeout (int): Time in seconds to enter an input.
            tries (int): Number of time the user has already tried.
            limit (int); Number of tries to enter a valid input.

        Returns:
            Exception/None: TimeoutException or RetryLimitException if
                the user has exceeded those limits, otherwise returns
                None.
        """
        if timeout is not None and start + timeout < time.time():
            return TimeoutException()
        if limit is not None and tries >= limit:
            return RetryLimitExecption()


def str_input(
    prompt: Optional[str] = "",
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter any string.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not an str.

    Returns:
        str: The string.

    >>> s = str_input("Enter a string: ")
    Enter a string: prototools
    >>> s
    'prototools'
    """
    validator = _GenericValidate(blank=blank, strip=strip, lang=lang)
    validator._validate_parameters()
    validation = lambda value: validate_str(value)
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def int_input(
    prompt: Optional[str] = "",
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    min: Union[int, float, None] = None,
    max: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    gt: Union[int, float, None] = None,
    lang: str = "en",
) -> int:
    """Prompt the user to enter an integer number.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not an int.

    Returns:
        int: The number as an int.

    >>> from prototools.inputs import int_input
    >>> number = int_input()
    6.0
    >>> number
    6
    >>> type(number)
    <class 'int'>
    """
    validator = _GenericValidate(blank=blank, strip=strip, lang=lang)
    validator._validate_numbers_parameters()
    validation = lambda value: validate_int(
        value, min=min, max=max, lt=lt, gt=gt, lang=lang
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def float_input(
    prompt: Optional[str] = "",
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    min: Union[int, float, None] = None,
    max: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    gt: Union[int, float, None] = None,
    lang: str = "en",
) -> int:
    """Prompt the user to enter a floating point number.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a float.

    Returns:
        int: The number as a float.
    
    >>> from prototools.inputs import float_input
    >>> number = float_input()
    6
    >>> number
    6.0
    >>> type(number)
    <class 'float'>
    """
    validator = _GenericValidate(blank=blank, strip=strip, lang=lang)
    validator._validate_numbers_parameters()
    validation = lambda value: validate_float(
        value, min=min, max=max, lt=lt, gt=gt, lang=lang
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def choice_input(
    choices: Sequence[str],
    sensitive: Optional[bool] = False,
    prompt: Optional[str] = "_default",
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> Any:
    """Prompt the user to enter one of the provieded choices.

    Args:
        choices (Sequence[str]): Sequence of strings, one of which the
            user must enter.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        prompt (str, optional): Prompts the user to enter input.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not one of the values in choices.

    Returns:
        str: The selected choice as a string.

    >>> options = ("a", "b", "c")
    >>> s = choice_input(options)
    Select one of: a, b, c
    1
    1 is not a valid choice
    Select one of: a, b, c
    a
    >>> s
    'a'
    """
    validator = _GenericValidate(
        choices=choices,
        sensitive=sensitive,
        letters=False,
        numbers=False,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    validator._validate_choices_parameters()
    validation = lambda value: validate_choice(
        value,
        choices=choices,
        sensitive=False,
        letters=False,
        numbers=False,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    if prompt == "_default":
        prompt = _("Select one of: {}\n", lang).format(", ".join(choices))
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def menu_input(
    choices: Sequence[str],
    numbers: Optional[bool] = False,
    letters: Optional[bool] = False,
    sensitive: Optional[bool] = False,
    prompt: Optional[str] = "_default",
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter one of the provieded choices. Also
    displays a small menu with bulleted, numbered, or lettered options.

    Args:
        choices (Sequence[str]): Sequence of strings, one of which the
            user must enter.
        numbers (bool, optional): If True, it will also accept a number
            as a choice.
        letters (bool, optional): If True, it will also accept a letter
            as a choice.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        prompt (str, optional): Prompts the user to enter input.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not one of the values in choices.

    Returns:
        str: The selected choice as a string.

    >>> options = ("a", "b", "c")
    >>> s = menu_input(options)
    Select one of the following:
    * a
    * b
    * c
    1
    1 is not a valid choice
    Select one of the following:
    * a
    * b
    * c
    a
    >>> s
    'a'
    """
    validator = _GenericValidate(
        choices=choices,
        sensitive=sensitive,
        letters=numbers,
        numbers=letters,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    validator._validate_choices_parameters()
    validation = lambda value: validate_choice(
        value,
        choices=choices,
        sensitive=sensitive,
        letters=letters,
        numbers=numbers,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    if prompt == "_default":
        prompt = _("Select one of the following:\n", lang)
    if numbers:
        prompt += "\n".join(
            [str(i + 1)+". "+ choices[i] for i in range(len(choices))]
        )
    elif letters:
        prompt += "\n".join(
            [chr(65 + i)+". "+ choices[i] for i in range(len(choices))]
        )
    else:
        prompt += "\n".join(["* "+ choice for choice in choices])
    prompt += "\n"
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def yes_no_input(
    prompt: Optional[str] = "",
    yes_value: Optional[str] = None,
    no_value: Optional[str] = None,
    sensitive: Optional[bool] = False,
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter a yes/no response.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        yes_value (bool, optional): Value of affirmative response.
            Defaults 'yes'.
        no_value (bool, optional): Value of negative response. Defaults
            'no'.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not a yes or no response.

    Returns:
        str: The yes_val or no_val argument, not value.
    
    >>> s = yes_no_input("Do you like this?")
    Do you like this? Yeah
    Yeah is not a valid yes/no response
    Do you like Python? yes
    >>> s
    'yes'
    """
    if yes_value is None:
        yes_value = _("yes", lang)
    if no_value is None:
        no_value = _("no", lang)
    validation = lambda value: validate_yes_no(
        value=value,
        blank=blank,
        strip=strip,
        yes_value=yes_value,
        no_value=no_value,
        sensitive=sensitive,
        lang=lang,
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    result = generic._input()
    result = validate_yes_no(
        result,
        blank=blank,
        strip=strip,
        yes_value=yes_value,
        no_value=no_value,
        sensitive=sensitive,
        lang=lang,
    )
    return result


def bool_input(
    prompt: Optional[str] = "",
    true_value: Optional[str] = None,
    false_value: Optional[str] = None,
    sensitive: Optional[bool] = False,
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> bool:
    """Prompts the user to enter a True/False response.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        true_value (bool, optional): Value of affirmative response.
            Defaults 'yes'.
        no_value (bool, optional): Value of negative response. Defaults
            'no'.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.
    
    Returns:
        bool: Boolean value.
    
    >>> s = bool_input()
    yes
    yes is not a valid yes/no response
    t
    >>> s
    True
    """
    if true_value is None:
        true_value = _("True", lang)
    if false_value is None:
        false_value = _("False", lang)
    validation = lambda value: validate_yes_no(
        value=value,
        blank=blank,
        strip=strip,
        yes_value=true_value,
        no_value=false_value,
        sensitive=sensitive,
        lang=lang,
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    result = generic._input()
    result = validate_bool(
        result,
        blank=blank,
        strip=strip,
        true_value=true_value,
        false_value=false_value,
        sensitive=sensitive,
        lang=lang,
    )
    return result


def date_input(
    prompt: Optional[str] = "",
    formats: Optional[Union[str, Sequence[str]]] = None,
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter a date.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        formats (Union[str, Sequence[str]], optional): Date formats.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.
    
    Returns:
        str: The date.
    
    >>> s = date_input()
    12-12-2021
    12-12-2021 is not a valid date
    12/12/2021
    >>> s
    2021/12/12
    >>> type(s)
    <class 'datetime.date'>
    """
    if formats is None:
        formats = ("%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d", "%y/%m/%d", "%x")
    validation = lambda value: validate_date(
        value=value,
        formats=formats,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def date_input_dmy(
    prompt: Optional[str] = "",
    formats: Optional[Union[str, Sequence[str]]] = None,
    to_str: Optional[bool] = True,
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter a date.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        formats (Union[str, Sequence[str]], optional): Date formats.
        to_str (bool, optional): If True, the date is returned as a
            string.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.
    
    Returns:
        str: The date.
    
    >>> s = date_input()
    12-12-2021
    12-12-2021 is not a valid date
    12/12/2021
    >>> s
    2021/12/12
    >>> type(s)
    <class 'datetime.date'>
    """
    if formats is None:
        formats = ("%d/%m/%Y", "%x") 
    date = date_input(
        prompt=prompt,
        formats=formats,
        default=default,
        blank=blank,
        strip=strip,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    if to_str:
        return date.strftime("%d/%m/%Y")
    return date


def time_input(
    prompt: Optional[str] = "",
    formats: Optional[Union[str, Sequence[str]]] = ("%H:%M:%S", "%H:%M", "%X"),
    default: Optional[Any] = None,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    timeout: Optional[int] = None,
    limit: Optional[int] = None,
    function: Optional[Callable] = None,
    validation: Optional[Callable] = None,
    lang: str = "en",
) -> str:
    """Prompt the user to enter a time.

    Args:
        prompt (str, optional): Prompts the user to enter input.
        formats (Union[str, Sequence[str]], optional): Time formats.
        default (Any, optional): Default value to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        timeout (int, optional): Time in seconds to enter an input.
        limit (int, optional): Number of tries to enter a valid input.
        function (Callable, optional): Optional function that is passed
            the user's input and returns the new value as the input.
        validation (Callable, optional): Validator.
        lang (str): Establish the language.

    Returns:
        str: The time.

    >>> s = time_input()
    1200
    1200 is not a valid time
    12:00
    >>> s
    12:00:00
    >>> type(s)
    <class 'datetime.time'>
    """
    validation = lambda value: validate_time(
        value=value,
        formats=formats,
        blank=blank,
        strip=strip,
        lang=lang,
    )
    generic = _GenericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        function=function,
        validation=validation,
        lang=lang,
    )
    return generic._input()


def month_input():
    return NotImplementedError()


def day_input():
    return NotImplementedError()


def password_input():
    """Prompts the user to enter a password. Mask characters will be
    displayed instead of the actual characters.
    """
    return NotImplementedError()


def custom_input(prefix: str = "", suffix: str = "") -> str:
    """Custom input with a prefix string and a suffix string. User's
    input is located in between prefix and suffix.

    Args:
        prefix (str): Prefix word before user input.
        suffix (str): Suffix word after user input.
    
    Returns:
        str: User input.
    
    >>> s = custom_input("Age: ", " years old.")
    Age: __ years old.
    Age: 18 years old.
    >>> s
    18
    """
    from prototools.keyboard import Keyboard

    user_input = ""
    print(prefix + " "+ suffix, end='\r', flush=True)
    print(prefix, end="", flush=True)
    while True:
        k = msvcrt.getch()
        L = len(user_input)
        if k in Keyboard.bBACKSPACE:
            user_input = user_input[:-1]
        elif k in Keyboard.bENTER:
            break
        else:
            try:
                word = str(k.decode("utf-8"))
            except:
                continue
            user_input += str(word)
        
        print('\r' + " "*(len(prefix)+L+len(suffix)+1), end='\r', flush=True)
        print('\r' + prefix + user_input +" "+ suffix, end='\r', flush=True)
        print(prefix + user_input, end="", flush=True)
    print()
    return user_input