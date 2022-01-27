# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from . import interfaces
from .. import InterpolationParameter


class InterpolationRepositoryError(Exception):
    pass


class InterpolationParameterRepository(interfaces.InterpolationParameterRepository):

    def __init__(self, model_config):
        self.params = model_config.interpolation_parameters()
        self.interp_param_as_attr = {'precipitation': {'idw': 'precipitation'},
                              'radiation': {'idw': 'radiation'},
                              'wind_speed': {'idw': 'wind_speed'},
                              'relative_humidity': {'idw': 'rel_hum'},
                              'temperature': {'idw': 'temperature_idw',
                                              'btk': 'temperature'},
                              }

    def get_parameters(self, interpolation_id):
        interp_param = InterpolationParameter()
        for var, val in self.params.items():
            method, param_dct = val['method'], val['params']
            if method not in self.interp_param_as_attr[var].keys():
                raise InterpolationRepositoryError(
                    'Unknown interpolation method {} for {} source.'.format(method, var))
            param_as_attr = self.interp_param_as_attr[var][method]
            sub_param = getattr(interp_param, param_as_attr)
            for p, v in param_dct.items():
                if hasattr(sub_param, p):
                    setattr(sub_param, p, v)
                else:
                    raise InterpolationRepositoryError(
                        "Invalid parameter '{}' for '{}' interpolation using method '{}'".format(
                            p, var, method))
        if self.params['temperature']['method'] == 'idw':
            interp_param.use_idw_for_temperature = True
        return interp_param
