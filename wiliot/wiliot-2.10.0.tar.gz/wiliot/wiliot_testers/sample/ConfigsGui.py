"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
'''
Created on Nov 1, 2021

@author: davidd
'''
import logging
import pygubu
from os.path import join, abspath, dirname, isfile
from json import dump, load
from copy import deepcopy

MEASURED = {'button': 'Measured', 'label': '[meter]'}
MANUAL = {'button': 'Manual', 'label': '[db]'}
DEFAULT_CONFIG = 'TEO'

logger = logging.getLogger('__main__')


class ConfigsGui(object):
    '''
    classdocs
    '''
    isGui = False
    atten_cur_mode = MANUAL
    tag_type = ''
    config = ''
    configsDict = {}
    paramDict = {}
    userConfigsDict = {}
    defaultConfigsDict = {}

    def __init__(self, top_builder=None):
        '''
        Constructor
        '''
        self.top_builder = top_builder
        if isfile(join('configs', '.user_configs.json')):
            with open(join('configs', '.user_configs.json'), 'r') as jsonFile:
                self.configsDict = self.userConfigsDict = load(jsonFile)
        with open(join('configs', '.default_configs.json'), 'r') as jsonFile:
            self.defaultConfigsDict = load(jsonFile)
            def_dict = deepcopy(self.defaultConfigsDict)
            self.configsDict.update(def_dict)

    def gui(self, ttk_frame=None):
        self.builder = builder = pygubu.Builder()
        ui_file = join(abspath(dirname(__file__)), 'utils', 'configs.ui')
        self.builder.add_from_file(ui_file)

        img_path = join(abspath(dirname(__file__)), '.')
        builder.add_resource_path(img_path)
        img_path = join(abspath(dirname(__file__)), 'utils')
        builder.add_resource_path(img_path)

        self.ttk = ttk_frame

        self.ttk.title("Sample Test Configs")

        self.mainwindow = self.builder.get_object('mainwindow', self.ttk)

        self.builder.connect_callbacks(self)

        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.ttk.lift()
        self.ttk.attributes("-topmost", True)
        self.ttk.attributes("-topmost", False)

        self.set_gui_defaults()

        self.isGui = True
        self.ttk.mainloop()

    def set_gui_defaults(self):
        temp_dict = deepcopy(self.configsDict)
        # temp_dict.update(self.userConfigsDict)
        self.builder.get_object('configsList')['values'] = [key for key, item in temp_dict.items()
                                                            if isinstance(item, dict)]
        if temp_dict.get(self.config):
            self.builder.get_object('configsList').set(self.config)
            self.top_builder.tkvariables.get('testTime').set(temp_dict[self.config]['testTime'])
            for param, value in temp_dict[self.config].items():
                if self.builder.tkvariables.get(param) is not None:
                    if isinstance(value, str) and '\\u' in value:
                        self.builder.tkvariables.get(param).set(eval(f'u"{value}"'))
                    else:
                        self.builder.tkvariables.get(param).set(value)
                else:
                    logger.error(f'Missing parameter {param}')

    def atten_mode(self):
        self.atten_cur_mode = MEASURED if self.atten_cur_mode == MANUAL else MANUAL
        self.builder.tkvariables.get('atten_mode').set(self.atten_cur_mode['button'])
        ble_label = self.builder.tkvariables.get('attenBleLabel')
        ble_label.set(ble_label.get().split()[0] + ' ' + self.atten_cur_mode['label'])
        lora_label = self.builder.tkvariables.get('attenLoRaLabel')
        lora_label.set(lora_label.get().split()[0] + ' ' + self.atten_cur_mode['label'])

    def close(self):
        self.isGui = False
        for param in self.configsDict[DEFAULT_CONFIG].keys():
            value = self.builder.tkvariables.get(param).get()
            self.paramDict[param] = value
            self.configsDict[self.config][param] = value
        self.ttk.destroy()

    def is_gui_opened(self):
        return self.isGui

    def get_params(self):
        return self.paramDict

    def get_configs(self):
        temp_dict = deepcopy(self.configsDict)
        temp_dict.update(self.userConfigsDict)
        return temp_dict

    def set_params(self, tag_type):
        self.paramDict = self.configsDict[tag_type]
        self.top_builder.tkvariables.get('testTime').set(self.paramDict['testTime'])

    def set_default_config(self, tag_type):
        self.tag_type = tag_type
        self.config = tag_type

    def config_select(self, *args):
        self.config = self.builder.get_object('configsList').get()
        self.top_builder.get_object('test_config').set(self.config)
        self.reset()

    def config_set(self, config):
        self.config = config
        self.set_params(config)
        if self.isGui:
            self.builder.get_object('configsList').set(config)
            self.set_gui_defaults()
        # except BaseException:
        #     pass

    def save(self):
        self.config = config = self.builder.get_object('configsList').get()
        if config not in self.defaultConfigsDict.keys():
            self.userConfigsDict[config] = {}
            for param in self.configsDict[DEFAULT_CONFIG].keys():
                value = self.builder.tkvariables.get(param)
                if value is not None:
                    self.userConfigsDict[config][param] = value.get()
            if config not in self.configsDict.keys():
                self.configsDict[config] = {}
            self.configsDict[config].update(self.userConfigsDict[config])
        self.builder.get_object('configsList')['values'] = [key for key, item in self.configsDict.items()
                                                            if isinstance(item, dict)]
        self.top_builder.get_object('test_config')['values'] = [key for key, item in self.configsDict.items()
                                                                if isinstance(item, dict)]
        self.top_builder.get_object('test_config').set(config)

        with open(join('configs', '.user_configs.json'), 'w+') as jsonFile:
            dump(self.userConfigsDict, jsonFile, indent=4)

    def reset(self):
        self.configsDict = deepcopy(self.userConfigsDict)
        def_dict = deepcopy(self.defaultConfigsDict)
        self.configsDict.update(def_dict)
        self.set_gui_defaults()

    def test_time_update(self, *args):
        self.top_builder.tkvariables.get('testTime').set(self.builder.tkvariables.get('testTime').get())
