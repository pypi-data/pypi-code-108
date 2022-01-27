# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import argparse
import torch
import os


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model_output_dir", help="model output directory", required=True
    )

    for i in range(1, 11):
        input_name = "--model_input_dir_" + str(i)
        parser.add_argument(
            input_name, type=str, required=i <= 2
        )  # only the first two inputs are required

    parser.add_argument("--num_models", type=int, required=True)
    parser.add_argument("--weights", type=str, required=False)
    parser.add_argument(
        "--model_name", type=str, required=False, default="pytorch_model.bin"
    )

    args, unknown = parser.parse_known_args()
    return args


def main(args):
    if args.weights:
        weights = [float(i) for i in args.weights.split(",")]
        try:
            assert sum(weights) == 1.0
        except AssertionError as e:
            print("SystemLog: the sum of weights is unequal to 1.")
            raise
        try:
            assert len(weights) == args.num_models
        except AssertionError as e:
            print(
                "SystemLog: the number of weights does not match with the number of input models."
            )
            raise
    else:
        weights = 1 / args.num_models

    models = []
    for i in range(args.num_models):
        input_name = "model_input_dir_" + str(i + 1)
        input_path = vars(args)[input_name]
        if os.path.isdir(input_path):
            input_path = os.path.join(input_path, args.model_name)
        models.append(torch.load(input_path, map_location=torch.device("cpu")))

    agg_model = models[0].copy()
    for k, v in agg_model.items():
        if ".embeddings." in k or "encoder.layer.0." in k or "encoder.layer.1." in k:
            # for freezed layers, not change it
            continue
        agg_model[k] = agg_model[k] * 0
        for i in range(args.num_models):
            agg_model[k] = agg_model[k] + models[i][k] * weights[i]

    output_path_to_agg_model = os.path.join(args.model_output_dir, args.model_name)
    torch.save(agg_model, output_path_to_agg_model)
    del agg_model


if __name__ == "__main__":
    print("SystemLog: start parsing args")
    try:
        args = get_args()
    except:
        print("SystemLog: got error when parsing args!")
    print("SystemLog: done get args, parsed args are: {}".format(args))
    try:
        main(args)
    except Exception as e:
        print("SystemLog: got error when running main(args), error message: " + str(e))
