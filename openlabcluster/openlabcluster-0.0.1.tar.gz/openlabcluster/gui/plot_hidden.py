
import argparse
from pathlib import Path
import torch.nn as nn

from openlabcluster.utils import auxiliaryfunctions

from openlabcluster.training_utils.util.logging import setup_logging
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import umap
DIMENSION_REDUCTION_DICT = {'PCA': PCA, 'tSNE': TSNE, 'UMAP':umap.UMAP}
class extract_hid():
    def __init__(self, config_yaml, dimension, reducer_name, model_name=None, model_type = None):
        from openlabcluster.training_utils.ssl.utilities import load_model
        import torch
        import os
        from torch.utils.data import Dataset
        from torch import optim
        os.chdir(
            str(Path(config_yaml).parents[0])
        )  # switch to folder of config_yaml (for logging)
        setup_logging()

        cfg = auxiliaryfunctions.read_config(config_yaml)#load_config(config_yaml)
        root_path = cfg["project_path"]
        batch_size = cfg['batch_size']
        #if not model_type:
        model_type = cfg['tr_modelType']
        #if not model_name:
        model_name = cfg['tr_modelName']

        label_path = os.path.join(cfg['project_path'],cfg['label_path'], 'label.npy')
        if not os.path.exists(label_path):
            label_path = None

        if len(cfg['train'])!=0:
            from openlabcluster.training_utils.ssl.data_loader import SupDataset, pad_collate_iter
            dataset_train = SupDataset(root_path, cfg['data_path'], cfg['train'], label_path)

        dataset_size_train = len(dataset_train)
        self.dataset_size_train = dataset_size_train

        indices_train = list(range(dataset_size_train))
        print("training data length: %d" % (len(indices_train)))
        # seperate train and validation
        train_loader = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size,
                                                   shuffle=False, collate_fn=pad_collate_iter)
        from openlabcluster.training_utils.ssl.SeqModel import seq2seq, SemiSeq2Seq

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
        feature_length = cfg['feature_length']
        hidden_size = cfg['hidden_size']
        batch_size = cfg['batch_size']
        en_num_layers = cfg['en_num_layers']
        de_num_layers = cfg['de_num_layers']
        cla_num_layers = cfg['cla_num_layers']
        learning_rate = cfg['learning_rate']
        device = cfg['device']

        # global variable
        cla_dim = cfg['cla_dim']  # 0 non labeled class
        self.num_class = cla_dim[-1]

        # initialize the model
        if model_type == 'seq2seq' or not model_type:
            model = seq2seq(feature_length, hidden_size, feature_length, batch_size,
                        en_num_layers, de_num_layers, fix_state, fix_weight, teacher_force, device).to(device)
            alpha= 0
        elif model_type == 'semi_seq2seq':
            model = SemiSeq2Seq(feature_length, hidden_size, feature_length, batch_size,
                                cla_dim, en_num_layers, de_num_layers, cla_num_layers, fix_state, fix_weight, teacher_force, device).to(device)
            alpha = 0.5
        with torch.no_grad():
            for child in list(model.children()):
                print(child)
                for param in list(child.parameters()):
                    if param.dim() == 2:
                        # nn.init.xavier_uniform_(param)
                        nn.init.uniform_(param, a=-0.05, b=0.05)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
        if model_name:
            if os.path.exists(model_name):
                model, _ = load_model(model_name, model, optimizer, device)

        from openlabcluster.training_utils.ssl.extract_hidden import extract_hidden_ordered
        hidd = extract_hidden_ordered(model, train_loader, hidden_size, alpha, device)
        self.hidarray = hidd[0]

        dim_reducer = DIMENSION_REDUCTION_DICT[reducer_name]
        if dimension == '2d':
            reducer = dim_reducer(n_components=2)
        else:
            reducer = dim_reducer(n_components=3)
        self.transformed = reducer.fit_transform(self.hidarray)
        self.semilabel = hidd[2]
        self.gt_label = hidd[1]
        if alpha!=0:
            self.pred_label = hidd[-2]
            self.mi = hidd[-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to yaml configuration file.")
    cli_args = parser.parse_args()

