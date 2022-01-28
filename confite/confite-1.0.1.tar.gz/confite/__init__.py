import os
import base64
from formatter import format_multiline_string


class Confite(object):

    # -----------------------------------------------------
    # CLASS CONSTRUCTOR
    # -----------------------------------------------------
    def __init__(self, env_variable_names: list):
        self.config_map: dict = {}
        self.__errors: list = []
        self.__load_config(env_variable_names=env_variable_names)

    # -----------------------------------------------------
    # FORMAT ERRORS
    # -----------------------------------------------------
    def __format_errors(self) -> str:
        formatted_error_list: str = ''
        for error in self.__errors:
            formatted_error_list += f'\n {error}'
        return formatted_error_list

    # -----------------------------------------------------
    # LOAD CONFIG
    # -----------------------------------------------------
    def __load_config(self, env_variable_names: list):
        for variable in env_variable_names:
            try:
                self.config_map[variable] = \
                    self.load_env_variable(variable)
            except ValueError as ve:
                self.__errors.append(str(ve))
        if len(self.__errors) > 0:
            raise EnvironmentError(
                f'Multiple environment setup '
                f'errors: \n {self.__format_errors()}')

    # -----------------------------------------------------
    # HAS VALUE
    # -----------------------------------------------------
    def has_value(self, key) -> bool:
        if key in self.config_map:
            return True
        return False

    # -----------------------------------------------------
    # AS STRING
    # -----------------------------------------------------
    def as_str(self, key) -> str:
        return self.config_map[key]

    # -----------------------------------------------------
    # AS INT
    # -----------------------------------------------------
    def as_int(self, key) -> int or None:
        try:
            return int(self.config_map[key])
        except TypeError:
            return None

    # -----------------------------------------------------
    # AS FILE
    # -----------------------------------------------------
    def as_file(self,
                file_name: str,
                property_key: str,
                base64_decode=False,
                break_line_character='\\n'):
        with open(
                file_name,
                mode='w',
                encoding='utf-8'
        ) as property_file:
            if base64_decode:
                config_property = self.as_base64_decoded_str(property_key)
            else:
                config_property = self.config_map[property_key]
            config_property = format_multiline_string(
                config_property,
                break_line_character
            )
            property_file.write(config_property)
        return file_name

    # -----------------------------------------------------
    # AS BASE 64 DECODED STR
    # -----------------------------------------------------
    def as_base64_decoded_str(self, key) -> str:
        return str(base64.b64decode(self.config_map[key]), 'utf-8')

    # -----------------------------------------------------
    # LOAD ENV VARIABLE
    # -----------------------------------------------------
    @staticmethod
    def load_env_variable(variable_name: str) -> str:
        value = os.environ.get(variable_name)
        if value is None or value == '':
            raise ValueError(
                f'Unable to find a valid '
                f'value for variable {variable_name}'
            )
        return value
