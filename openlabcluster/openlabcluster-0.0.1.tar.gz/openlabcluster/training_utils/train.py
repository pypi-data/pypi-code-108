"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

Adapted from DeeperCut by Eldar Insafutdinov
https://github.com/eldar/pose-tensorflow

"""
import argparse

from pathlib import Path
import torch.nn as nn
from openlabcluster.utils import auxiliaryfunctions



class LearningRate(object):
    def __init__(self, cfg):
        self.steps = cfg.multi_step
        self.current_step = 0

    def get_lr(self, iteration):
        lr = self.steps[self.current_step][0]
        if iteration == self.steps[self.current_step][1]:
            self.current_step += 1

        return lr


def load_and_enqueue(sess, enqueue_op, coord, dataset, placeholders):
    while not coord.should_stop():
        batch_np = dataset.next_batch()
        food = {pl: batch_np[name] for (name, pl) in placeholders.items()}
        sess.run(enqueue_op, feed_dict=food)

def train(
    config_yaml,
    canvas,
    displayiters,
    saveiters,
    maxiters,
    max_to_keep=5,
    keepdeconvweights=True,
    allow_growth=False,
):
    import torch
    import os
    import  numpy as np
    from torch.utils.data import Dataset, SubsetRandomSampler

    from torch import optim
    start_path = os.getcwd()
    os.chdir(
        str(Path(config_yaml).parents[0])
    )  # switch to folder of config_yaml (for logging)


    cfg = auxiliaryfunctions.read_config(config_yaml)#load_config(config_yaml)
    num_class= cfg['num_class'][0]
    root_path = cfg["project_path"]
    batch_size = cfg['batch_size']
    # if (
    #     cfg.dataset_type == "scalecrop"
    #     or cfg.dataset_type == "tensorpack"
    #     or cfg.dataset_type == "deterministic"
    # ) and cfg["batch_size"] != 1:
    #     print(
    #         "Switching batchsize to 1, as the tensorpack/ scalecrop/ deterministic loader does not support batches >1. Use imgaug/default loader for larger batch sizes."
    #     )
    #     cfg["batch_size"] = 1  # in case this was edited for analysis.-
    if len(cfg['train'])!=0:
        from openlabcluster.training_utils.ssl.data_loader import UnsupData, pad_collate_iter
        dataset_train = UnsupData(os.path.join(root_path,cfg['data_path'], cfg['train']))



    if len(cfg['test'])!=0:
        dataset_test = UnsupData(os.path.join(root_path,cfg['data_path'], cfg['test']))

        dataset_size_train = len(dataset_train)
        dataset_size_test = len(dataset_test)

        indices_train = list(range(dataset_size_train))
        indices_test = list(range(dataset_size_test))

        random_seed = 11111

        np.random.seed(random_seed)
        np.random.shuffle(indices_train)
        np.random.shuffle(indices_test)

        print("training data length: %d, validation data length: %d" % (len(indices_train), len(indices_test)))
        # seperate train and validation
        train_sampler = SubsetRandomSampler(indices_train)
        valid_sampler = SubsetRandomSampler(indices_test)
        train_loader = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size,
                                                   sampler=train_sampler, collate_fn=pad_collate_iter)
        eval_loader = torch.utils.data.DataLoader(dataset_test, batch_size=batch_size,
                                                  sampler=valid_sampler, collate_fn=pad_collate_iter)

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
    feature_length = cfg['feature_length']
    hidden_size = cfg['hidden_size']
    batch_size = cfg['batch_size']
    en_num_layers = cfg['en_num_layers']
    de_num_layers = cfg['de_num_layers']
    cla_num_layers = cfg['cla_num_layers']
    learning_rate = cfg['learning_rate']
    epoch = cfg["multi_epoch"]

    k = 2  # top k accuracy
    # for classification
    device = cfg['device']
    percentage =1
    few_knn = False
    # global variable
    cla_dim = cfg['cla_dim']  # 0 non labeled class


    print_every = 1

    model = seq2seq(feature_length, hidden_size, feature_length, batch_size,
                    en_num_layers, de_num_layers, fix_state, fix_weight, teacher_force).to(device)


    with torch.no_grad():
        for child in list(model.children()):
            print(child)
            for param in list(child.parameters()):
                if param.dim() == 2:
                    # nn.init.xavier_uniform_(param)
                    nn.init.uniform_(param, a=-0.05, b=0.05)

    # model_name = './seq2seq_model/'+ 'FSfewPCA0.0000_P100_layer3_hid1024_epoch30' #'FSfewCVrandomA0.0000_P50_layer3_hid1024_epoch16'  ##'FScvA0.0000_P100_layer3_hid1024_epoch4'#'FScvnewA0.0000_P100_layer3_hid1024_epoch1'#'test1_FWA0.0000_P100_layer3_hid1024_epoch255'
    # optimizer_tmp = optim.Adam(filter(lambda p: p.requires_grad, model_tmp.parameters()), lr=learning_rate)
    # # #
    # model_tmp,_ = load_model(model_name, model_tmp, optimizer_tmp, device)
    # model.seq = model_tmp
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)

    loss_type = 'L1'  # 'L1'

    if loss_type == 'MSE':
        criterion_seq = nn.MSELoss(reduction='none')

    if loss_type == 'L1':
        criterion_seq = nn.L1Loss(reduction='none')

    criterion_cla = nn.CrossEntropyLoss(reduction='sum')

    past_acc = 10
    alpha = 0

    file_output = open(os.path.join(root_path,cfg['output_path'], '%sA%.2f_P%d_en%d_hid%d.txt' % (
        network, alpha, percentage * 100, en_num_layers, hidden_size)), 'w')
    model_prefix= os.path.join(root_path, cfg['model_path'],'%sA%.2f_P%d_en%d_hid%d' % (
        network, alpha, percentage * 100, en_num_layers, hidden_size))
    training(epoch, train_loader, eval_loader, print_every, canvas,
             model, optimizer, criterion_seq, criterion_cla, alpha, k, file_output, past_acc,
             root_path, network, percentage, en_num_layers, hidden_size, model_prefix, num_class,
             few_knn, device)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to yaml configuration file.")
    cli_args = parser.parse_args()

    train(Path(cli_args.config).resolve())
