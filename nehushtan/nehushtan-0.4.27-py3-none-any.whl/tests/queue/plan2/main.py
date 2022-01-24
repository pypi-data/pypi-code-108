import shutil

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from tests.queue.plan2.Test2NehushtanQueue import Test2NehushtanQueue
from tests.queue.plan2.Test2NehushtanQueueDelegate import Test2NehushtanQueueDelegate
from tests.queue.plan2.Test2NehushtanQueueTaskDelegate import Test2NehushtanQueueTaskDelegate

if __name__ == '__main__':
    shutil.rmtree('/Users/leqee/code/nehushtan/log/queue-plan2')

    config_dictionary = {}
    logger = NehushtanFileLogger('loop', '/Users/leqee/code/nehushtan/log/queue-plan2')
    delegate = Test2NehushtanQueueDelegate(config_dictionary, logger)
    task_delegate = Test2NehushtanQueueTaskDelegate(config_dictionary, logger)

    Test2NehushtanQueue(delegate, task_delegate).loop()
