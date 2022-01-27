import os
import time
from threading import Event

from rox.core.configuration.configuration_fetched_invoker import FetcherStatus
from rox.core.utils.time_utils import now_in_unix_milliseconds
from rox.server.flags.rox_flag import RoxFlag
from rox.server.rox_options import RoxOptions
from rox.server.rox_server import Rox


class Container:
    def __init__(self):
        self.flag1 = RoxFlag()
        self.flag2 = RoxFlag()
        self.flag3 = RoxFlag()


class FixedUsersScene:
    def __init__(self, container):
        self.container = container
        self.api_key = '5bec37714f2a1832ff559377'
        self.dev_key = '3692fc437794dff9b68cafca'

    def run(self):
        print('run')
        now = now_in_unix_milliseconds()
        ms_in_hour = 60 * 60 * 1000
        for i in range(167, -1, -1):
            current_time = now - ms_in_hour * i
            os.environ['rox.analytics.ms'] = str(current_time)
            print('running batch %d' % i)
            self.run_batch()

    def run_batch(self):
        for i in range(0, 3):
            for user in range(0, 100):
                if i == 2 and user == 0:
                    continue

                flag = self.get_flag(i)
                context = {'userId': str(user)}
                value = flag.is_enabled(context)
                print('Checking flag %s is %s' % (flag.name, value))
            time.sleep(0.001)  # Release GIL to get time to other threads.

    def get_flag(self, curr_val):
        if curr_val % 3 == 0:
            return self.container.flag1

        if curr_val % 3 == 1:
            return self.container.flag2

        return self.container.flag3


def main():
    container = Container()
    scene = FixedUsersScene(container)
    os.environ['ROLLOUT_MODE'] = 'QA'
    Rox.register(container)

    is_running = {'value': False}
    run_event = Event()

    def configuration_fetched_handler(e):
        if not is_running['value'] and e.fetcher_status == FetcherStatus.APPLIED_FROM_NETWORK:
            is_running['value'] = True
            scene.run()
            run_event.set()

    options = RoxOptions(dev_mode_key=scene.dev_key, configuration_fetched_handler=configuration_fetched_handler)

    Rox.set_custom_string_property('rox.distinct_id', lambda context: context['userId'])
    cancel_event = Rox.setup(scene.api_key, options).result()
    run_event.wait()
    cancel_event.set()
    print('Hello World!')


if __name__ == '__main__':
    main()
