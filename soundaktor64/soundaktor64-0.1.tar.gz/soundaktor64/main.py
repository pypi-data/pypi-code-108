import logging
import multiprocessing
import time
from time import sleep

import pkg_resources

from soundaktor64.silicon import get_temperature_subprocess
from soundaktor64.sound import Sound

CHECK_INTERVAL = 10
FAN_SOUND = pkg_resources.resource_filename(__name__, 'Laptop_Fan.mp3')
TEMP_VOLUMES = {
    # 45: 0.2,
    50: 0.3,
    55: 0.4,
    60: 0.5,
    65: 0.6,
    70: 0.7,
    75: 0.8,
    80: 0.9,
    85: 1.0,
}
TEMP_THRESHOLD = min(TEMP_VOLUMES.keys())
START_TIME = 2
END_TIME = 3 * 60 + 10
DURATION = 3 * 60 + 13

def get_cpu_temp_subprocess():
    start = time.time()
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=get_temperature_subprocess, args=(queue, ))
    process.start()
    process.join(timeout=5.0)
    logging.debug('Subprocess call took %.3f secs', time.time() - start)
    return queue.get()


def main():
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.DEBUG)

    sound = Sound(FAN_SOUND)

    playing = False
    time_since_last_check = CHECK_INTERVAL
    current_temp = 0
    volume = 0.0

    while True:
        if time_since_last_check >= CHECK_INTERVAL:
            current_temp = get_cpu_temp_subprocess()
            logging.info('Curent temperature is %.2f', current_temp)
            time_since_last_check = 0

        if current_temp >= TEMP_THRESHOLD:
            old_volume = volume
            volume = max(vol for temp, vol in TEMP_VOLUMES.items() if current_temp >= temp)
            if playing:
                if old_volume != volume:
                    sound.set_volume(volume)
                if sound.current_time >= END_TIME:
                    sound.set_time(START_TIME)
            else:
                sound.set_volume(volume)
                sound.set_time(0)
                sound.play()
                playing = True
        else:
            if playing:
                sound.set_time(END_TIME)
                sleep(DURATION - END_TIME + 1)
                time_since_last_check += DURATION - END_TIME + 1
                playing = False

        sleep(1.0)
        time_since_last_check += 1

if __name__ == '__main__':
    main()
