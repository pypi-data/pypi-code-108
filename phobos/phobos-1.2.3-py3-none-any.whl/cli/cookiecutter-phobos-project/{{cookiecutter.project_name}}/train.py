import os
import logging
import tarfile
import phobos

import torch
import torch.nn as nn
from torchvision import datasets, transforms

from torch.utils.data import Dataset

from polyaxon.tracking import Run

from phobos.loss import get_loss
from phobos.runner import Runner
from phobos.grain import Grain
from phobos.metrics import set_metric
from phobos.io import getDataLoaders, getWdsDistLoader

from models.model import Dummy

import torch.distributed as dist
import torch.utils.data.distributed


################### Polyaxon / Local ###################
"""
Initialization to use datalab or local system for training.
"""

experiment = None
if not Runner.local_testing():
    experiment = Run()


################### Polyaxon / Local ###################

################### Arguments ###################

"""Initialize all arguments passed via metadata.json
"""
grain_exp = Grain(polyaxon_exp=experiment)
args = grain_exp.parse_args_from_yaml('metadata.yaml')

################### Arguments ###################

############## Input & Output from Grain ###############

inputs, outputs = grain_exp.get_inputs_outputs()

logging.basicConfig(level=logging.WARNING)

########################################################


################### Setup Data and Weight ###################

if not Runner.local_testing():
    """
    When using datalab for training, we need to see how data is stored in datastore 
    and copy, untar, or pass url properly depending on how we use the datastore. 
    This will require a bit of effort in understanding the structure of the dataset, 
    like are train, val tarred together or are they different. Are we using webdataset
    shards, etc. We will eventually move to a unified framwork under webdataset-aistore
    for all dataset coming from Europa and all third party open-source datasets.
    """
    if not os.path.exists(args.local_artifacts_path):
        os.makedirs(args.local_artifacts_path)
    #tf = tarfile.open(os.path.join(args.nfs_data_path, 'train.tar.gz'))
    #tf.extractall(args.local_artifacts_path)
    #tf = tarfile.open(os.path.join(args.nfs_data_path, 'test.tar.gz'))
    #tf.extractall(args.local_artifacts_path)
    #args.dataset_dir = os.path.join(args.local_artifacts_path)

    # log code to artifact/code folder
    # code_path = os.path.join(experiment.get_artifacts_path(), 'code')
    # copytree('.', code_path, ignore=ignore_patterns('.*'))

    # set artifact/weight folder
    args.weight_dir = os.path.join(experiment.get_artifacts_path(), 'weights')

if not os.path.exists(args.weight_dir):
    os.makedirs(args.weight_dir)


################### Setup Data and Weight Directories ###################

transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

dataset_train = datasets.MNIST('data', train=True, download=True, transform=transform)
dataset_test = datasets.MNIST('data', train=False, download=True, transform=transform)

class DatasetM(Dataset):
    def __init__(self, data):
        super(DatasetM, self).__init__()
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        x, y = self.data.__getitem__(index)
        
        inputs = {'inp1': x}
        labels = {'out1': y}

        return inputs, labels


mnist_datasets = { 'train': DatasetM(dataset_train), 'val': DatasetM(dataset_test) }

loaders = getDataLoaders(
    datasets=mnist_datasets,
    batch_size=args.batch_size,
    num_workers=args.num_workers,
    distributed=args.distributed,
    load=args.load
)

'''
AIS webdataset eg,
def preproc(data):
    inp1 = data['x.pth']
    inp1 = torch.unsqueeze(inp1,0)

    out1 = data['y.cls']

    x = {'inp1': inp1}
    y = {'out1': out1}
    
    return x,y

urlmap = { 
    'train': 'http://aistore.granular.ai/v1/objects/test_ais/train/train-{0..4}.tar?provider=gcp',
    'val': 'http://aistore.granular.ai/v1/objects/test_ais/val/val-{0..4}.tar?provider=gcp',
}
transmap = {'train': preproc, 'val': preproc }

loaders = getWebDataLoaders(
    posixes=urlmap,
    transforms=transmap,
    shuffle=True,
    batch_size=args.batch_size,
    num_workers=args.num_workers,
    distributed=args.distributed,
)
'''

################### Intialize Model ###################
"""
Load Model then define other aspects of the model
"""

if args.model == 'dummy':
    """
    Make sure that all args that are passed to model class are passed
    via grain load_model functions. This allows us to later use the 
    arguments as it is during inference.
    """
    model = grain_exp.load_model(Dummy,
                                 n_channels=len(args.band_ids),
                                 n_classes=args.num_classes)

if args.pretrained_checkpoint:
    """
    If you have any pretrained weights that you want to load for the model, this 
    is the place to do it.
    """
    pretrained = torch.load(args.pretrained_checkpoint)
    model.load_state_dict(pretrained)

model = model.to(args.device)

if args.distributed:
    model = nn.parallel.DistributedDataParallel(model, find_unused_parameters=False)
elif args.num_gpus > 1:
    """Ad-hoc method to use gpu(s). We will be moving to DistributedParallel for all 
    datalab trainings.
    """
    model = nn.DataParallel(model, device_ids=list(range(args.num_gpus)))

if args.resume_checkpoint:
    """If we want to resume training from some checkpoints.
    """
    weight = torch.load(args.resume_checkpoint)
    model.load_state_dict(weight)

################### Intialize Model ###################

################### Intialize Runner ###################

runner = Runner(
    model=model,
    device=args.device,
    train_loader=loaders['train'],
    val_loader=loaders['val'], 
    inputs=inputs, 
    outputs=outputs, 
    optimizer=args.optimizer, 
    optimizer_args=args.optimizer_args,
    scheduler=args.scheduler,
    scheduler_args=args.scheduler_args,
    mode=args.mode,
    distributed=args.distributed,
    verbose=args.verbose,
    max_iters=args.max_iters,
    frequency=args.frequency, 
    tensorboard_logging=True, 
    polyaxon_exp=experiment
)

################### Intialize Runner ###################

################### Train ###################
"""Dice coeffiecient is used to select best model weights.
Use metric as you think is best for your problem.
"""

best_val = -1e5
best_metrics = None

logging.info('STARTING training')

for step, outputs in runner.trainer():
    if runner.master():
        print(f'step: {step}')
        outputs.print()

        val_recall = outputs.heads['1'].means['val_metrics']['recall']
        if val_recall > best_val:
            best_val = val_recall
            cpt_path = os.path.join(args.weight_dir,
                                    'checkpoint_epoch_'+ str(step) + '.pt')
            state_dict = model.module.state_dict() if runner.distributed \
                else model.state_dict()
            torch.save(state_dict, cpt_path)

################### Train ###################