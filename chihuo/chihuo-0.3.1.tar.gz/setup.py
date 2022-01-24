# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chihuo']

package_data = \
{'': ['*']}

install_requires = \
['lodis-py>=0.2.2,<0.3.0']

setup_kwargs = {
    'name': 'chihuo',
    'version': '0.3.1',
    'description': 'chihuo: An Asynchronous Task Running Engine',
    'long_description': '# chihuo: An Asynchronous Task Running Engine\n\nchihuo is an asynchronous task running engine. It runs asynchronous tasks concurrently\nfrom a queue which can be at memory, Redis, Lodis or Some MQ.\n\n## The Loop\n\n`ChihuoLoop` is the asynchronous engine core which responses to connect the backend queue\nand distributes every tasks to the global event loop.\n\nFor a process, the chihuo create only one global event loop to run all asynchronous\ntasks and the loop is running forever.\n\n- `ChihuoLoop.start` method\n\n  When a `ChihuoLoop` starts, it needs to add some primary tasks to the backend queue.\n  The `start` function is the place to fire these priorities.\n\n- `ChihuoLoop.add_task` method\n\n  At anywhere and anytime, we can use the `add_task` method to add a task to backend queue.\n  The task discription must be the tuple as `(task_id: str, task_info: jsonifiable object_)`\n  e.g. `add_task(("task1", [1, 1+10]), ("task2", [2, 2+10]))`\n\n- `ChihuoLoop.make_task` method\n\n  Each classes which have implemented the `ChihuoLoop` class must to implement the `make_task`\n  method for receiving the task\'s information that is added by `ChihuoLoop.add_task` to\n  the backend queue.\n\n- `ChihuoLoop.task_finish` method\n\n  When a task is finished and is unneeded at future, we can tag the task as the `finished` state\n  using the `task_finish` method. e.g. `task_finish(task_id)`. The task that is at `finished`\n  state can\'t be add to backend queue again.\n\n- `ChihuoLoop.task_unfinish` method\n\n  When a task is at the `finished` state and we need to add it to queue again, we can use\n  the `task_unfinish` method to set the task state to `unfinish`. Then, we can use\n  `ChihuoLoop.add_task` to add the task to queue again.\n\n- `ChihuoLoop.stop` property\n\n  When the property `stop` to be set as True, the `ChihuoLoop` will stop pull the tasks from\n  queue and exit.\n\n## Demo\n\n```python\n# filename: abc.py\n\nfrom chihuo import ChihuoLoop\nfrom chihuo.common import SERVER_DEFAULT_CONFIG_PATH\nimport chihuo\n\n\nclass MyTasksA(ChihuoLoop):\n\n    NAME = "my-tasksA"  # The unique id for backend queue server\n    CONCURRENCY = 10   # The number of tasks running concurrently\n    SERVER_CONFIG = SERVER_DEFAULT_CONFIG_PATH\n\n    def __init__(self):\n        super().__init__()\n\n    async def start(self):\n        for id in range(10):\n            await self.add_task((str(i), {i ** 2}))\n\n    async def make_task(self, task_id, task):\n        print(f"my-task-A: {task_id}")\n        print(f"power of {i} is {task}")\n\n        # Talk chihuo that the task is finished\n        await self.task_finish(i)\n\n\nclass MyTasksB(ChihuoLoop):\n\n    NAME = "my-tasksB"  # The unique id for the loop\n    CONCURRENCY = 10   # The number of tasks running concurrently\n    SERVER_CONFIG = SERVER_DEFAULT_CONFIG_PATH\n\n    def __init__(self):\n        super().__init__()\n\n    async def start(self):\n        for id in range(10):\n            await self.add_task((str(i), {i ** 2}))\n\n    async def make_task(self, task_id, task):\n        print(f"my-task-B: {task_id}")\n        print(f"power of {i} is {task}")\n\n        # Talk chihuo that the task is finished\n        await self.task_finish(i)\n\n\nif __name__ == \'__main__\':\n    chihuo.run(MyTasksA, MyTasksB)\n```\n\nTo Run the project, firstly we need to launch a backend queue server.\nHere, we use a Lodis instance as default server.\n\nStart a Lodis server:\n\n```\nLODIS_DB_PATH=/data/test-lodis LODIS_IP_PORT="127.0.0.1:8311" nohup /path/to/lodis &\n```\n\nThen, we write a configure file as `./server.json` (the `SERVER_DEFAULT_CONFIG_PATH`)\nto connect the backend for our `MyTasksA` and `MyTasksB`.\n\n```\nbackend=lodis\nip=127.0.0.1\nport=8311\n```\n\nNow, we can run the script.\n\n```\npython3 abc.py\n```\n\n## Shutdown the Tasks\n\nDefaultly, the global loop is running forever and we need to shutdown the loop by sending\na `INT (interrupt)` signal to the process. After the process received The `INT` signal, it will\nset the property `stop` of instance which is implemented from `ChihuoLoop` to True and the\ninstance will stop all running tasks and send them back to queue, finally exit.\n',
    'author': 'PeterDing',
    'author_email': 'dfhayst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PeterDing/chihuo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
