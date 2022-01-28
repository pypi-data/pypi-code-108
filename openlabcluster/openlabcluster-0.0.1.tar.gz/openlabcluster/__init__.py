"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import os

# Suppress tensorflow warning messages
# import tensorflow as tf
#
# vers = (tf.__version__).split(".")
# if int(vers[0]) == 1 and int(vers[1]) > 12:
#     TF = tf.compat.v1  # behaves differently before 1.13
# else:
#     TF = tf

#TF.logging.set_verbosity(TF.logging.ERROR)
DEBUG = True and "DEBUG" in os.environ and os.environ["DEBUG"]
from openlabcluster import DEBUG

# DLClight version does not support GUIs. Importing accordingly
import matplotlib as mpl

if os.environ.get("DLClight", default=False) == "True":
    print(
        "DLC loaded in light mode; you cannot use any GUI (labeling, relabeling and standalone GUI)"
    )
    mpl.use(
        "AGG"
    )  # anti-grain geometry engine #https://matplotlib.org/faq/usage_faq.html
else:  # standard use [wxpython supported]
    mpl.use("WxAgg")
    # from openlabcluster import generate_training_dataset
    # from openlabcluster import refine_training_dataset
    # from openlabcluster.generate_training_dataset import (
    #     label_frames,
    #     dropannotationfileentriesduetodeletedimages,
    #     comparevideolistsanddatafolders,
    #     dropimagesduetolackofannotation,
    # )
    # from openlabcluster.generate_training_dataset import (
    #     multiple_individuals_labeling_toolbox,
    # )
    # from openlabcluster.generate_training_dataset import (
    #     adddatasetstovideolistandviceversa,
    #     dropduplicatesinannotatinfiles,
    # )
    from openlabcluster.gui.launch_script import launch_dlc

    # from openlabcluster.refine_training_dataset import refine_labels
    # from openlabcluster.utils import select_crop_parameters
    # from openlabcluster.utils.skeleton import SkeletonBuilder
    # from openlabcluster.refine_training_dataset.tracklets import refine_tracklets

#
from openlabcluster.create_project import (
    create_new_project,
    # create_new_project_3d,
    # add_new_videos,
    # load_demo_data,
)
# from openlabcluster.create_project import (
#     create_pretrained_project,
#     create_pretrained_human_project,
# )
# from openlabcluster.generate_training_dataset import extract_frames
# from openlabcluster.generate_training_dataset import (
#     check_labels,
#     create_training_dataset,
#     mergeandsplit,
# )
# from openlabcluster.generate_training_dataset import (
#     create_training_model_comparison,
#     cropimagesandlabels,
# )
# from openlabcluster.generate_training_dataset import create_multianimaltraining_dataset
# from openlabcluster.utils import (
#     create_labeled_video,
#     create_video_with_all_detections,
#     plot_trajectories,
#     auxiliaryfunctions,
# )
# from openlabcluster.utils import (
#     convert2_maDLC,
#     convertcsv2h5,
#     convertannotationdata_fromwindows2unixstyle,
# )
# from openlabcluster.utils import analyze_videos_converth5_to_csv, auxfun_videos
#
# from openlabcluster.utils.auxfun_videos import ShortenVideo, DownSampleVideo, CropVideo


# Train, evaluate & predict functions / all require TF
from openlabcluster.training_utils import (
    train_network,
    return_train_network_path,
)
# from openlabcluster.training_utils import (
#     evaluate_network,
#     return_evaluate_network_data,
#     evaluate_multianimal_crossvalidate,
# )
#
# from openlabcluster.training_utils import (
#     analyze_videos,
#     analyze_time_lapse_frames,
#     convert_detections2tracklets,
# )
# from openlabcluster.training_utils import (
#     extract_maps,
#     visualize_scoremaps,
#     visualize_locrefs,
#     visualize_paf,
#     extract_save_all_maps,
# )
# from openlabcluster.training_utils import export_model

# from openlabcluster.pose_estimation_3d import (
#     calibrate_cameras,
#     check_undistortion,
#     triangulate,
#     create_labeled_video_3d,
# )
#
# from openlabcluster.refine_training_dataset.tracklets import convert_raw_tracks_to_h5
# from openlabcluster.refine_training_dataset import extract_outlier_frames, merge_datasets
# from openlabcluster.post_processing import filterpredictions, analyzeskeleton


from openlabcluster.version import __version__, VERSION
