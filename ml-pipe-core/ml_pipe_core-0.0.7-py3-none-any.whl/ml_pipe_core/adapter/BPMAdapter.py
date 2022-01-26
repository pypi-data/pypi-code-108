import numpy as np
import time
import csv
from typing import Dict, Tuple

try:
    import PyTine as pt
except:
    pass

from ml_pipe_core.adapter.bpm_fit import correct_bpm
from ml_pipe_core.logger import logging


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class BPM:
    def __init__(self, bpm_type, path_to_calibr_file='src/ml_pipe_core/bpm_settings/bpm_settings'):
        calibr_file = path_to_calibr_file + '/common/'+bpm_type+'.par'
        colmat = np.loadtxt(calibr_file)
        self.cx = [r[0] for r in colmat]
        self.cy = [r[1] for r in colmat]

    def correct_x(self, x):
        x_ = 0.0
        for i in range(len(self.cx)):
            x_ += self.cx[i] * x**i
        return x_

    def correct_y(self, y):
        y_ = 0.0
        for i in range(len(self.cy)):
            y_ += self.cy[i] * y**i
        return y_


class BPMAdapter:
    def __init__(self, units='mm', path_to_calibr_file='src/ml_pipe_core/adapter/bpm_settings', path_to_constants_file='constants.csv'):
        self.bpm_names = ['bpm_swr_13', 'bpm_swr_31', 'bpm_swr_46', 'bpm_swr_61', 'bpm_swr_75', 'bpm_swr_90', 'bpm_swr_104', 'bpm_swr_118', 'bpm_swr_133', 'bpm_wl_140', 'bpm_wl_126', 'bpm_wl_111', 'bpm_wl_97', 'bpm_wl_82', 'bpm_wl_68', 'bpm_wl_53', 'bpm_wl_36', 'bpm_wl_30', 'bpm_wl_24', 'bpm_wl_18', 'bpm_wl_12', 'bpm_wl_6', 'bpm_wr_0', 'bpm_wr_7', 'bpm_wr_13', 'bpm_wr_19', 'bpm_wr_25', 'bpm_wr_31', 'bpm_wr_37', 'bpm_wr_56', 'bpm_wr_68', 'bpm_wr_82', 'bpm_wr_97', 'bpm_wr_111', 'bpm_wr_126', 'bpm_wr_140', 'bpm_nwl_133', 'bpm_nwl_118', 'bpm_nwl_104', 'bpm_nwl_90', 'bpm_nwl_75', 'bpm_nwl_61', 'bpm_nwl_46', 'bpm_nwl_31', 'bpm_nwl_13', 'bpm_nwl_1', 'bpm_nwr_13', 'bpm_nwr_31', 'bpm_nwr_46', 'bpm_nwr_61', 'bpm_nwr_75', 'bpm_nwr_90', 'bpm_nwr_104', 'bpm_nwr_118', 'bpm_nwr_133', 'bpm_nl_140', 'bpm_nl_126', 'bpm_nl_111', 'bpm_nl_97', 'bpm_nl_82', 'bpm_nl_68', 'bpm_nl_53', 'bpm_nl_36', 'bpm_nl_30', 'bpm_nl_24', 'bpm_nl_18', 'bpm_nl_12', 'bpm_nl_6', 'bpm_nr_0', 'bpm_nr_7', 'bpm_nr_13', 'bpm_nr_19', 'bpm_nr_25', 'bpm_nr_31', 'bpm_nr_37', 'bpm_nr_56', 'bpm_nr_62', 'bpm_nr_65', 'bpm_nr_69', 'bpm_nr_74', 'bpm_nr_79', 'bpm_nr_83', 'bpm_nr_87', 'bpm_nr_90', 'bpm_nr_96', 'bpm_nr_100', 'bpm_nr_104', 'bpm_nr_111', 'bpm_nr_126', 'bpm_nr_140', 'bpm_nol_133', 'bpm_nol_118', 'bpm_nol_104', 'bpm_nol_90', 'bpm_nol_75', 'bpm_nol_61', 'bpm_nol_46', 'bpm_nol_31', 'bpm_nol_10', 'bpm_nor_6', 'bpm_nor_11', 'bpm_nor_23', 'bpm_nor_32', 'bpm_nor_39', 'bpm_nor_40', 'bpm_nor_44', 'bpm_nor_47', 'bpm_nor_50', 'bpm_nor_52', 'bpm_nor_55', 'bpm_nor_58', 'bpm_nor_62', 'bpm_nor_63', 'bpm_nor_67', 'bpm_nor_70', 'bpm_nor_73', 'bpm_nor_78', 'bpm_nor_81', 'bpm_nor_85', 'bpm_nor_86', 'bpm_nor_90', 'bpm_nor_93', 'bpm_nor_96',
                          'bpm_nor_98', 'bpm_nor_101', 'bpm_nor_104', 'bpm_nor_108', 'bpm_nor_109', 'bpm_nor_113', 'bpm_nor_116', 'bpm_nor_119', 'bpm_nor_124', 'bpm_nor_127', 'bpm_nor_131', 'bpm_nor_132', 'bpm_ol_152', 'bpm_ol_149', 'bpm_ol_146', 'bpm_ol_144', 'bpm_ol_141', 'bpm_ol_138', 'bpm_ol_134', 'bpm_ol_133', 'bpm_ol_129', 'bpm_ol_126', 'bpm_ol_123', 'bpm_ol_118', 'bpm_ol_115', 'bpm_ol_111', 'bpm_ol_110', 'bpm_ol_106', 'bpm_ol_103', 'bpm_ol_100', 'bpm_ol_98', 'bpm_ol_95', 'bpm_ol_92', 'bpm_ol_88', 'bpm_ol_87', 'bpm_ol_83', 'bpm_ol_80', 'bpm_ol_77', 'bpm_ol_75', 'bpm_ol_72', 'bpm_ol_69', 'bpm_ol_65', 'bpm_ol_64', 'bpm_ol_60', 'bpm_ol_58', 'bpm_ol_48', 'bpm_ol_37', 'bpm_ol_24', 'bpm_ol_13', 'bpm_ol_0', 'bpm_or_8', 'bpm_or_17', 'bpm_or_22', 'bpm_or_26', 'bpm_or_32', 'bpm_or_37', 'bpm_or_44', 'bpm_or_53', 'bpm_or_62', 'bpm_or_65', 'bpm_or_69', 'bpm_or_74', 'bpm_or_79', 'bpm_or_83', 'bpm_or_87', 'bpm_or_90', 'bpm_or_96', 'bpm_or_100', 'bpm_or_104', 'bpm_or_111', 'bpm_or_126', 'bpm_or_140', 'bpm_sol_133', 'bpm_sol_118', 'bpm_sol_104', 'bpm_sol_90', 'bpm_sol_75', 'bpm_sol_61', 'bpm_sol_54', 'bpm_sol_46', 'bpm_sol_31', 'bpm_sol_13', 'bpm_sol_1', 'bpm_sor_13', 'bpm_sor_31', 'bpm_sor_46', 'BPM_SWR_13', 'bpm_sor_75', 'bpm_sor_90', 'bpm_sor_104', 'bpm_sor_118', 'bpm_sor_133', 'bpm_sl_140', 'bpm_sl_126', 'bpm_sl_111', 'bpm_sl_97', 'bpm_sl_82', 'bpm_sl_68', 'bpm_sl_53', 'bpm_sl_36', 'bpm_sl_24', 'bpm_sl_6', 'bpm_sr_6', 'bpm_sr_24', 'bpm_sr_36', 'bpm_sr_53', 'bpm_sr_68', 'bpm_sr_82', 'bpm_sr_97', 'bpm_sr_111', 'bpm_sr_126', 'bpm_sr_140', 'bpm_swl_133', 'bpm_swl_118', 'bpm_swl_104', 'bpm_swl_90', 'bpm_swl_75', 'bpm_swl_61', 'bpm_swl_46', 'bpm_swl_39', 'bpm_swl_31', 'bpm_swl_13', 'bpm_swl_1']
        self.bpm_names = [p.upper() for p in self.bpm_names]
        # self.bpm_names = [name for name in self.bpm_names if name not in ['BPM_NR_9','BPM_NOR_52','BPM_NOR_98','BPM_OL_144','BPM_OL_98', "BPM_OL_75", "BPM_OR_74", "BPM_NOR_104"]] # BPM_OR_74 was broken on 18.8.2021
        self.units = units
        scales = {'nm': 1, 'mum': 1e-3, 'mm': 1e-6, 'm': 1e-9}
        self.scale = scales[units]
        self.calibr_file_path = path_to_calibr_file

        # Constants to calculate the bpm beam current
        self.constants: Dict[str, Tuple[int, int]] = {}
        if path_to_constants_file:
            with open(path_to_constants_file) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.constants[row['name']] = (row['c0'], row['c1'])
            _logger.debug(f"Constants loaded: length {len(self.constants)}")

        with open(self.calibr_file_path + '/BPMsettings.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            devices = []
            bpm_types = []
            for row in reader:
                devices.append(row['Device'])
                bpm_types.append(row['BPMTYP'])

        self.bpm_info = {device: bpm_type for device, bpm_type in zip(devices, bpm_types)}

        self.load_calibration(set(bpm_types))

    def load_calibration(self, bpm_types):
        self.PQ = {}

        for bpm_t in bpm_types:
            bpm = BPM(bpm_t, path_to_calibr_file=self.calibr_file_path)
            self.PQ[bpm_t] = (bpm.cx, bpm.cy)

        return

    def get_names(self, start_with):
        start_i = self.bpm_names.index(start_with)
        names = self.bpm_names[start_i:]+self.bpm_names[:start_i]  # realign names to start from start_with
        return start_i, names

    def read(self, n_turns=10, start_with="BPM_SOR_61", is_corrected=True):
        start_i, names = self.get_names(start_with)

        res = np.zeros((len(names), n_turns, 2))

        for i, name in enumerate(names):
            for k in range(3):
                try:
                    res[i, :, 0] = np.array(pt.get(f'/PETRA/LBRENV/{name}/', 'DD_X', size=n_turns, mode='SYNC')['data'])
                    res[i, :, 1] = np.array(pt.get(f'/PETRA/LBRENV/{name}/', 'DD_Y', size=n_turns, mode='SYNC')['data'])
                    break
                except Exception as e:
                    print(f'attempt {k}:', e)
                    time.sleep(1)

        if is_corrected:
            res = self.correct(res, names)
        return res, names

    def read_sum(self, n_turns=10, start_with="BPM_SOR_61", is_corrected=True):
        start_i, names = self.get_names(start_with)

        res = np.zeros((len(names), n_turns, 1))

        for i, name in enumerate(names):
            for k in range(3):
                try:
                    res[i, :, 0] = np.array(pt.get(f'/PETRA/LBRENV/{name}/', 'DD_SUM', size=n_turns, mode='SYNC')['data'])
                    break
                except Exception as e:
                    print(f'attempt {k}:', e)
                    time.sleep(1)

        return res, names

    def correct(self, res, names, scale=1e-6):
        res *= scale
        print(res.shape)
        res_cor = np.empty_like(res)
        for i, name in enumerate(names):
            PQ = self.PQ[self.bpm_info[name]]
            x, y = correct_bpm(res[i, :, 0], res[i, :, 1], PQ[0], PQ[1])
            res_cor[i, :, 0] = x
            res_cor[i, :, 1] = y
        return res_cor/scale

    def get_reference(self, start_with="BPM_SOR_61"):
        # start_with = "BPM_SWR_13"
        name0 = self.bpm_names[0]
        x = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'SA_X')['data'])
        y = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'SA_Y')['data'])
        res = np.vstack((x, y)).T
        res = res[:-2]

        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0)*self.scale, names

    def get_offsets(self, start_with="BPM_SOR_61"):
        name0 = self.bpm_names[0]
        x = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'CORR_X_BBA')['data'])
        y = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'CORR_Y_BBA')['data'])
        res = np.vstack((x, y)).T
        res = res[:-2]

        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0)*self.scale, names

    def get_offsets_go(self, start_with="BPM_SOR_61"):
        name0 = self.bpm_names[0]
        # x = np.array(pt.get(f'/PETRA/REFORBIT/{name0}','SA_X')['data'])*self.scale
        x = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'CORR_X_BBAGO')['data'])
        y = np.array(pt.get(f'/PETRA/REFORBIT/{name0}', 'CORR_Y_BBAGO')['data'])
        res = np.vstack((x, y)).T
        res = res[:-2]
        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0)*self.scale, names

    def get_orbit(self, start_with="BPM_SOR_61"):
        name0 = self.bpm_names[0]
        # x = np.array(pt.get(f'/PETRA/REFORBIT/{name0}','SA_X')['data'])*self.scale
        x = np.array(pt.get(f'/PETRA/LBRENV/{name0}', 'SA_X')['data'])
        y = np.array(pt.get(f'/PETRA/LBRENV/{name0}', 'SA_Y')['data'])
        res = np.vstack((x, y)).T
        res = res[:-2]
        start_i, names = self.get_names(start_with)
        return np.roll(res, -start_i, axis=0)*self.scale, names

    def get_bpm_beam_currents(self, n_turns=10):
        if self.c0 == None or self.c1 == None:
            _logger.error(f"Constants c0, c1 are not set. c0={self.c0} and c1={self.c1}")
            return None, None
        sum_signal, names = self.read_sum(n_turns=n_turns)
        n_bpms = len(names)
        currents = np.zeros([n_bpms, n_turns])

        for i, name in enumerate(names):
            c0, c1 = self.constants.get(name)
            currents[i] = c0 + c1 * sum_signal[i, :, 0]
        return currents, names


if __name__ == "__main__":
    adapter = BPMAdapter()
    data, names = adapter.get_orbit()
