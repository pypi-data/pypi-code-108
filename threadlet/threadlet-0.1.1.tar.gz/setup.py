# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['threadlet']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'threadlet',
    'version': '0.1.1',
    'description': 'Improved `Thread` and `ThreadPoolExecutor` classes.',
    'long_description': '# Threadlet\n\nImproved `Thread` and `ThreadPoolExecutor` classes.\n\n---\n\n### Installation\n`pip3 install threadlet`\n\n### Features\n\n- Threads with results:\n\n```python\nfrom threadlet.thread import Thread\n\n# threads now have "future" attribute of type concurrent.futures.Future.\n# usage:\nthread = Thread(target=sum, args=([1, 1],))\nthread.start()\ntry:\n    assert thread.future.result(1) == 2\nfinally:\n    thread.join()  # pay attention that "future" attribute won\'t be available after joining\n    # thread.future.result(1) #  raises AttributeError\n\n# equals to:\nwith Thread(target=sum, args=([1, 1],)) as thread:\n    assert thread.future.result(1) == 2\n\n# equals to:\nwith Thread.submit(sum, [1, 1]) as thread:\n    assert thread.future.result(1) == 2\n```\n\n- ThreadPoolExecutor with improved workers performance (fixed IDLE semaphore) and new features:\n```python\nimport time\nimport threading\nfrom threadlet.executor import ThreadPoolExecutor\n\nMAX_WORKERS = 4\nMIN_WORKERS = 2\nWORK_TIME = 0.5\nIDLE_TIMEOUT = 1\n\n# "idle_timeout" argument:\n# workers now are going to die after not doing any work for "idle_timeout" time.\nwith ThreadPoolExecutor(MAX_WORKERS, idle_timeout=IDLE_TIMEOUT) as tpe:\n    assert threading.active_count() == 1\n    for _ in range(2):\n        for _ in range(MAX_WORKERS):\n            tpe.submit(time.sleep, WORK_TIME)\n        assert threading.active_count() == MAX_WORKERS + 1\n        time.sleep(WORK_TIME + IDLE_TIMEOUT + 1)  # wait until workers die on timeout\n        assert threading.active_count() == 1\n\n# "min_workers" argument:\n# this amount of workers are pre-created at start and not going to die ever in despite of "idle_timeout".\nwith ThreadPoolExecutor(MAX_WORKERS, min_workers=MIN_WORKERS, idle_timeout=IDLE_TIMEOUT) as tpe:\n    assert threading.active_count() == MIN_WORKERS + 1\n    for _ in range(MAX_WORKERS):\n        tpe.submit(time.sleep, WORK_TIME)\n    assert threading.active_count() == MAX_WORKERS + 1\n    time.sleep(WORK_TIME + MIN_WORKERS + 1)  # wait until workers die on timeout\n    assert threading.active_count() == MIN_WORKERS + 1\n```\n\n---\n\n- Free software: MIT license\n',
    'author': 'Andrii Kuzmin',
    'author_email': 'jack.cvr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
