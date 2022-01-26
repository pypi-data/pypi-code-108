"""
 * $Id: 0.8+14 model_data_service.py 7495965f5725 2019-09-24 od $
 *
 * This file is part of the Cloud Services Integration Platform (CSIP),
 * a Model-as-a-Service framework, API and application suite.
 *
 * 2012-2018, Olaf David and others, OMSLab, Colorado State University.
 *
 * OMSLab licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
"""
import json, os

from collections import OrderedDict
from typing import AnyStr
from csip.utils import Client


class ModelDataService(object):
    """
    ModelDataService Python implementation.
    """

    REQUEST = ".request.json"
    RESULT = ".result.json"

    def __init__(self, workdir: AnyStr = None, request_fname: AnyStr = REQUEST):
        """
        :param workdir: Workspace directory
        """
        self.workdir = workdir or os.getcwd()
        self.response = OrderedDict()

        if self.workdir.find('/work/') > 1:
            path = self.workdir.replace('/work/', '/results/')
            if os.path.exists(path):
                self.workdir = path

        self.__load_request(request_fname)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.write_results()

    def __load_request(self, request_fname: AnyStr = REQUEST):
        """
        Import the CSIP request
        :param request_fname: The source file
        :return:
        """
        path = os.path.join(self.workdir, request_fname)
        if not os.path.exists(path):
            raise Exception("No request file found: " + path)

        with open(path) as fp:
            data = json.load(fp)

        self.csip = Client(data=data[Client.PARAMETER])

    def has_param(self, param):
        return self.csip.has_data(param)

    def get_param_unit(self, param):
        return self.csip.get_data_unit(param);

    def get_param_descr(self, param):
        return self.csip.get_data_description(param);

    def __get_param(self, param, def_value=None, typ=None):
        """
        Return the value of the parameter
        :param param: THe request parameter
        :param def_value: If the parameter is optional, then this is the default value
        :param typ: Type cast to apply if value is not a string
        :return: string
        """
        val = self.csip.get_data_value(param, def_value)
        if typ:
            try:
                val = typ(val)
            except TypeError:
                val = None
        return val

    def get_int_param(self, *args):
        """
        Apply type cast to get_param
        :param args:
        :return: int
        """
        return self.__get_param(*args, typ=int)

    def get_float_param(self, *args):
        """
        App.y float cast to value
        :param args:
        :return: float
        """
        return self.__get_param(*args, typ=float)

    def get_string_param(self, *args):
        """
        App.y float cast to value
        :param args:
        :return: string
        """
        return self.__get_param(*args, typ=str)

    def put_result(self, name, value, unit=None, descr=None):
        """
        Add value to result response
        :param name:
        :param value:
        :param unit:
        :param desc:
        :return:
        """
        self.response[name] = {
            Client.KEY_VALUE: value,
        }
        if unit:
            self.response[name][Client.KEY_UNIT] = unit
        if descr:
            self.response[name][Client.KEY_DESCRIPTION] = descr

    def write_results(self, result_fname: AnyStr = RESULT):
        """
        Write response object to disk.
        :return:
        """
        result = []
        for name, oparam in self.response.items():
            result.append({Client.KEY_NAME: name, **oparam})

        with open(os.path.join(self.workdir, result_fname), 'w') as f:
            json.dump({Client.RESULT: result}, f, indent=2)

        return result


if __name__ == '__main__':
    # test
    md = {
        "metainfo": {},
        "parameter": [{
            "name": "param1",
            "value": 23,
        }, {
            "name": "optparam1",
            "value": 25.6,
            "unit": 'F',
            "description": "optional",
        }]
    }

    test_dir = '/tmp/mds_test'
    if not os.path.exists(test_dir):
        #        shutil.rmtree(test_dir)
        os.makedirs(test_dir)

    request_path = os.path.join(test_dir, ModelDataService.REQUEST)
    with open(request_path, 'w') as req_fp:
        json.dump(md, req_fp, indent=2)

    mds = ModelDataService(test_dir)
    param1 = mds.get_int_param('param1')
    assert param1 == 23, "Failed to extract parameter, expected 23, got {0}".format(param1)
    optparam1 = mds.get_float_param('optparam1', 57)
    assert optparam1 == 25.6, "Failed to extract parameter with default value, expected 25.6, got {0}".format(optparam1)
    nonexistentparam = mds.get_int_param('nonexistentparam', 57)
    assert nonexistentparam == 57, "Failed to extract optional parameter, expected 57, got {0}".format(nonexistentparam)
    descr = mds.get_param_descr('optparam1')
    assert descr == 'optional', "Failed to extract optional description, got {0}".format(descr)
    unit = mds.get_param_unit('optparam1')
    assert unit == 'F', "Failed to extract optional unit, got {0}".format(unit)
    has = mds.has_param('optparam1')
    assert has == True, "Failed to check paramter, got {0}".format(has)

    # Write some results
    mds.put_result("result", 47)
    testunit = "someunit"
    mds.put_result("result_with_units", 45.55, testunit)
    testdesc = "a description for result_with_unit_and_desc"
    mds.put_result("result_with_units_and_desc", 33.33, "units!", testdesc)

    results = mds.write_results()
    assert results[0]['value'] == 47, "Failed to set result to 47"
    assert results[1]['unit'] == testunit, "Failed to set unit to {0}".format(testunit)
    assert results[2]['description'] == testdesc, "Failed to set description to {0}".format(testdesc)

    with open(os.path.join(test_dir, ModelDataService.RESULT)) as resp_fp:
        oresult = json.load(resp_fp)

    assert 'result' in oresult

    print("All tests passed...")

    with ModelDataService(test_dir) as s:
        p = s.get_int_param('param1')
        print(p)
        s.put_result("result", 147)
