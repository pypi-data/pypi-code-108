# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
from tcell_agent.rust.models.diagnostics_config import DiagnosticsConfig


class DiagnosticsConfigTests(object):
    def setup_method(self):
        class AgentConfig(object):
            config_filename = 'a'
            demomode = 'b'
            enabled = 'c'
            enabled_instrumentations = 'd'
            max_data_ex_db_records_per_request = 'e'
            preload_policy_filename = 'f'
            reverse_proxy = 'g'
            tcell_home = 'h'
        self.config = AgentConfig()

    def test_config_has_expected_keys(self):
        expected_keys = [
            'config_filename',
            'demomode',
            'enabled',
            'enabled_instrumentations',
            'max_data_ex_db_records_per_request',
            'preload_policy_filename',
            'reverse_proxy',
            'tcell_home',
        ]
        assert sorted(list(DiagnosticsConfig(self.config).keys())) == sorted(expected_keys)

    def test_to_properties_returns_correct_config(self):
        expected_properties = [
            {'name': 'config_filename', 'value': 'a'},
            {'name': 'demomode', 'value': 'b'},
            {'name': 'enabled', 'value': 'c'},
            {'name': 'enabled_instrumentations', 'value': 'd'},
            {'name': 'max_data_ex_db_records_per_request', 'value': 'e'},
            {'name': 'preload_policy_filename', 'value': 'f'},
            {'name': 'reverse_proxy', 'value': 'g'},
            {'name': 'tcell_home', 'value': 'h'},
        ].sort(key=lambda x: x['name'])
        properties = DiagnosticsConfig(self.config).to_properties().sort(key=lambda x: x['name'])

        assert properties == expected_properties
