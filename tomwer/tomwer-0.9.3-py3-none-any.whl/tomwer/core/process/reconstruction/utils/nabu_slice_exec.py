from nabu.pipeline.fullfield.chunked_cuda import CudaChunkedPipeline
from nabu.pipeline.fullfield.processconfig import ProcessConfig


def launch_reconstruction(config_file, slice_index):
    proc = ProcessConfig(config_file)
    worker_process = CudaChunkedPipeline(
        proc, sub_region=(None, None, slice_index, slice_index + 1)
    )
    worker_process.process_chunk()
