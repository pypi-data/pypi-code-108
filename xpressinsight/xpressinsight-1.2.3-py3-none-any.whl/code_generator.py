"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import os
import sys
import shutil
from typing import TextIO, ValuesView

from . import __version__
from .app_runner import exit_msg, import_app
from .app_base import AppBase, AppConfig
from .exec_mode import ExecMode
from .types import *


def quote_mos(s: str, max_length: int = 5000) -> str:
    """ Get Mosel source code representation of a string, without type or bound checking. """
    #
    #
    #
    #
    #
    #
    #
    if '\0' in s:
        raise ValueError(r"Null character '\0' not allowed in string: {}".format(repr(s)))
    if len(s) > max_length:
        raise ValueError("The string must not be longer than {} characters: {}.".format(max_length, repr(s)))

    result = s.replace('\\', r'\\').replace('"', r'\"').replace('\n', r'\n').replace('\r', r'\r').replace('\t', r'\t')
    return '"' + result + '"'


mos_repr_str = quote_mos


def mos_repr_bool(b: bool) -> str:
    """ Get the Mosel source code representation of an bool, without type or bound checking. """
    return 'true' if b else 'false'


def mos_repr_int(i: int) -> str:
    """ Get the Mosel source code representation of an int, without type or bound checking. """
    return repr(i)


def mos_repr_real(f: float) -> str:
    """ Get the Mosel source code representation of a float, without type or bound checking. """
    #
    #
    return repr(f)


class CodeGenerator:
    BASIC_TYPE_NAME_MAP: Dict[Type[BasicType], str] = {
        boolean: 'boolean',
        integer: 'integer',
        string: 'string',
        real: 'real',
    }

    BASIC_SQL_TYPE_NAME_MAP: Dict[Type[BasicType], str] = {
        boolean: 'SQL_TYPE_BOOL',
        integer: 'SQL_TYPE_INT',
        string: 'SQL_TYPE_STR',
        real: 'SQL_TYPE_REAL',
    }

    def __init__(self, app_cls: Type[AppBase], file: TextIO):
        self.file: TextIO = file
        self.app_cls: Type[AppBase] = app_cls
        self.app_cfg: AppConfig = app_cls.app_cfg
        self.ExecModes = self.app_cfg.exec_modes
        self.Entities: ValuesView[EntityBase] = self.app_cfg.entities
        self.Params: List[Param] = [e for e in self.Entities if isinstance(e, Param)]
        self.DeclaredEntities: List[EntityBase] = [e for e in self.Entities if not isinstance(e, Param)]

    def write_header(self):
        self.file.write("""! This is a generated file. Do not modify it.
model {}
    version {}\n
    uses "mminsight"
    uses "apprunner"\n
    namespace AppRunner
    nssearch AppRunner\n\n""".format(
            quote_mos(self.app_cfg.name),
            validate_annotation_str(str(self.app_cfg.version))
        ))

    def write_app_config_annotations(self):
        for scen_type in self.app_cfg.scen_types:
            self.file.write(f"        @insight.scentypes.{validate_raw_ident(scen_type, 'scenario type identifier')}\n")

        self.file.write("\n        @insight.resultdata.delete {}\n"
                        .format(validate_annotation_str(self.app_cfg.result_data.delete.value)))

    def write_exec_mode(self, mode: ExecMode):
        self.file.write("""
        @insight.execmodes.{}.
            @descr {}
            @clearinput {}\n""".format(validate_raw_ident(mode.name, 'execution mode name'),
                                       validate_annotation_str(mode.descr), mos_repr_bool(mode.clear_input)))

        if mode.preferred_service != '':
            self.file.write("            @preferredservice {}\n".format(mode.preferred_service))

        if mode.threads != 0:
            self.file.write("            @threads {}\n".format(mode.threads))

    def write_global_annotations(self):
        self.file.write("""    (!@.\n""")
        self.write_app_config_annotations()

        for mode in self.ExecModes:
            self.write_exec_mode(mode)

        self.file.write("""
        @.              Unselect current category.
        @mc.flush       Define previous annotations as global.
    !)\n\n""")

    def write_one_line_xi_annotation(self, name: str, value: str):
        """ Write a single line Insight annotation with a value. Indentation 8."""
        self.file.write('        !@insight.{} {}\n'.format(name, validate_annotation_str(value)))

    def write_entity_annotations(self, entity: Entity):
        """ Write all annotations of an entity. Each annotation is written as a single line comment. Indentation 8. """

        #
        #

        if entity.alias != "":
            self.write_one_line_xi_annotation('alias', entity.alias)

        if entity.format != "":
            self.write_one_line_xi_annotation('format', entity.format)

        if entity.hidden != Hidden.FALSE:
            self.write_one_line_xi_annotation('hidden', entity.hidden.value)

        #
        if not isinstance(entity, Param):
            self.write_one_line_xi_annotation('manage', entity.manage.value)

        if entity.read_only:
            self.write_one_line_xi_annotation('readonly', mos_repr_bool(entity.read_only))

        if entity.transform_labels_entity != "":
            self.write_one_line_xi_annotation('transform.labels.entity', entity.transform_labels_entity)

        if not isinstance(entity, Param):
            if entity.update_after_execution:
                self.write_one_line_xi_annotation('update.afterexecution', mos_repr_bool(entity.update_after_execution))

    def declare_param(self, param: Param):
        self.write_entity_annotations(param)

        #
        param.check_type(param.default)

        if param.dtype == string:
            value_str = mos_repr_str(param.default)
        elif param.dtype == integer:
            value_str = mos_repr_int(param.default)
        elif param.dtype == real:
            value_str = param.default.hex() + "  ! " + mos_repr_real(param.default)
        elif param.dtype == boolean:
            value_str = mos_repr_bool(param.default)
        else:
            raise ValueError("Unexpected value of dtype={}.".format(param.dtype))

        self.file.write('        {} = {}\n'.format(validate_ident(param.name), value_str))

    def declare_parameters(self):
        if len(self.Params) > 0:
            self.file.write('    parameters\n')

            for i, param in enumerate(self.Params):
                if i > 0:
                    self.file.write('\n')

                self.declare_param(param)

            self.file.write('    end-parameters\n\n')

    def declare_scalar(self, scalar: Scalar):
        self.write_entity_annotations(scalar)
        self.file.write('        {}: {}\n'
                        .format(validate_ident(scalar.name), CodeGenerator.BASIC_TYPE_NAME_MAP[scalar.dtype]))

    def declare_index(self, index: Index):
        self.write_entity_annotations(index)
        self.file.write('        {}: dynamic set of {}\n'
                        .format(validate_ident(index.name), CodeGenerator.BASIC_TYPE_NAME_MAP[index.dtype]))

    @staticmethod
    def get_index_set_str(index_list: Tuple[Index]) -> str:
        result = ''

        for i, index in enumerate(index_list):
            if i > 0:
                result += ', '

            result += index.name

        return result

    def declare_array(self, name: str, index: Tuple[Index], dtype: BASIC_TYPE):
        self.file.write('        {}: dynamic array({}) of {}\n'.format(validate_ident(name),
                                                                       self.get_index_set_str(index),
                                                                       CodeGenerator.BASIC_TYPE_NAME_MAP[dtype]))

    def declare_series(self, series: Series):
        self.write_entity_annotations(series)
        self.declare_array(series.name, series.index, series.dtype)

    def declare_data_frame(self, data_frame: DataFrame):
        for i, column in enumerate(data_frame.columns):
            if i > 0:
                self.file.write('\n')

            self.write_entity_annotations(column)
            self.declare_array(data_frame.name + '_' + column.name, data_frame.index, column.dtype)

    def write_declarations(self):
        if len(self.DeclaredEntities) > 0:
            self.file.write('    public declarations\n')

            for i, entity in enumerate(self.DeclaredEntities):
                if i > 0:
                    self.file.write('\n')

                if isinstance(entity, Scalar):
                    self.declare_scalar(entity)
                elif isinstance(entity, Index):
                    self.declare_index(entity)
                elif isinstance(entity, Series):
                    self.declare_series(entity)
                elif isinstance(entity, DataFrame):
                    self.declare_data_frame(entity)
                else:
                    raise TypeError('Unexpected type "{}".'.format(type(entity).__name__))

            self.file.write('    end-declarations\n\n')

    def write_data_func_header(self, func_name: str):
        self.file.write("""    public procedure {}(
            AppRunnerScalarBoolean: array(set of string) of boolean,
            AppRunnerScalarInteger: array(set of string) of integer,
            AppRunnerScalarReal: array(set of string) of real,
            AppRunnerScalarString: array(set of string) of string)\n""".format(func_name))

    def write_data_func_footer(self):
        self.file.write('    end-procedure\n\n')

    def data_func_manage_scalar(self, scalar: Union[Scalar, Param], export: bool):
        cmd = 'AppRunnerScalar{1}("{0}") := {0}\n' if export else '{0} := AppRunnerScalar{1}("{0}")\n'
        self.file.write('        ' + cmd.format(validate_ident(scalar.name), scalar.dtype.__name__.capitalize()))

    def data_func_manage_index(self, index: Index, export: bool):
        func_name = 'exportset' if export else 'importset'
        self.file.write('        {1}("{0}", {0})\n'.format(validate_ident(index.name), func_name))

    @staticmethod
    def get_sql_index_set_list(index_list: Tuple[Index]) -> str:
        result = '['

        for i, index in enumerate(index_list):
            if i > 0:
                result += ', '

            result += '["{0}", {1}]'.format(index.name, CodeGenerator.BASIC_SQL_TYPE_NAME_MAP[index.dtype])

        return result + ']'

    def data_func_manage_array(self, array_name: str, index: Tuple[Index], dtype: BASIC_TYPE, manage: Manage,
                               export: bool):
        func_name = 'exportarraysql' if export else 'importarraysql'
        err_msg = 'EXPORT_ARRAY_SQL_ERR_MSG' if export else 'IMPORT_ARRAY_SQL_ERR_MSG'
        self.file.write("""        SQLexecute({3}("{0}", {1},
            {2}), {0})
        checksqlstatus({4}, ["{0}"])\n"""
                        .format(validate_ident(array_name),
                                CodeGenerator.BASIC_SQL_TYPE_NAME_MAP[dtype],
                                self.get_sql_index_set_list(index),
                                func_name, err_msg))

        if export and manage == Manage.INPUT:
            self.file.write('        delcell({})\n'.format(array_name))

    def write_data_func(self, func_name: str, entities: List[EntityBase], manage: Manage, export: bool):
        self.write_data_func_header(func_name)
        i = 0

        for entity in entities:
            if isinstance(entity, Entity):
                if entity.is_managed(manage):
                    i += 1
                    if isinstance(entity, (Scalar, Param)):
                        self.data_func_manage_scalar(entity, export)
                    elif isinstance(entity, Index):
                        self.data_func_manage_index(entity, export)
                    elif isinstance(entity, Series):
                        self.data_func_manage_array(entity.name, entity.index, entity.dtype, manage, export)
                    else:
                        raise TypeError('Unexpected type "{}".'.format(type(entity).__name__))
            elif isinstance(entity, DataFrame):
                for column in entity.columns:
                    if column.is_managed(manage):
                        i += 1
                        self.data_func_manage_array(entity.name + '_' + column.name, entity.index, column.dtype,
                                                    manage, export)
            else:
                raise TypeError('Unexpected type "{}".'.format(type(entity).__name__))

        if i == 0:
            self.file.write('        assert(true)\n')

        self.write_data_func_footer()

    def write_data_funcs(self):
        self.write_data_func('AppRunner~exportparams', self.Params, Manage.INPUT, export=True)
        self.write_data_func('AppRunner~importinputs', self.DeclaredEntities, Manage.INPUT, export=False)
        self.write_data_func('AppRunner~exportinputs', self.DeclaredEntities, Manage.INPUT, export=True)
        self.write_data_func('AppRunner~importresults', self.DeclaredEntities, Manage.RESULT, export=False)

    def write_footer(self):
        self.file.write('    runapp\n')
        self.file.write('end-model\n')

    def generate_mos(self):
        self.write_header()
        self.write_global_annotations()
        self.declare_parameters()
        self.write_declarations()
        self.write_data_funcs()
        self.write_footer()


def generate(app_source_dir: str, target_file: str, app_package_name: str = 'application'):
    print("Python", sys.version)
    print("xpressinsight package v" + __version__)

    #
    if not os.path.isdir(os.path.dirname(target_file)):
        try:
            os.makedirs(os.path.dirname(target_file))
        except (FileExistsError, OSError):
            exit_msg(-1, 'Could not create the directory for target_file="{}"'.format(target_file))

    #
    app_cls = import_app(app_source_dir, app_package_name)
    print("Application class:", app_cls.__name__)
    print("Application name:", app_cls.app_cfg.name)

    #
    if os.path.isfile(os.path.join(app_source_dir, app_package_name + '._mos')):
        #
        hard_coded_template = os.path.join(app_source_dir, app_package_name + '._mos')
        print('Using hard coded template:', hard_coded_template, file=sys.stderr)
        shutil.copyfile(hard_coded_template, target_file)
    else:
        #
        with open(target_file, 'w', encoding='utf8') as file:
            CodeGenerator(app_cls, file).generate_mos()
