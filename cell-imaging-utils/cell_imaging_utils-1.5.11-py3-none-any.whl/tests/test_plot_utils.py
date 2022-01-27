import os
import logging
import numpy as np

from cell_imaging_utils.plots.plot_utils import PlotsUtils
from cell_imaging_utils.image.image_utils import ImageUtils

log = logging.getLogger(__name__)
results_save_dir = "{}\\tests\\results".format(os.getcwd())
images_save_dir = "{}\\tests\\images".format(os.getcwd())

organelle_name = "Endoplasmic-reticulum"
# organelle_name = "Golgi"
# organelle_name = "Microtubules"
# organelle_name = "Lysosome"
# organelle_name =  "Tight-junctions"
# organelle_name = "Mitochondria"
image_file_name_1 = "0_prediction_c0..tif"
# image_file_name_2 = "0_signal.tif" #"0_prediction_c0..tif"
# image_file_name_2 = "0_target.tif"
image_file_name_2 = "0_seg.tif"
# result_fig = "signal_target_slice31.png"
result_fig = "seg_prediction_slice31.png"
# seg_image_file_name = "image_list_test.csv"

if not os.path.exists(results_save_dir):
    os.makedirs(results_save_dir)

def test_plot_utils() -> None:
    
    image1 = ImageUtils.imread("{}\\{}\\{}".format(images_save_dir,organelle_name,image_file_name_1))
    image2 = ImageUtils.imread("{}\\{}\\{}".format(images_save_dir,organelle_name,image_file_name_2))
    # print(ImageUtils.get_channel_names(image))
    image1_ndarray = ImageUtils.normalize(ImageUtils.image_to_ndarray(image1),max_value=255,dtype=np.double)
    image2_ndarray = ImageUtils.normalize(ImageUtils.image_to_ndarray(image2),max_value=255,dtype=np.double)
    diff_image = np.abs(image1_ndarray - image2_ndarray)
    diff_image = ImageUtils.normalize(diff_image,max_value=255,dtype=np.double)
    diff_image = np.clip(diff_image,0,100)
    PlotsUtils.plot_image_heatmap(diff_image[0,31,:,:], organelle_name,"x","y",save="{}\\{}_{}".format(results_save_dir,organelle_name,result_fig))
    # # image1_ndarray = np.clip(image1_ndarray,50,150)
    # PlotsUtils.plot_image_heatmap(image1_ndarray[0,30,:,:], organelle_name,"x","y")
    # # image2_ndarray = np.clip(image2_ndarray,50,150)
    # PlotsUtils.plot_image_heatmap(image2_ndarray[0,30,:,:], organelle_name,"x","y")
    return None


test_plot_utils()