import os
import logging

from cell_imaging_utils.datasets_metadata.table.datasetes_metadata_csv import DatasetMetadataSCV
from cell_imaging_utils.datasets_metadata.dict.datasetes_metadata_pickle import DatasetMetadataPickle
from cell_imaging_utils.image.image_utils import ImageUtils

log = logging.getLogger(__name__)
csvs_save_dir = "{}\\tests\\csvs".format(os.getcwd())
pickle_save_dir = "{}\\tests\\pickles".format(os.getcwd())
results_save_dir = "{}\\tests\\results".format(os.getcwd())


organelle_name = "Nuclear_envelop"
train_file_name = "image_list_train.csv"
test_file_name = "image_list_test.csv"
pickle_file_name = "bestResults.p"

if not os.path.exists(results_save_dir):
    os.makedirs(results_save_dir)

def test_datasets_metadata() -> None:
    image_list_train = DatasetMetadataSCV("{}\\{}\\{}".format(csvs_save_dir,organelle_name,train_file_name),"{}\\{}\\{}".format(csvs_save_dir,organelle_name,train_file_name))
    seg_image_list_train = DatasetMetadataSCV("{}\\{}_{}".format(results_save_dir,organelle_name,train_file_name))
    pickle_best_res = DatasetMetadataPickle("{}\\{}\\{}".format(pickle_save_dir,organelle_name,train_file_name),"{}\\{}".format(pickle_save_dir,pickle_file_name))
    print(pickle_best_res.get_data())
    print(seg_image_list_train.get_data())
    
    seg_image_list_train.create_header(["a","b","c"])
    seg_image_list_train.add_row([1,2,3])
    seg_image_list_train.create()
    
    return None


test_datasets_metadata()