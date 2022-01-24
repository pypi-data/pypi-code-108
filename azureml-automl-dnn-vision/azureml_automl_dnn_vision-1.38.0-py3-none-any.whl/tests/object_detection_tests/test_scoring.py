import json
import os

from os import path
from pathlib import Path

import pytest
from azureml.core import Workspace, Experiment, Run
from pytest import approx

import azureml.automl.dnn.vision.common.utils as common_utils

from azureml.automl.dnn.vision.object_detection.writers.score_script import main

# Change these for different tests

subscription_id = "dbd697c3-ef40-488f-83e6-5ad4dfb78f9b"
resource_group = "raduko-image-tests"
workspace_name = "raduko-image-tests"

root_dir_path = "D:/images_datasets/kitti_single"
image_list_file_name = "kitti_val_sub_nocrowd_sample.json"

baseline_run_id = "od-shm-test_1593064081_4ecfb4a3"
experiment_name = "od-shm-test"


#################################

class TestScoring:
    """Utility class to check that scoring is not affected by some modifications to the code."""

    @staticmethod
    def offline_run_distill(run_id, exp_name):
        workspace = Workspace(subscription_id,
                              resource_group,
                              workspace_name)
        experiment = Experiment(workspace, exp_name)
        return Run(experiment=experiment, run_id=run_id)

    @staticmethod
    def extract_file_names(src_filename, dst_filename):
        with open(src_filename) as src_fp, open(dst_filename, 'w') as dst_fp:
            for line in src_fp:
                dst_fp.write(json.loads(line)["imageUrl"] + "\n")

    @pytest.mark.skip(reason="offline test only")
    def test_transform_in_dataloader_produces_same_result(self):
        tmp_output_dir = "out"
        Path(tmp_output_dir).mkdir(exist_ok=True)
        # overwrite the run distill so it works offline
        common_utils._distill_run_from_experiment = self.offline_run_distill

        root_dir = root_dir_path
        image_list_file_src = os.path.join(root_dir, image_list_file_name)
        image_list_file = os.path.join(root_dir, "image_list.txt")
        self.extract_file_names(image_list_file_src, image_list_file)

        training_run_id = baseline_run_id
        training_experiment_name = experiment_name

        # run predictions

        self.check_same_scores(image_list_file, root_dir, tmp_output_dir, training_experiment_name,
                               training_run_id)

    def check_same_scores(self, image_list_file, root_dir, tmp_output_dir, training_experiment_name,
                          training_run_id):
        # Create baseline
        predictions_file = 'predictions_od_baseline.txt'
        predictions_output_file = os.path.join(tmp_output_dir, predictions_file)
        if not os.path.exists(predictions_output_file):
            print("Baseline not found - recreating.")
            self.perform_scoring(image_list_file,
                                 predictions_output_file,
                                 root_dir,
                                 training_experiment_name,
                                 training_run_id)
        predictions_file_no_transform = 'predictions_od_no_transform_no_resize.txt'
        predictions_output_file_no_transform = os.path.join(tmp_output_dir, predictions_file_no_transform)
        self.perform_scoring(image_list_file,
                             predictions_output_file_no_transform,
                             root_dir,
                             training_experiment_name,
                             training_run_id)
        line_counter = 0
        box_counter = 0
        with open(predictions_output_file) as fp_baseline:
            with open(predictions_output_file_no_transform) as fp_no_transform:
                for line_baseline, line_no_transform in zip(fp_baseline, fp_no_transform):
                    line_counter += 1
                    baseline_json = json.loads(line_baseline)
                    no_transform_json = json.loads(line_no_transform)
                    assert baseline_json["filename"] == no_transform_json["filename"]
                    for baseline_box, no_transform_box in zip(baseline_json["boxes"], no_transform_json["boxes"]):
                        box_counter += 1
                        assert baseline_box["label"] == no_transform_box["label"]
                        assert baseline_box["score"] == approx(no_transform_box["score"], abs=1e-5)
                        assert baseline_box["box"]["topX"] == approx(no_transform_box["box"]["topX"], abs=1e-5)
                        assert baseline_box["box"]["topY"] == approx(no_transform_box["box"]["topY"], abs=1e-5)
                        assert baseline_box["box"]["bottomX"] == approx(no_transform_box["box"]["bottomX"], abs=1e-5)
                        assert baseline_box["box"]["bottomY"] == approx(no_transform_box["box"]["bottomY"], abs=1e-5)
        assert line_counter > 0
        assert box_counter > 0
        print("Output lines: {}".format(line_counter))
        assert path.exists(predictions_output_file)

    @staticmethod
    def perform_scoring(image_list_file, predictions_output_file, root_dir,
                        training_experiment_name, training_run_id):
        scoring_arguments = ['--run_id', training_run_id,
                             '--experiment_name', training_experiment_name,
                             '--output_file', predictions_output_file,
                             '--root_dir', root_dir,
                             '--image_list_file', image_list_file,
                             '--batch_size', '4']
        main(scoring_arguments)
