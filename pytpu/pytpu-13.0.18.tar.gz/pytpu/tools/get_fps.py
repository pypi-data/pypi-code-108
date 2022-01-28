# pylint: disable=E0611,C0103,R0914,W1514,R1735,R1734,C0206

import asyncio
from typing import Dict, List
from time import time
from zipfile import ZipFile
import tempfile
import json
import os
# import shutil

import numpy as np
from ..pytpu import TPUDevice, TPUProgram, TPUInference, TPUProgramInfo, ProcessingMode  # type: ignore
# from ..tools.helpers import to_raw
from ..tools.helpers import STR_TO_DTYPE
from ..tools.helpers import get_tpu_devices

__all__ = [
    'get_fps',
]


async def run_inference(name: str, device: TPUDevice, inference: TPUInference,
                        data_list: List[Dict[str, np.ndarray]], raw: bool = False) -> None:

    mode = ProcessingMode.FULL
    if raw:
        mode = ProcessingMode.RAW

    for ii, data in enumerate(data_list):
        inference.load(data, mode=mode)
        status = await device.load_inference(inference)
        assert status.is_success
        inference.get(as_dict=True, mode=mode)

        if (ii + 1) % 10 == 0:
            print(f'{name}: finish {ii + 1} iteration')


def get_fps(program_path: str, raw: bool = False, n_queries: int = 100, n_proc: int = 4) -> float:

    print(f'Start measure performance for program: {program_path}')
    print(f'Configuration: RAW = {raw}; queries = {n_queries}; processes = {n_proc}')

    tpu_device_names = get_tpu_devices()

    with tempfile.TemporaryDirectory() as tempdir:
        with ZipFile(program_path, 'r') as zip_obj:
            zip_obj.extractall(tempdir)

        with open(os.path.join(tempdir, 'metadata.json'), 'r') as metadata_file:
            metadata = json.load(metadata_file)

        # if raw is True:
        #     with open(os.path.join(tempdir, 'metadata.json'), 'w') as metadata_file:
        #         metadata = to_raw(metadata)
        #         json.dump(metadata, metadata_file)
        #
        #     with tempfile.NamedTemporaryFile() as temp_file:
        #         program_path = os.path.join(tempdir, 'program_raw.tpu')
        #         shutil.make_archive(temp_file.name, 'zip', tempdir)
        #         os.rename(temp_file.name + '.zip', program_path)
        #
        #     print(f'Raw program saved to {program_path}')

        layers_param = dict()
        for _, region in metadata['inputs'].items():
            for name, inp in region.items():
                layers_param[inp['anchor']] = inp

        data_list = list()
        for _ in range(n_queries):
            for name in layers_param:
                if raw:
                    data_shape = layers_param[name]['tpu_shape']
                    data_type = STR_TO_DTYPE[layers_param[name]['tpu_dtype']]
                else:
                    data_shape = layers_param[name]['user_shape']
                    data_type = STR_TO_DTYPE[layers_param[name]['user_dtype']]

                generated_data = (np.random.rand(*data_shape) * 2 - 1) * 100

                if raw:
                    generated_data = generated_data.astype(data_type).tobytes()
                else:
                    generated_data = generated_data.astype(data_type)

                generated_data_dict = {name: generated_data}
                data_list.append(generated_data_dict)

        # input_name = list(layers_param.keys())[0]
        # program_name = os.path.basename(program_path)[:-4]
        # root_dir = os.path.dirname(program_path)
        # with open(os.path.join(root_dir, program_name + '_input.bin'), 'w') as f:
        #     data_list[0][input_name].tofile(f)

        batch = max([layers_param[name]['user_shape'][0] for name in layers_param])

        inference_processes = list()
        # tpu_device_names = ['/dev/tpu0', ]
        device_num = len(tpu_device_names)
        tpu_devices = list()
        for dev_ii, device_name in enumerate(tpu_device_names):
            tpu_devices.append(TPUDevice.open(device_name))
            # device = TPUDevice()
            tpu_program = TPUProgram(program_path, TPUProgramInfo(max_tasks_count=n_proc))
            tpu_devices[dev_ii].load_program(tpu_program)
            inferences = [TPUInference(tpu_program) for _ in range(n_proc)]
            inference_processes.extend([run_inference(f'Device {device_name} process {ii}', tpu_devices[dev_ii],
                                                      inferences[ii],
                                                      data_list[ii:len(data_list):n_proc * device_num], raw)
                                        for ii in range(n_proc)])

        start_time = time()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*inference_processes))
        total_inference_time = time() - start_time

        fps = n_queries * batch / total_inference_time

        print(f'Estimated FPS = {fps}')

    return fps
