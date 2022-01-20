# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import traceback
from alphalogic_api3.attributes import Visible, Access, Priority
from alphalogic_api3.logger import log
from alphalogic_api3.utils import Exit, value_from_rpc, decode_string


class ConfInspector(object):

    def is_parameter_exist(self, name, object):
        try:
            parameter = object.parameter(name)
            return parameter
        except Exception:
            return None

    def check_parameter_accordance(self, parameter_model):
        try:
            id_parameter = parameter_model.id
            #1 check value_type
            if parameter_model.value_type is bool and not(parameter_model.is_bool()):
                raise Exception('Real and model type are different')
            elif parameter_model.value_type is int and not(parameter_model.is_long()):
                raise Exception('Real and model type are different')
            elif parameter_model.value_type is float and not(parameter_model.is_double()):
                raise Exception('Real and model type are different')
            elif parameter_model.value_type is datetime.datetime and not(parameter_model.is_datetime()):
                raise Exception('Real and model type are different')
            elif parameter_model.value_type is str and not(parameter_model.is_string()):
                raise Exception('Real and model type are different')

            #2 check visible
            if parameter_model.visible == Visible.runtime and not(parameter_model.is_runtime()):
                raise Exception('Real and model visible are different')
            elif parameter_model.visible == Visible.setup and not(parameter_model.is_setup()):
                raise Exception('Real and model visible are different')
            elif parameter_model.visible == Visible.hidden and not(parameter_model.is_hidden()):
                raise Exception('Real and model visible are different')
            elif parameter_model.visible == Visible.common and not(parameter_model.is_common()):
                raise Exception('Real and model visible are different')

            # 3 check access
            if parameter_model.access == Access.read_only and not(parameter_model.is_read_only()):
                raise Exception('Real and model access are different')
            elif parameter_model.access == Access.read_write and not(parameter_model.is_read_write()):
                raise Exception('Real and model access are different')

            # 4 check enums
            '''
            model_choices = parameter_model.choices
            real_choices = parameter_model.enums()
            if model_choices is None and len(real_choices) != 0:
                raise Exception('Real and model enums are different')
            elif model_choices is not None:
                if len(model_choices) != len(real_choices):
                    raise Exception('Real and model enums are different')
                else:
                    if type(model_choices[0]) is not tuple:
                        model_vals = sorted(model_choices)
                        real_vals  = sorted(zip(*real_choices)[0])
                        if model_vals != real_vals:
                            raise Exception('Real and model enums are different')
                    else:
                        model_vals, model_keys = zip(*model_choices)
                        model_vals, model_keys = sorted(model_vals), sorted(model_keys)
                        real_vals, real_keys = zip(*real_choices)
                        real_vals, real_keys = sorted(real_vals), sorted(real_keys)
                        if model_vals != real_vals or model_keys != real_keys:
                            raise Exception('Real and model enums are different')
            '''
        except Exception as err:
            t = traceback.format_exc()
            log.error(f'Parameter discrepancy \'{parameter_model.name()}\':\n{decode_string(t)}')
            raise Exit

    def is_event_exist(self, name, object):
        try:
            event = object.event(name)
            return event
        except Exception as err:
            return None

    def check_event_accordance(self, event_model):
        try:
            id_event = event_model.id
            # 1 check priority
            if event_model.priority == Priority.blocker and not(event_model.is_blocker()):
                raise Exception('Real and model priority are different')
            elif event_model.priority == Priority.critical and not(event_model.is_critical()):
                raise Exception('Real and model priority are different')
            elif event_model.priority == Priority.major and not(event_model.is_major()):
                raise Exception('Real and model priority are different')
            elif event_model.priority == Priority.minor and not(event_model.is_minor()):
                raise Exception('Real and model priority are different')

            # 2 check argument list in code and configuration
            code_arguments_list = set([x[0] for x in event_model.arguments])
            conf_arguments_list = set(event_model.argument_list())
            if code_arguments_list != conf_arguments_list:
                raise Exception('Event arguments list mismathcing: {0}'.format(conf_arguments_list^code_arguments_list))

            # 3 check argument list and check type in argument_list
            for arg_name_model, arg_type_model in event_model.arguments:
                arg_name_real, arg_value = event_model.argument(arg_name_model)
                arg_type_real = type(value_from_rpc(arg_value))
                if arg_name_model != arg_name_real or \
                        not(self.check_value_type_accordance(arg_type_model, arg_type_real)):
                    raise Exception('Real and model arguments are different')

        except Exception as err:
            t = traceback.format_exc()
            log.error('Event discrepancy \'{0}\'\n{1}'.format(event_model.name(), decode_string(t)))
            raise Exit

    def check_command_accordance(self, command_model):
        try:
            id_command = command_model.id
            # 1 check return type
            '''
            model_result_type = command_model.result_type
            if model_result_type is bool and not(command_model.is_bool()):
                raise Exception('Real and model result type are different')
            elif model_result_type is int and not(command_model.is_long()):
                raise Exception('Real and model result type are different')
            elif model_result_type is float and not(command_model.is_double()):
                raise Exception('Real and model result type are different')
            elif model_result_type is datetime.datetime and not(command_model.is_datetime()):
                raise Exception('Real and model result type are different')
            elif model_result_type is unicode and not(command_model.is_string()):
                raise Exception('Real and model result type are different')
            '''

            # 2 check argument list and check type in argument_list
            for arg_name_model, _ in command_model.arguments:
                arg_type_model = command_model.arguments_type[arg_name_model]
                arg_name_real, arg_value = command_model.argument(arg_name_model)
                arg_type_real = type(value_from_rpc(arg_value))
                if arg_name_model != arg_name_real or \
                        not(self.check_value_type_accordance(arg_type_model, arg_type_real)):
                    raise Exception('Real and model arguments are different')

        except Exception as err:
            t = traceback.format_exc()
            log.error('Command discrepancy \'{0}\': {1}'.format(command_model.name(), decode_string(t)))
            raise Exit

    def check_value_type_accordance(self, arg_type_model, arg_type_real):
        if arg_type_model is str and arg_type_real is str:
            return True
        elif arg_type_model is int and arg_type_real is int:
            return True
        elif arg_type_model is float and arg_type_real is float:
            return True
        elif arg_type_model is datetime.datetime and arg_type_real is datetime.datetime:
            return True
        elif arg_type_model is bool and arg_type_real is bool:
            return True
        else:
            return False
