
from pathlib import Path
from openlabcluster.utils import auxiliaryfunctions
from openlabcluster.training_utils.ssl.utilities import load_model
def selecting_samples(config_yaml, model_path, model_type, sample_method, label_per):

    import torch
    import os
    import numpy as np
    from torch.utils.data import Dataset, SubsetRandomSampler
    from openlabcluster.training_utils.ssl.extract_hidden import extract_hidden_ordered
    from torch import optim
    start_path = os.getcwd()
    os.chdir(
        str(Path(config_yaml).parents[0])
    )  # switch to folder of config_yaml (for logging)

    cfg = auxiliaryfunctions.read_config(config_yaml)  # load_config(config_yaml)
    root_path = cfg["project_path"]
    label_path = cfg['label_path']
    batch_size = cfg['batch_size']


    if len(cfg['train']) != 0:
        from openlabcluster.training_utils.ssl.data_loader import UnsupData, pad_collate_semi
        dataset_train = UnsupData(os.path.join(root_path, cfg['data_path'], cfg['train']))

    if len(cfg['test']) != 0:
        dataset_test = UnsupData(os.path.join(root_path, cfg['data_path'], cfg['test']))

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
                                                   sampler=train_sampler, collate_fn=pad_collate_semi)
        eval_loader = torch.utils.data.DataLoader(dataset_test, batch_size=batch_size,
                                                  sampler=valid_sampler, collate_fn=pad_collate_semi)

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
    epoch = cfg["multi_epoch"]
    labeled_id = cfg['labeled_id']
    k = 2  # top k accuracy
    # for classification
    device = cfg['device']
    few_knn = False
    # global variable
    cla_dim = cfg['cla_dim']  # 0 non labeled class


    # initialize the model

    print_every = 1
    if model_type == "seq2seq":
        alpha = 0
        model = seq2seq(feature_length, hidden_size, feature_length, batch_size,
                    en_num_layers, de_num_layers, fix_state, fix_weight, teacher_force, device).to(device)

    elif model_type == 'semi_seq2seq':
        alpha = 1
        cla_num_layers = len(cla_dim)
        model = SemiSeq2Seq(feature_length, hidden_size,feature_length, batch_size, cla_dim,
                 en_num_layers, de_num_layers, cla_num_layers,
                 fix_state, fix_weight, teacher_force, device).to(device)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    model,_ = load_model(model_path, model, optimizer, device)
    # model.seq = model_tmp
    if sample_method == 'ktop':
        from openlabcluster.training_utils.ssl.labelSampling import SampleFromCluster
        hi_train, label, label_train_semi, data_id = extract_hidden_ordered(
            model,dataset_train, alpha, device )
        ncluster = int(np.round(len(dataset_train.data_set)* label_per/100))
        from openlabcluster.training_utils.ssl.clustering_classification import remove_labeled_cluster, iter_kmeans_cluster
        if len(labeled_id)!=0:
            toLabel = np.load(labeled_id)
        else:
            toLabel = []
        hi_part, label_part, index_part = remove_labeled_cluster(hi_train, label, data_id, toLabel)
        train_id_list, dis_list, dis_list_prob, label_list = iter_kmeans_cluster(hi_part,  label_part,
                                                                                index_part,
                                                                                ncluster, beta=1)

        tmp = SampleFromCluster(train_id_list, dis_list, dis_list_prob, sample_method, label_per/100)
        file_list = [x for x in os.listdirlabel_path if os.path.isfile(x)]
        file_list = np.sort(file_list)
        import re
        last_id = re.findall(r'\d+', file_list[-1])
        np.save(os.path.join(label_path, "iteration%d.npy" %(int(last_id+1))), tmp)

    from sklearn.manifold import TSNE
    tran_data = TSNE(n_components=2).fit_transform(hi_train)

    return tran_data[0,:], tran_data[1,:], data_id, tmp