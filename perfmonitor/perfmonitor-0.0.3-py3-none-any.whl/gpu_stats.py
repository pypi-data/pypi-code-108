from typing import Tuple

import xmltodict
import subprocess
import time


def get_data() -> dict:
    """
    Parse nvidia-smi output.
    """
    return xmltodict.parse(
        subprocess.Popen("nvidia-smi -q -x", shell=True, stdout=subprocess.PIPE).communicate()[0].decode("utf8",
                                                                                                         "ignore"))


def get_gpu_state() -> Tuple[dict, float]:
    t = time.time()
    try:
        data = get_data()['nvidia_smi_log']
    except:
        return None, None

    gpu = data['gpu']

    temp = gpu['temperature']['gpu_temp']
    slow_temp = gpu['temperature']['gpu_temp_slow_threshold']
    max_temp = gpu['temperature']['gpu_temp_max_threshold']

    (total_mem, used_mem,
     free_mem) = gpu['fb_memory_usage']['total'], gpu['fb_memory_usage']['used'], gpu['fb_memory_usage']['free']

    gpu_usage, memory_usage = gpu['utilization']['gpu_util'], gpu['utilization']['memory_util']
    encoder_usage, decoder_usage = gpu['utilization']['encoder_util'], gpu['utilization']['decoder_util']

    # processes = gpu['processes']['process_info']
    power_draw = gpu['power_readings']['power_draw']

    return {
        "temperature": temp,
        "gpu_usage": gpu_usage,
        "power_draw": power_draw,
        "slow_temp": slow_temp,
        "max_temp": max_temp,
        "memory_usage": memory_usage,
        "decoder_usage": decoder_usage,
        "encoder_usage": encoder_usage,
        "total_mem": total_mem,
        "used_mem": used_mem,
        "free_mem": free_mem
    }, time.time() - t


def main():
    v, _ = get_gpu_state()[0]
    print(v)


if __name__ == '__main__':
    main()
