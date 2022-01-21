import os
from pathlib import Path
import cv2
import numpy as np
import torch
from torchvision import models, transforms
from torch import nn
from torch.utils.data import Dataset
import wandb
import random
import sklearn.metrics
import yaml

path_to_config = "config/config_vhh_od.yaml"
batchsize = 8
std = 55.7495 / 255
mean = 87.2851 / 255

fp = open(path_to_config, 'r')
config = yaml.load(fp, Loader=yaml.BaseLoader)
used_classes = config['OdCore']['CLASSES_FOR_CLASSIFIER']
n_classes = len(used_classes)

transform_normalize = transforms.Normalize(mean=[mean, mean, mean], std=[std, std, std])

test_transform =  transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((224,224)),
        transforms.Grayscale(num_output_channels=3),
        # Normalization from our data:
        transform_normalize,
    ])

def class_to_idx(class_name):
    return used_classes.index(class_name)

def idx_to_class(idx):
    return used_classes[idx]

def get_class_distribution(dataset):
    samples = [0 for i in used_classes]
    for i, sample in enumerate(dataset):
        label = sample["class"]
        samples[label] += 1

    print([float(i) for i in samples])
    return [float(i)/len(dataset) for i in samples]

def output_to_prediction(outputs):
    return [np.argmax(outputs[i]) for i in range(outputs.shape[0])]

def get_metrics(outputs, labels, do_class_metrics = False):
    precision, recall, f1, _ = sklearn.metrics.precision_recall_fscore_support(labels, outputs, average="macro")
    metrics = {"macro_prec": precision, "macro_rec": recall, "macro_f1": f1}

    if do_class_metrics:
        for label in range(n_classes):
            precision, recall, f1, _ = sklearn.metrics.precision_recall_fscore_support(labels, outputs, average="macro", labels = [label])
            metrics["prec ({0})".format( idx_to_class(label))] = precision
            metrics["rec ({0})".format(idx_to_class(label))] = recall
            metrics["f1 ({0})".format(idx_to_class(label))] = f1

    nr_correct_predictions = sum([1 for i in range(len(outputs)) if outputs[i] == labels[i]])
    accuracy = float(nr_correct_predictions) / len(outputs)
    metrics["accuracy"] = accuracy
    return metrics

class Classifier():
    """
    Classifies an image of a person
    """
    def __init__(self, model_name, path_to_weights, device):
        self.model = ClassifierModel(model_name)
        self.model.load_state_dict(torch.load(path_to_weights))
        self.device = device
        self.model.to(device)

    def inference(self, crops):
        """
        Takes a batch of (unprocessed) crops and classifies them
        """
        self.model.eval()
        with torch.no_grad():
            crops = crops.to(self.device)
            outputs = self.model(crops).cpu().detach().numpy()
            class_idx = output_to_prediction(outputs)
            class_names = [idx_to_class(idx) for idx in class_idx]
        return class_names, class_idx

    def to(self, device):
        self.model.to(device)
        self.device = device

    def inference_from_img(self, img):
        """
        Takes a batch of (unprocessed) crops and returns scores
        """
        return self.inference(img)
    

class ClassifierModel(nn.Module):
    """
    A wrapper around a pretrained classifier model
    Classifies a batch of crops according to used_classes
    """

    def __init__(self, model_name):
        super(ClassifierModel, self).__init__()

        if model_name == "densenet121":
            self.model = models.densenet121(pretrained=True)
            num_ftrs = self.model.classifier.in_features
            self.model.classifier = nn.Linear(num_ftrs, n_classes)
        elif model_name == "vgg11":
            self.model = models.vgg11(pretrained=True)
            num_ftrs = self.model.classifier[6].in_features
            self.model.classifier[6] = nn.Linear(num_ftrs,n_classes)
        elif model_name == "vgg16":
            self.model = models.vgg16(pretrained=True)
            num_ftrs = self.model.classifier[6].in_features
            self.model.classifier[6] = nn.Linear(num_ftrs,n_classes)
        elif model_name == "wide_resnet50_2":
            self.model = models.wide_resnet50_2(pretrained=True)
            self.model.fc = nn.Linear(2048, n_classes)
        self.input_size = 224

    def forward(self, x):
        return self.model(x)

class PersonsDataset(Dataset):
    def __init__(self, img_folder, shuffle=True, transforms = None, dropFilesFrom = None):
        """
        Args:
            img_folder (string): The folder containing the class folders
            dropFilesFrom (list of tuples (string, int)): 
                Can be used to downsample or upsample data. 
                [("corpse", 5)] would mean that only every fifth image from the corpse folder would be used.
                [("corpse", 5), ("soldier", -3)] means the same as above and that every image from the soldier folder will be used three times. 
        """
        self.img_folder = img_folder
        self.transform = transforms

        self.data = []


        do_drop_classes = dropFilesFrom is not None
        if do_drop_classes:
            dropped_classes, acceptance_mod = list(zip(*dropFilesFrom))
            print(dropped_classes, acceptance_mod)


        # Load data
        for directory in os.listdir(img_folder):
            if directory in used_classes:
                for i, path in enumerate(Path(os.path.join(img_folder, directory)).rglob('*.png')):
                    # Up and downsampling
                    if do_drop_classes and directory in dropped_classes:
                        acceptance = acceptance_mod[dropped_classes.index(directory)] 
                        # Drop samples if acceptance > 0 (downsampling)
                        if acceptance > 0 and i % acceptance != 0:
                            continue
                        # Import samples multiple times if acceptance < 0 (upsampling)
                        elif acceptance < 0:
                            for j in range(int(-acceptance)):
                                self.data.append((str(path), class_to_idx(directory)))

                    self.data.append((str(path), class_to_idx(directory)))

        # Shuffle
        if shuffle:
            np.random.shuffle(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.data[idx][0]
        img_class = self.data[idx][1]
        img =  cv2.imread(img_path)
        np_img = np.asarray(img)

        if self.transform:
            np_img = self.transform(np_img)

        return {"image": np_img, "class": img_class}

def evaluate(dataloader, name, epoch, device, model, criterion, do_class_metrics = False):
    model.eval()
    with torch.no_grad():
        curr_loss = 0
        predictions_train = []
        labels_train = []
        for batch in dataloader:
            inputs = batch["image"].to(device)
            labels = batch["class"].to(device)
            outputs = model(inputs)

            labels_train += labels.cpu().detach().numpy().tolist()
            predictions_train += output_to_prediction(outputs.cpu().detach().numpy())

            loss = criterion(outputs, labels)
            curr_loss += loss.cpu().item()

        metrics = get_metrics(predictions_train, labels_train, do_class_metrics=do_class_metrics)
        curr_loss = curr_loss / len(dataloader)
        metrics["total_loss"] = curr_loss
        print("\t{0} loss: {1}\n\t{0} accuracy: {2}".format(name, curr_loss, metrics["accuracy"]))
        return metrics


class obj_list_loader:
    """
    This is a generator that allows you to loop through custom_objects and images
    """

    def __init__(self, custom_obj_list, relevant_frames):
        self.custom_obj_list = custom_obj_list
        self.relevant_frames = relevant_frames

    def loop(self):
        crops = None
        indices = []

        curr_frame = -1
        curr_frame_id = -1

        # Indices of objects in which persons appear
        for i, obj in enumerate(self.custom_obj_list):

            # None means that we did not find predictions for this frame
            if obj is None:
                curr_frame += 1
                continue

            # If an object is from a new frame then increase our frame counter
            if obj.fid > curr_frame_id:
                    curr_frame += 1
                    curr_frame_id = obj.fid

            if obj.object_class_name == "person":
                rel_image = self.relevant_frames[curr_frame]

                # Sometimes OD predicts boundary boxes with coordinates < 0, cannot crop those so ignore them
                if(obj.bb_y1 < 0) or (obj.bb_y2 < 0) or (obj.bb_x1 < 0) or (obj.bb_x2 < 0) or (obj.bb_y2 <= obj.bb_y1) or (obj.bb_x2 <= obj.bb_x1) \
                or (obj.bb_y2 >= rel_image.shape[0]) or (obj.bb_x2 >= rel_image.shape[1]):
                    continue
                
                indices.append(i)
                image = rel_image[obj.bb_y1:obj.bb_y2, obj.bb_x1:obj.bb_x2]
                image = test_transform(image)

                # Add a new dimenions in front on which we will append the different images
                image = torch.unsqueeze(image, 0)

                if crops is not None:
                    crops = torch.cat((crops, image), 0)
                else:
                    crops = image
            else:
                continue

            if len(indices) == batchsize:
                yield crops, indices
                crops = None
                indices = []
        yield crops, indices




def run_classifier_on_list_of_custom_objects(classifier, custom_obj_list, relevant_frames):
    generator = obj_list_loader(custom_obj_list, relevant_frames)

    for crops, indices in generator.loop():
        # No crops means nothing to classify
        if crops is None:
            return

        crops = torch.split(crops, batchsize, dim=0)
        idx = 0
        for batch in crops:
            class_names, _ = classifier.inference_from_img(batch)
            
            for class_name in class_names:
                custom_obj_list[indices[idx]].add_person_classification(class_name)
                idx += 1
