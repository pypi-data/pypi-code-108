import numpy as np
import mccd

path = '/Users/tliaudat/Documents/PhD/github/cosmostat_official/mccd/data/sim_inputs/train_positions.npy'
path_ccd = '/Users/tliaudat/Documents/PhD/github/cosmostat_official/mccd/data/sim_inputs/train_ccd_list.npy'
poss = np.load(path, allow_pickle=True)
ccdss = np.load(path_ccd, allow_pickle=True)

test_pos = poss[ccdss == 0.]
test_ccds = ccdss[ccdss == 0.]
ccd_id = 0

config_file_path = '''/Users/tliaudat/Documents/PhD/github/cosmostat_official/mccd/tests/hidden_tests/test_config_MCCD.ini'''

mccd_instance = mccd.auxiliary_fun.RunMCCD(config_file_path,
                                           fits_table_pos=1)

mccd_model_path = '/Users/tliaudat/Documents/PhD/github/cosmostat_official/mccd/tests/hidden_tests/outputs/fitted_model-2086592.npy'
local_pos = True

rec_PSFs = mccd_instance.recover_MCCD_PSFs(mccd_model_path,
                                           positions=test_pos,
                                           ccd_id=ccd_id,
                                           local_pos=local_pos)

print('Good bye!')
