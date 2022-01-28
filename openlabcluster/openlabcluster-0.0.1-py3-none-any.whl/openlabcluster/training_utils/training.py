"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import os
import wx
from pathlib import Path
from threading import Thread
from wx.lib.pubsub import pub
from openlabcluster.training_utils.util.logging import setup_logging
def return_train_network_path(config, shuffle=1, trainingsetindex=0, modelprefix=""):
    """ Returns the training and test pose config file names as well as the folder where the snapshot is
    Parameters
    ----------
    config : string
        Full path of the config.yaml file as a string.

    shuffle: int
        Integer value specifying the shuffle index to select for training.

    trainingsetindex: int, optional
        Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).

    Returns the triple: trainposeconfigfile, testposeconfigfile, snapshotfolder
    """
    from openlabcluster.utils import auxiliaryfunctions

    cfg = auxiliaryfunctions.read_config(config)
    modelfoldername = auxiliaryfunctions.GetModelFolder(
        cfg["TrainingFraction"][trainingsetindex], shuffle, cfg, modelprefix=modelprefix
    )
    trainposeconfigfile = Path(
        os.path.join(
            cfg["project_path"], str(modelfoldername), "train", "pose_cfg.yaml"
        )
    )
    testposeconfigfile = Path(
        os.path.join(cfg["project_path"], str(modelfoldername), "test", "pose_cfg.yaml")
    )
    snapshotfolder = Path(
        os.path.join(cfg["project_path"], str(modelfoldername), "train")
    )

    return trainposeconfigfile, testposeconfigfile, snapshotfolder

class train_network(Thread):
    def __init__(self, config, canvas,
    displayiters=None,
    saveiters=None,
    maxiters=None,
    continue_training=False,
    reducer_name = 'PCA',
    dimension=2,
    allow_growth=False,
    gputouse=None,
    autotune=False,
    keepdeconvweights=True,
    modelprefix=""):
        """Init Worker Thread Class."""
        Thread.__init__(self)

        self.canvas = canvas
        self.displayiters = displayiters
        self.maxiters = maxiters
        self.saveiters = saveiters
        # TF.reset_default_graph()
        start_path = os.getcwd()
        self.cfg =config
        self.stop_work_thread = 0
        self.continue_training = continue_training
        self.reducer_name = reducer_name
        self.dimension = dimension
        # Read file path for pose_config file. >> pass it on
        self.start()  # start the thread

    def run(self):
        import torch.nn as nn
        import torch
        import os
        import numpy as np
        from torch.utils.data import Dataset, SubsetRandomSampler
        from openlabcluster.utils import auxiliaryfunctions
        from torch import optim
        start_path = os.getcwd()
        print(self.cfg)
        os.chdir(
            str(Path(self.cfg).parents[0])
        )  # switch to folder of config_yaml (for logging)
        setup_logging()

        cfg = auxiliaryfunctions.read_config(self.cfg)  # load_config(config_yaml)
        num_class = cfg['num_class'][0]
        root_path = cfg["project_path"]
        batch_size = cfg['batch_size']
        model_name = cfg['tr_modelName']
        model_type = cfg['tr_modelType']
        import sys
        if len(cfg['train']) != 0:
            from openlabcluster.training_utils.ssl.data_loader import UnsupData, pad_collate_iter, get_data_paths
            dataset_train = UnsupData(get_data_paths(root_path, cfg['data_path'], cfg['train']))

            dataset_size_train = len(dataset_train)

            indices_train = list(range(dataset_size_train))

            random_seed = 11111

            np.random.seed(random_seed)
            np.random.shuffle(indices_train)

            print("training data length: %d" % (len(indices_train)))
            # seperate train and validation
            train_sampler = SubsetRandomSampler(indices_train)
            train_loader = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size,
                                                       sampler=train_sampler, collate_fn=pad_collate_iter)

        from openlabcluster.training_utils.ssl.SeqModel import seq2seq
        from openlabcluster.training_utils.ssl.seq_train import training

        fix_weight = cfg['fix_weight']
        fix_state = cfg['fix_state']
        teacher_force = cfg['teacher_force']
        phase = 'PC'
        if fix_weight:
            network = 'FW' + phase

        if fix_state:
            network = 'FS' + phase

        if not fix_state and not fix_weight:
            network = 'O' + phase

        # hyperparameter
        # global variable
        feature_length = cfg['feature_length']
        hidden_size = cfg['hidden_size']
        batch_size = cfg['batch_size']
        en_num_layers = cfg['en_num_layers']
        de_num_layers = cfg['de_num_layers']
        learning_rate = cfg['learning_rate']
        epoch = self.maxiters

        k = 2  # top k accuracy
        # for classification
        device = cfg['device']
        percentage = 1
        few_knn = False

        # initialize the model
        model = seq2seq(feature_length, hidden_size, feature_length, batch_size,
                        en_num_layers, de_num_layers, fix_state, fix_weight, teacher_force, device).to(device)

        with torch.no_grad():
            for child in list(model.children()):
                print(child)
                for param in list(child.parameters()):
                    if param.dim() == 2:
                        # nn.init.xavier_uniform_(param)
                        nn.init.uniform_(param, a=-0.05, b=0.05)

        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
        if model_type == 'seq2seq' and self.continue_training:
            if os.path.exists(model_name):
                from openlabcluster.training_utils.ssl.utilities import load_model
                model, optimizer = load_model(model_name, model, optimizer, device)

        loss_type = 'L1'  # 'L1'

        if loss_type == 'MSE':
            criterion_seq = nn.MSELoss(reduction='none')

        if loss_type == 'L1':
            criterion_seq = nn.L1Loss(reduction='none')

        criterion_cla = nn.CrossEntropyLoss(reduction='sum')

        past_acc = 10
        alpha = 0

        file_output = open(os.path.join(root_path, cfg['output_path'], '%sA%.2f_P%d_en%d_hid%d.txt' % (
            network, alpha, percentage * 100, en_num_layers, hidden_size)), 'w')
        model_prefix = os.path.join(root_path, cfg['model_path'], '%sA%.2f_P%d_en%d_hid%d' % (
            network, alpha, percentage * 100, en_num_layers, hidden_size))
        model_path = Path(model_prefix).parent
        pre = Path(model_prefix).name
        lambda1 = lambda ith_epoch: 0.95 ** (ith_epoch // 5)
        model_scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda1)
        past_loss = sys.float_info.max
        for ith_epoch in range(epoch):
            if self.stop_work_thread == 1:
                break
            past_loss, self.path_model =  training(ith_epoch, epoch, train_loader, self.displayiters, self.canvas,
                 model, optimizer, criterion_seq, criterion_cla, alpha, k, file_output, past_loss,model_path, pre,
                 hidden_size, model_prefix, num_class,
                 few_knn, device, self.reducer_name, self.dimension)
            model_scheduler.step()
            #wx.CallAfter(pub.sendMessage, "update", step=val)
            if ith_epoch % 50 == 0:
                filename = file_output.name
                file_output.close()
                file_output = open(filename, 'a')
            if self.path_model:
                auxiliaryfunctions.edit_config(self.cfg, {'tr_modelName':self.path_model, 'tr_modelType': 'seq2seq'})
            else:
                auxiliaryfunctions.edit_config(self.cfg, {'tr_modelType': 'seq2seq'})
        wx.CallAfter(pub.sendMessage, "finish")
        return

    def postTime(self, amt):
        """
        Send time to GUI
        """
        amtOfTime = (amt + 1) * 10
        pub().sendMessage("update", amtOfTime)

    def stop(self):
        self.stop_work_thread = 1

