import collections.abc
import datetime
import time
from typing import Any, Optional, Sequence, Tuple, Union

from prototools.utils import strip_string

SEQUENCE_ABC = collections.abc.Sequence
MAX_ERROR = 50


def _(s: str, lang="en") -> str:
    """Translate string to another language."""
    if lang not in ("en", "es"):
        lang = "en"
    spanish = {
        "Blank values are not allowed":
            "No se permiten valores en blanco",
        "'blank' argument must be a bool":
            "El argumento 'blank' debe ser de tipo bool",
        "'strip' argument must be a bool, str or None":
            "El argumento 'strip' debe ser de tipo bool, str or None",
        "Only one argument for 'min' or 'gt' can be passed, not both":
            "Solo un argumento para 'min' o 'gt'puede ser pasado, no ambos",
        "Only one argument for 'max' or 'lt' can be passed, not both":
            "Solo un argumento para 'max' o 'lt' puede ser pasado, no ambos",
        "The 'min' argument must be less than or equal to 'max' argument":
            "El argumento 'min' debe ser menor o igual que el argumento 'max'",
        "The 'min' argument must be less than 'lt' argument":
            "El argumento 'min' debe ser menor que el argumento 'lt'",
        "The 'max' argument must be greater than 'gt' argument":
            "El argumento 'max' debe ser mayor que el argumento 'gt'",
        "'{}' argument must be int, float, or None":
            "El argumento '{}' debe ser int, float o None",
        "'sensitive' argument must be a bool":
            "El argumento 'sensitive' debe ser de tipo bool",
        "'choices' argument must be a sequence":
            "El argumento 'choices' debe ser una secuencia",
        "'choices' must have at least two items if 'blank' is False":
            "'choices' debe tener al menos dos elementos si 'blank' es False",
        "'choices' must have at least one item":
            "'choices' debe tener al menos un elemento",
        "'letters' cannot be True if there are more than 26 choices":
            "'letters' no puede ser True si hay mas de 26 opciones",
        "'numbers' and 'letters' cannot both be True":
            "'numbers' y 'letters' no pueden ser ambos True",
        "Duplicates entries in 'choices'":
            "Elementos duplicados en 'choices'",
        "Duplicate case-sensitive entries in 'choices'":
            "Elementos case-sensitive duplicados en 'choices'",
        "yes_val argument must be a non-empty string":
            "El argumento 'yes_val' debe de ser una cadena de texto no vacía",
        "no_val argument must be a non-empty string":
            "El argumento 'no_val' debe de ser una cadena de texto no vacía",
        "yes_val and no_val arguments must be different":
            "Los argumentos 'yes_val' y 'no_val' deben de ser diferentes",
        "First character of yes_val and no_val arguments must be different":
            "El primer carácter de los argumentos 'yes_val' y 'no_val'"\
            " debe de ser diferente",
        "true_value argument must be a non-empty string":
            "El argumento 'true_value' debe ser una cadena de texto no vacía",
        "false_value argument must be a non-empty string":
            "El argumento 'false_value' debe ser una cadena de texto no vacía",
        "true_value and false_value arguments must be different":
            "Los argumentos 'true_value' y 'false_value' deben ser diferentes",
        "First character of true_value and false_value arguments must be different":
            "El primer carácter de los argumentos 'true_value' y 'false_value'"\
            " debe de ser diferente",
        "{} is not a number": "{} no es un número",
        "{} is not a float": "{} no es un decimal",
        "{} is not an integer": "{} no es un entero",
        "Number must be at minimum {}": "El número debe ser como mínimo {}",
        "Number must be at maximum {}": "El número debe ser como máximo {}",
        "Number must be less than {}": "El número debe ser menor que {}",
        "Number must be greater than {}": "El número debe ser mayor que {}",
        "{} is not a valid choice": "{} no es una opción válida",
        "{} is not a valid {}/{} response": "{} no es una respuesta {}/{} válida",
        "'formats' argument must be specified":
            "El argumento 'formats' debe estar especificado",
        "'formats' argument must be a non-str sequence of strftime format strings":
            "El argumento 'formats' debe ser una secuencia de formato strftime",
        "'formats' argument contains invalid strftime format strings":
            "El argumento 'formats' contiene un formato strftime inválido",
        "{} is not a valid time": "{} no es una tiempo válido",
        "{} is not a valid date": "{} no es una fecha válida",
        "{} is not a valid date and time": "{} no es un fecha y tiempo válido",
    }
    if lang == "es":
        return spanish[s]
    else:
        return s


class ValidatorsException(Exception):
    """Base class for exceptions."""


class ValidationException(ValidatorsException):
    """Exception raised when a validation function is called and the
    input fails validation.
    """


class TimeoutException(ValidatorsException):
    """Exception raised when the user has failed to enter a valid input
    before the timeout period.
    """


class RetryLimitExecption(ValidatorsException):
    """Exception raised when the user has failed to enter a valid input
    within the limited number of tries given.
    """


def _err_str(value: str) -> str:
    """Return the value truncated to MAX_ERROR characters. If it's
    truncated, the returned value will have '...' on the end.

    Args:
        value (str): Value.
    
    Returns:
        str: Truncated value.
    """
    value = str(value)
    if len(value) > MAX_ERROR:
        return value[:MAX_ERROR] + "..."
    else:
        return value


def _raise_validation_exception(
    standard_msg: str, 
    custom_msg: Optional[str] = None
) -> ValidationException:
    """Raise a ValidationException.

    Args:
        standard_msg (str): Standard message.
        custom_msg (str, optional): Custom message.

    Raises:
        ValidationException: An exception with an standard or custom
            message.
    """
    if custom_msg is None:
        raise ValidationException(str(standard_msg))
    else:
        raise ValidationException(str(custom_msg))


class _GenericValidate:
    """Base generic validation.

    Args:
        value (str, optional): 
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        choices (Sequence[Any]): Sequence of choices.
        numbers (bool, optional): If True, it will also accept a number
            as a choice.
        letters (bool, optional): If True, it will also accept a letter
            as a choice.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        yes_value (str): Value of affirmative response.
            Defaults 'yes'.
        no_value (str): Value of negative response. Defaults
            'no'.
        formats (Sequence[str], optional): Sequence of formats.
        lang (str): Establish the language.
    """
    def __init__(
        self,
        value: Optional[str] = None,
        blank: Optional[bool] = None,
        strip: Union[str, bool, None] = None,
        min: Union[int, float, None] = None,
        max: Union[int, float, None] = None,
        lt: Union[int, float, None] = None,
        gt: Union[int, float, None] = None,
        exc_msg: Optional[str] = None,
        choices: Sequence[Any] = None,
        numbers: Optional[bool] = False,
        letters: Optional[bool] = False,
        sensitive: Optional[bool] = False,
        yes_value: str = "yes",
        no_value: str = "no",
        true_value: str = "True",
        false_value: str = "False",
        formats: Union[str, Sequence[str]] = None,
        lang: str = "en",
    ) -> None:
        self.value = value
        self.blank = blank
        self.strip = strip
        self.min = min
        self.max = max
        self.lt = lt
        self.gt = gt
        self.exc_msg = exc_msg
        self.choices = choices
        self.numbers = numbers
        self.letters = letters
        self.sensitive = sensitive
        self.yes_value = yes_value
        self.no_value = no_value
        self.true_value = true_value
        self.false_value = false_value
        self.formats = formats
        self.lang = lang

    def _prevalidation(self) -> Tuple[bool, str]:
        """Perform some pre-validations before any validation.

        Returns:
            Tuple[bool, str]: Returns a tuple of two vales, the first
                is a bool that tells the caller if they should return
                True; the second is a new possibly stripped value to
                replace the value passed for value parameter.
        """
        self.value = str(self.value)
        self.value = strip_string(self.value, self.strip)
        if not self.blank and self.value == "":
            _raise_validation_exception(
                _("Blank values are not allowed", self.lang), self.exc_msg
            )
        elif self.blank and self.value =="":
            return True, self.value
        return False, self.value

    def _validate_parameters(self) -> None:
        """Return None if blank and strip are valid.

        Raises:
            Exception: if blank or strip are invalid. 
        """
        if not isinstance(self.blank, bool):
            raise ValidatorsException(
                _("'blank' argument must be a bool", self.lang)
            )
        if not isinstance(self.strip, (bool, str, type(None))):
            raise ValidatorsException(
                _("'strip' argument must be a bool, str or None", self.lang)
            )

    def _validate_numbers_parameters(self) -> None:
        """Check parameters (numeric) in validators functions.

        Raises:
            Exception: If the numbers are invalid.
        """
        if self.min is not None and self.gt is not None:
            raise ValidatorsException(
                _( "Only one argument for 'min' or 'gt'"\
                " can be passed, not both", self.lang)
            )
        if self.max is not None and self.lt is not None:
            raise ValidatorsException(
                _("Only one argument for 'max' or 'lt'"\
                " can be passed, not both", self.lang)
            )
        if (self.min is not None and
            self.max is not None and
            self.min > self.max):
            raise ValidatorsException(
                _("The 'min' argument must be less than or equal to"\
                " 'max' argument", self.lang)
            )
        if (self.min is not None and
            self.lt is not None and
            self.min >= self.lt):
            raise ValidatorsException(
                _(
                    "The 'min' argument must be less than 'lt' argument",
                    self.lang
                )
            )
        if (self.max is not None and
            self.gt is not None and
            self.max <= self.gt):
            raise ValidatorsException(
                _(
                    "The 'max' argument must be greater than 'gt' argument",
                    self.lang
                )
            )
        for name, value in (
            ("min", self.min),
            ("max", self.max), 
            ("lt", self.lt),
            ("gt", self.gt),
        ):
            if not isinstance(value, (int, float, type(None))):
                raise ValidatorsException(
                    _(
                        "'{}' argument must be int, float, or None", self.lang
                    ).format(name)
                )
    
    def _validate_choices_parameters(self) -> None:
        """Called by validate_choice to check its arguments.

        Raises:
            Exception: If the arguments are invalid.
        """
        if not isinstance(self.sensitive, bool):
            raise ValidatorsException(
                _("'sensitive' argument must be a bool", self.lang)
            )
        if not isinstance(self.choices, (SEQUENCE_ABC, type(None))):
            raise ValidatorsException(
                _("'choices' argument must be a sequence", self.lang)
            )
        if self.choices is not None:
            try:
                len(self.choices)
            except:
                raise ValidatorsException(
                    _("'choices' argument must be a sequence", self.lang)
                )
            if self.blank == False and len(self.choices) < 2:
                raise ValidatorsException(
                    _("'choices' must have at least"\
                    " two items if 'blank' is False", self.lang)
                )
            elif self.blank == True and len(self.choices) < 1:
                raise ValidatorsException(
                    _("'choices' must have at least one item", self.lang)
                )
        self._validate_parameters()
        if self.letters and len(self.choices) > 26:
            raise ValidatorsException(
                _("'letters' cannot be True if"\
                " there are more than 26 choices", self.lang)
            )
        if self.numbers and self.letters:
            raise ValidatorsException(
                _("'numbers' and 'letters' cannot both be True", self.lang)
            )
        if len(self.choices) != len(set(self.choices)):
            raise ValidatorsException(
                _("Duplicates entries in 'choices'", self.lang)
            )
        if (not self.sensitive 
            and len(self.choices) != len(set(
                [choice.upper() for choice in self.choices]
            ))):
            raise ValidatorsException(
                _("Duplicate case-sensitive entries in 'choices'", self.lang)
            )

    def _validate_yes_no_parameters(self) -> None:
        """Called by validate_yes_no to check its arguments.

        Raises:
            Exception: If the arguments are invalid.
        """
        self.yes_value = str(self.yes_value)
        self.no_value = str(self.no_value)
        if len(self.yes_value) == 0:
            raise ValidatorsException(
                _("yes_value argument must be a non-empty string", self.lang)
            )
        if len(self.no_value) == 0:
            raise ValidatorsException(
                _("no_value argument must be a non-empty string", self.lang)
            )
        if (self.yes_value == self.no_value or
            (not self.sensitive and
            self.yes_value.upper() == self.no_value.upper())):
            raise ValidatorsException(
                _(
                    "yes_value and no_value arguments must be different",
                    self.lang
                )
            )
        if (self.yes_value[0] == self.no_value or
            (not self.sensitive and
            self.yes_value[0].upper() == self.no_value[0].upper())):
            raise ValidatorsException(
                _("First character of yes_value and"\
                " no_value arguments must be different", self.lang)
            )
    
    def _validate_bool_parameters(self) -> None:
        """Called by validate_bool to check its arguments.

        Raises:
            Exception: If the arguments are invalid.
        """
        self.true_value = str(self.true_value)
        self.false_value = str(self.false_value)
        if len(self.true_value) == 0:
            raise ValidatorsException(
                _("true_value argument must be a non-empty string", self.lang)
            )
        if len(self.false_value) == 0:
            raise ValidatorsException(
                _("false_value argument must be a non-empty string", self.lang)
            )
        if ((self.true_value == self.false_value) or 
            (not self.sensitive and
            self.true_value.upper() == self.false_value.upper())):
            raise ValidatorsException(
                _(
                    "true_value and false_value arguments must be different",
                    self.lang,
                )
            )
        if ((self.true_value[0] == self.false_value[0]) or 
            (not self.sensitive and
            self.true_value[0].upper() == self.false_value[0].upper())):
            raise ValidatorsException(
                _(
                    "First character of true_value and false_value arguments" \
                    " must be different",
                    self.lang,
                )
            )

    def _validate_datetime_parameters(self) -> None:
        """Called by validate_date to check its arguments.

        Raises:
            Exception: If the arguments are invalid.
        """
        if self.formats is None:
            raise ValidatorsException(
                _("'formats' argument must be specified", self.lang)
            )
        if isinstance(self.formats, str):
            raise ValidatorsException(
                _(
                    "'formats' argument must be a non-str sequence of" \
                    " strftime format strings", self.lang)
            )
        if not isinstance(self.formats, SEQUENCE_ABC):
            raise ValidatorsException(
                _(
                    "'formats' argument must be a non-str sequence of" \
                    " strftime format strings", self.lang)
            )
        for time_format in self.formats:
            try:
                time.strftime(time_format)
            except: 
                raise ValidatorsException(
                    _(
                        "'formats' argument contains invalid strftime" \
                        " format strings", self.lang)
                )


def validate_number(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    n_type: str = "num",
    min: Union[int, float, None] = None,
    max: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    gt: Union[int, float, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> Union[int, float, str]:
    """Validate a number.

    Args:
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        n_type (str): One of 'num', 'int', or 'float' to validate
            against, where 'num' means int or float.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        exc_msg (str): Custom message for exceptions. Defaults to
            None.
        lang (str): Establish the language.

    Raises:
        ValidatorsException: If value is not a float or int.

    Returns:
        Union[int, float, str]: Value.
    """
    assert n_type in ("num", "int", "float")
    generic = _GenericValidate(
        value=value,
        blank=blank,
        strip=strip,
        min=min,
        max=max,
        lt=lt,
        gt=gt,
        exc_msg=exc_msg,
        lang=lang,
    )
    generic._validate_parameters()
    generic._validate_numbers_parameters()
    return_now, value = generic._prevalidation()
    if return_now:
        if (n_type == "num" and "." in value) or (n_type == "float"):
            try:
                return float(value)
            except ValueError:
                return value
        elif ((n_type == "num" and "." not in value) or
            (n_type == "int")):
            try:
                return int(value)
            except ValueError:
                return value
        else:
            assert False
    if n_type == "num" and "." in value:
        try:
            numeric_value = float(value)
        except:
            _raise_validation_exception(
                _("{} is not a number", lang).format(_err_str(value)), exc_msg
            )
    elif n_type == "num" and "." not in value:
        try:
            numeric_value = int(value)
        except:
            _raise_validation_exception(
                _("{} is not a number", lang).format(_err_str(value)), exc_msg
            )
    elif n_type == "float":
        try:
            numeric_value = float(value)
        except:
            _raise_validation_exception(
                _("{} is not a float", lang).format(_err_str(value)), exc_msg
            )
    elif n_type == "int":
        try:
            if float(value) % 1 != 0:
                _raise_validation_exception(
                    _("{} is not an integer", lang).format(_err_str(value)),
                    exc_msg
                )
            numeric_value = int(float(value))
        except:
            _raise_validation_exception(
                _("{} is not an integer", lang).format(_err_str(value)),
                exc_msg
            )
    else:
        assert False
    if min is not None and numeric_value < min:
        _raise_validation_exception(
            _("Number must be at minimum {}", lang).format(min), exc_msg
        )
    if max is not None and numeric_value > max:
        _raise_validation_exception(
            _("Number must be at maximum {}", lang).format(max), exc_msg
        )
    if lt is not None and numeric_value >= lt:
        _raise_validation_exception(
            _("Number must be less than {}", lang).format(lt), exc_msg
        )
    if gt is not None and numeric_value <= gt:
        _raise_validation_exception(
            _("Number must be greater than {}", lang).format(gt), exc_msg
        )
    return numeric_value


def validate_str(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a str.

    Args:
        value (str, optional): 
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not an str.

    Returns:
        str: Value.
    """
    generic = _GenericValidate(
        value=value, blank=blank, strip=strip, exc_msg=exc_msg, lang=lang,
    )
    generic._validate_parameters()
    _, value = generic._prevalidation()
    return value


def validate_int(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    min: Union[int, float, None] = None,
    max: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    gt: Union[int, float, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> Union[int, str]:
    """Validate an integer.

    Args:
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        number_type (str): One of 'num', 'int', or 'float' to validate
            against, where 'num' means int or float.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        exc_msg (str, optional): Custom message for exceptions.
            Defaults to None.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not an int.

    Returns:
        int: Value.
    """
    return validate_number(
        value=value, 
        blank=blank, 
        strip=strip, 
        n_type="int",
        min=min,
        max=max,
        lt=lt,
        gt=gt,
        exc_msg=exc_msg,
        lang=lang,
    )


def validate_float(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    min: Union[int, float, None] = None,
    max: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    gt: Union[int, float, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> Union[int, str]:
    """Validate a float.

    Args:
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        number_type (str): One of 'num', 'int', or 'float' to validate
            against, where 'num' means int or float.
        min (Union[int, float, None]): Minimum valur (inclusive).
        max (Union[int, float, None]): Maximum value (inclusive).
        lt (Union[int, float, None]): Minimum value (exclusive).
        gt (Union[int, float, None]): Maximum value (exclusive).
        exc_msg (str, optional): Custom message for exceptions.
            Defaults to None.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a float.

    Returns:
        float: Value.
    """
    return validate_number(
        value=value, 
        blank=blank, 
        strip=strip, 
        n_type="float",
        min=min,
        max=max,
        lt=lt,
        gt=gt,
        exc_msg=exc_msg,
        lang=lang,
    )


def validate_choice(
    value: str,
    choices: Sequence[Any],
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    numbers: Optional[bool] = False,
    letters: Optional[bool] = False,
    sensitive: Optional[bool] = False,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a choice.

    Args:
        value (str, optional): The value being validated.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        choices (Sequence[Any]): Sequence of choices.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        numbers (bool, optional): If True, it will also accept a number
            as a choice.
        letters (bool, optional): If True, it will also accept a letter
            as a choice.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not one of the values in choices.

    Returns:
        str: The selected choice.
    """
    generic = _GenericValidate(
        value=value,
        choices=choices,
        blank=blank,
        strip=strip,
        numbers=numbers,
        letters=letters,
        sensitive=sensitive,
        exc_msg=exc_msg,
        lang=lang,
    )
    generic._validate_choices_parameters()
    str_choices = [str(choice) for choice in choices]
    if "" in str_choices:
        generic.blank = True
    return_now, value = generic._prevalidation()
    if return_now:
        return value
    if value in str_choices:
        return value
    if (numbers and value.isdigit() and
        0 < int(value) <= len(str_choices)):
        return str_choices[int(value) - 1]
    if (letters and
        len(value) == 1 and
        value.isalpha() and
        0 < ord(value.upper()) - 64 <= len(str_choices)
    ):
        return str_choices[ord(value.upper()) - 65]
    if not sensitive and value.upper() in [
        choice.upper() for choice in str_choices
    ]:
        return str_choices[[
            choice.upper()
            for choice in str_choices].index(value.upper())
        ]
    _raise_validation_exception(
        _("{} is not a valid choice", lang).format(_err_str(value))
    )


def validate_yes_no(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    yes_value: Optional[str] = "yes",
    no_value: Optional[str] = "no",
    sensitive: Optional[bool] = False,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a yes/no response.

    Args:
        value (str, optional): The value being validated.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        yes_value (bool, optional): Value of affirmative response.
            Defaults 'yes'.
        no_value (bool, optional): Value of negative response. Defaults
            'no'.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not a yes or no response.

    Returns:
        str: The yes_val or no_val argument, not value.
    """
    generic = _GenericValidate(
            value=value,
            blank=blank,
            strip=strip,
            yes_value=yes_value,
            no_value=no_value,
            sensitive=sensitive,
            exc_msg=exc_msg,
            lang=lang,
        )
    generic._validate_parameters()
    generic._validate_yes_no_parameters()
    return_now, value = generic._prevalidation()
    if return_now:
        return value
    if sensitive:
        if value in (yes_value, yes_value[0]):
            return yes_value
        elif value in (no_value, no_value[0]):
            return no_value
    else:
        if value.upper() in (yes_value.upper(), yes_value[0].upper()):
            return yes_value
        elif value.upper() in (no_value.upper(), no_value[0].upper()):
            return no_value
    _raise_validation_exception(
        _(
            "{} is not a valid {}/{} response", lang
        ).format(_err_str(value), yes_value, no_value)
    )
    assert False


def validate_bool(
    value: str,
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    true_value: Optional[str] = "True",
    false_value: Optional[str] = "False",
    sensitive: Optional[bool] = False,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a yes/no response.

    Args:
        value (str, optional): The value being validated.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        true_value (bool, optional): Value of True. Defaults 'True'.
        false_value (bool, optional): Value of False. Defaults 'False'.
        sensitive (bool, optional): If True, then the exact case of the
            option must be entered.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.

    Raises:
        Exception: If value is not a "True" or "False" response.

    Returns:
        str: The true_value or false_value argument, not value.
    """
    generic = _GenericValidate(
            value=value,
            blank=blank,
            strip=strip,
            true_value=true_value,
            false_value=false_value,
            sensitive=sensitive,
            exc_msg=exc_msg,
            lang=lang,
        )
    generic._validate_parameters()
    generic._validate_bool_parameters()
    return_now, value = generic._prevalidation()
    if return_now:
        return value
    try:
        result = validate_yes_no(
            value,
            blank=blank,
            strip=strip,
            yes_value=true_value,
            no_value=false_value,
            sensitive=sensitive,
            exc_msg=None,
            lang=lang,
        )
    except ValidationException:
        _raise_validation_exception(
            _(
                "{} is not a valid {}/{} response", lang
            ).format(_err_str(value), true_value, false_value)
        )
    
    if result == true_value:
        return True
    elif result == false_value:
        return False
    else:
        assert False


def _validate_to_datetime_format(
    value: str,
    formats: Union[str, Sequence[str]],
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Function used by validate_datetime.

    Args:
        value (str, optional): The value being validated.
        formats (Union[str, Sequence[str]]): The formats to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a valid datetime.

    Returns:
        str: The value argument, not value.
    """
    generic = _GenericValidate(
            value=value,
            formats=formats,
            blank=blank,
            strip=strip,
            exc_msg=exc_msg,
            lang=lang,
        )
    generic._validate_parameters()
    generic._validate_datetime_parameters()
    return_now, value = generic._prevalidation()
    if return_now:
        for time_format in formats:
            try:
                return datetime.datetime.strptime(value, time_format)
            except ValueError:
                continue
        return value
    for time_format in formats:
        try:
            return datetime.datetime.strptime(value, time_format)
        except ValueError:
            continue
    _raise_validation_exception(_("{} is not a valid datetime").format(_err_str(value)))
    assert False


def validate_date(
    value: str,
    formats: Union[str, Sequence[str]] = (
        "%Y/%m/%d", "%y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%x",
    ),
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a date.

    Args:
        value (str, optional): The value being validated.
        formats (Union[str, Sequence[str]]): The formats to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a valid date.

    Returns:
        str: The value argument, not value.
    """
    try:
        dt = _validate_to_datetime_format(
            value=value,
            formats=formats,
            blank=blank,
            strip=strip,
            exc_msg=exc_msg,
            lang=lang,
        )
    except ValidationException:
        _raise_validation_exception(
            _("{} is not a valid date").format(_err_str(value))
        )
    if isinstance(dt, str):
        return dt
    return datetime.date(dt.year, dt.month, dt.day)


def validate_time(
    value: str,
    formats: Union[str, Sequence[str]] = ("%H:%M:%S", "%H:%M", "%X"),
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a time.

    Args:
        value (str, optional): The value being validated.
        formats (Union[str, Sequence[str]]): The formats to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a valid time.

    Returns:
        str: The value argument, not value.
    """
    try:
        dt = _validate_to_datetime_format(
            value=value,
            formats=formats,
            blank=blank,
            strip=strip,
            exc_msg=exc_msg,
            lang=lang,
        )
    except ValidationException:
        _raise_validation_exception(
            _("{} is not a valid time").format(_err_str(value))
        )
    if isinstance(dt, str):
        return dt
    return datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond)


def validate_datetime(
    value: str,
    formats: Union[str, Sequence[str]] = (
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%x %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%y/%m/%d %H:%M",
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M",
        "%x %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%x %H:%M:%S",
    ),
    blank: Optional[bool] = False,
    strip: Union[str, bool, None] = None,
    exc_msg: Optional[str] = None,
    lang: str = "en",
) -> str:
    """Validate a datetime.

    Args:
        value (str, optional): The value being validated.
        formats (Union[str, Sequence[str]]): The formats to use.
        blank (bool, optional): If True, a blank string will be
            accepted. Defaults to False.
        strip (Union[None, str, bool], optional): If None, whitespace
            is strip from value. If str, the characters in it are
            stripped. If False, nothing is stripped.
        exc_msg (str, optional): Custom message to use in the raised
            ValidatorsException.
        lang (str): Establish the language.
    
    Raises:
        Exception: If value is not a valid datetime.

    Returns:
        str: The value argument, not value.
    """
    try:
        return _validate_to_datetime_format(
            value=value,
            formats=formats,
            blank=blank,
            strip=strip,
            exc_msg=exc_msg,
            lang=lang,
        )
    except ValidationException:
        _raise_validation_exception(
            _("{} is not a valid date and time").format(_err_str(value))
        )
    assert False


def validate_email():
    raise NotImplementedError()


def validate_phone():
    raise NotImplementedError()


def validate_name():
    raise NotImplementedError()
