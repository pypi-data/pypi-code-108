'''Expansion of python configparser module

Insert description here
'''

import configparser
import logging
from pathlib import Path
from collections import OrderedDict as _default_dict
from beetools import Archiver, result_rep

_PROJ_DESC = __doc__.split('\n')[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem


class ConfigParserExt(configparser.ConfigParser):
    '''Insert description here'''

    def __init__(
        self,
        defaults=None,
        dict_type=_default_dict,
        allow_no_value=False,
        delimiters=('=', ':'),
        comment_prefixes=('#', ';'),
        inline_comment_prefixes=None,
        strict=True,
        empty_lines_in_values=True,
        default_section=configparser.DEFAULTSECT,
        interpolation=configparser._UNSET,
        converters=configparser._UNSET,
        p_parent_logger_name=None,
    ):
        '''Insert description here'''
        self.success = False
        if p_parent_logger_name:
            self.logger_name = '{}.{}'.format(p_parent_logger_name, _PROJ_NAME)
            self.logger = logging.getLogger(self.logger_name)
        super().__init__(
            defaults=defaults,
            dict_type=dict_type,
            allow_no_value=allow_no_value,
            delimiters=delimiters,
            comment_prefixes=comment_prefixes,
            inline_comment_prefixes=inline_comment_prefixes,
            strict=strict,
            empty_lines_in_values=empty_lines_in_values,
            default_section=default_section,
            interpolation=interpolation,
            converters=converters,
        )

    def get(
        self,
        p_section,
        p_option,
        p_prefix=False,
        p_split=False,
        raw=False,
        vars=None,
        fallback=configparser._UNSET,
    ):
        '''Insert description here'''

        def split_value(p_value):
            value_parsed = p_value.split(';')
            return value_parsed

        # end split_value

        if p_prefix:
            value_series = []
            option_series = self.options(p_section, p_option)
            for option in option_series:
                value_parsed = super().get(
                    p_section, option, raw=raw, vars=vars, fallback=fallback
                )
                if p_split:
                    value_parsed = split_value(value_parsed)
                value_series.append([option, value_parsed])
        else:
            value_series = super().get(
                p_section, p_option, raw=raw, vars=vars, fallback=fallback
            )
            if p_split:
                value_series = split_value(value_series)
        return value_series

    def options(self, p_section, p_option_prefix=None):
        '''Insert description here'''
        all_options = series = super().options(p_section)
        if p_option_prefix:
            series = []
            for option in sorted(all_options):
                x = len(p_option_prefix)
                if option[:x].lower() == p_option_prefix.lower():
                    series.append(option)
        return series

    def sections(self, p_section_prefix=''):
        '''Insert description here'''
        all_sections = series = super().sections()
        if p_section_prefix:
            series = []
            for section in all_sections:
                x = len(p_section_prefix)
                if section[:x] == p_section_prefix:
                    series.append(section)
        return series


def do_examples(p_cls=True):
    '''Insert description here'''

    def basic_test():
        '''Basic and mandatory scenario tests for certification of the class'''
        success = True
        t_series_prefix = 'Series'
        t_sections_01 = ['General', 'Series01', 'Series02', 'Series03']
        t_sections_02 = ['Series01', 'Series02', 'Series03']
        t_options_01 = ['cmd1', 'cmd2', 'str1', 'str2']
        t_options_02 = ['cmd1', 'cmd2']
        t_value_01 = 'This;option;can;be;slit'
        t_value_02 = 'It;split;at;the;semicolon'
        t_value_03 = [
            ['cmd1', 'This;option;can;be;slit'],
            ['cmd2', 'It;split;at;the;semicolon'],
        ]
        t_value_split_03 = [
            ['cmd1', ['This', 'option', 'can', 'be', 'slit']],
            ['cmd2', ['It', 'split', 'at', 'the', 'semicolon']],
        ]
        t_cfg_ext = ConfigParserExt()
        t_cfg_ext['General'] = {'SeriesPrefix': 'Series', 'OptionPrefix': 'Cmd'}
        t_cfg_ext['Series01'] = {'Cmd1': 'ls', 'Cmd2': 'll', 'Val1': 1, 'Val2': 2}
        t_cfg_ext['Series02'] = {
            'Cmd1': 'This;option;can;be;slit',
            'Cmd2': 'It;split;at;the;semicolon',
            'Str1': 'c',
            'Str2': 'd',
        }
        t_cfg_ext['Series03'] = {'Cmd1': 5, 'Cmd2': 6, 'Str1': 'e', 'Str2': 'f'}

        sections_series = t_cfg_ext.sections()
        if sections_series != t_sections_01:
            success = False and success
            result_rep(success, 't_sections_01')
        series_prefix = t_cfg_ext.get('General', 'SeriesPrefix')
        if series_prefix != t_series_prefix:
            success = False and success
            result_rep(success, 't_series_prefix')
        sections_series = t_cfg_ext.sections(series_prefix)
        if sections_series != t_sections_02:
            success = False and success
            result_rep(success, 't_sections_02')
        option_prefix = t_cfg_ext.get('General', 'OptionPrefix')
        option_series = t_cfg_ext.options('Series02')
        if option_series != t_options_01:
            success = False and success
            result_rep(success, 't_options_01')
        option_series = t_cfg_ext.options('Series02', option_prefix)
        if option_series != t_options_02:
            success = False and success
            result_rep(success, 't_options_02')
        value = t_cfg_ext.get('Series02', 'Cmd1')
        if value != t_value_01:
            success = False and success
            result_rep(success, 't_value_01')
        value = t_cfg_ext.get('Series02', 'Cmd2')
        if value != t_value_02:
            success = False and success
            result_rep(success, 't_value_02')
        value_series = t_cfg_ext.get('Series02', 'Cmd', p_prefix=True)
        if value_series != t_value_03:
            success = False and success
            result_rep(success, 't_value_03')
        value_series = t_cfg_ext.get('Series02', 'Cmd', p_prefix=True, p_split=True)
        if value_series != t_value_split_03:
            success = False and success
            result_rep(success, 't_value_split_03')
        result_rep(success, 'Completed')
        return success

    archiver = Archiver(_PROJ_DESC, _PROJ_PATH)
    archiver.print_header(p_cls=p_cls)
    success = basic_test()
    archiver.print_footer()
    return success


# end do_tests


def project_desc():
    return _PROJ_DESC


if __name__ == '__main__':
    do_examples()
# end __main__
