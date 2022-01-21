# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastack_celery']

package_data = \
{'': ['*']}

install_requires = \
['celery>=5.2.3,<6.0.0', 'fastack>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'fastack-celery',
    'version': '0.1.0',
    'description': 'Celery Integration For Fastack',
    'long_description': '# fastack-celery\n\nSimple package to integrate celery with fastack.\n\n## To-do\n\nThere are several to-do lists for the future\n\n- [ ] See [#1](https://github.com/fastack-dev/fastack-celery/issues/1)\n\n## Installation\n\n```\npip install fastack-celery\n```\n\n## Usage\n\n### Create celery app\n\nCopy the code below and put it in `app/main.py`:\n\n```py\nfrom fastack_celery import make_celery\ncelery = make_celery(app)\n```\n\nYou can also pass parameters to the celery app.\n\n### Configuration\n\nFor celery configuration, you can create it via `Celery` class in your app settings. For example:\n\n```py\n# app/settings/local.py\nclass Celery:\n    broker_url = "amqp://strong_user:strong_password@localhost:5672/celery_vhost"\n    result_backend = "redis://localhost:6900/0"\n```\n\nFor other celery configurations, see here https://docs.celeryproject.org/en/stable/userguide/configuration.html#new-lowercase-settings\n\n### Create a task\n\nYou can create tasks using the `shared_task` decorator:\n\n```py\n# app/tasks.py\n\n# Sample task from examples/celery/app/tasks.py\n@shared_task\ndef counter_task(id: int):\n    session = db.open()\n    with session.begin():\n        obj: Counter = session.query(Counter).where(Counter.id == id).first()\n        if obj:\n            print(f"start counting #{id}")\n            obj.counter += 1\n            state = obj.state\n            if state is None or state == Counter.State.NOT_IN_QUEUE:\n                obj.state = Counter.State.NOT_IN_QUEUE\n            elif state == Counter.State.TERMINATED:\n                task_id = obj.task_id  # or current_task.request.id\n                celery.control.revoke(task_id, terminate=True)\n                obj.task_id = None\n            else:\n                obj.state = Counter.State.IN_QUEUE\n                counter_task.apply_async(args=(id,), countdown=1, task_id=obj.task_id)\n\n            obj.save(session)\n\n        else:\n            print(f"Object with id #{id} not found")\n```\n\nBy default, all tasks must be stored in `app/tasks.py` which will be automatically imported by the `make_celery` function.\n\n### Running celery workers\n\n```\ncd your-project\ncelery -A app.main:celery worker -l info\n```\n',
    'author': 'aprilahijriyan',
    'author_email': 'hijriyan23@gmail.com',
    'maintainer': 'aprilahijriyan',
    'maintainer_email': '37798612+aprilahijriyan@users.noreply.github.com',
    'url': 'https://github.com/fastack-dev/fastack-celery',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
