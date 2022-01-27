# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eventy',
 'eventy.config',
 'eventy.config.aiohttp',
 'eventy.config.celery',
 'eventy.config.django',
 'eventy.config.sanic',
 'eventy.integration',
 'eventy.logging',
 'eventy.messaging',
 'eventy.record',
 'eventy.serialization',
 'eventy.trace_id']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15', 'contextvars>=2', 'semver>=2']

extras_require = \
{'aiohttp': ['aiohttp>=1'],
 'avro': ['PyYAML>=5', 'avro-python3>=1'],
 'celery': ['celery>=5'],
 'confluent-kafka': ['confluent-kafka>=1.7'],
 'django': ['django>=1'],
 'requests': ['requests'],
 'sanic': ['sanic>=18']}

setup_kwargs = {
    'name': 'eventy',
    'version': '3.1.27',
    'description': 'Qotto/eventy',
    'long_description': "# Eventy\n\n* Source: [Eventy on GitLab](https://gitlab.com/qotto/oss/eventy)\n* Package: [Eventy on Pypi](https://pypi.org/project/eventy/)\n* Documentation: [Eventy API documentation](https://qotto.gitlab.io/oss/eventy/)\n\n## What is Eventy?\n\nEventy is both a protocol and a library for making the design of fault-tolerant, event-driven, concurrent and\ndistributed applications in a microservices-oriented architecture easier.\n\nAs a protocol, Eventy is language-agnostic.\n\nHowever, the reference implementation is written in Python. Whatever is your programming language, you can use Eventy.\nIf you are using Python, you will be able to make the most of it quicker.\n\n## Motivation\n\nThe reality is, a distributed, microservices-oriented architecture is a bit hard to make right.\n\nMartin Fowler even [ended up stating](https://www.drdobbs.com/errant-architectures/184414966):\n\n> First Law of Distributed Object Design: “don't distribute your objects”.\n\nHe later [detailed his view](https://martinfowler.com/articles/distributed-objects-microservices.html) of the First Law\nregarding microservices.\n\nAs Martin Folwer points out, inherently microservices come with their undeniable advantages and a few companies use them\nwith great success. The only reason why a lot of people end up struggling with microservices, is because it greatly\nincreases the complexity of the whole system, which makes it harder to get it right.\n\nEventy is adressing exactly that issue — providing you with a reliable framework to make microservices work for you.\n\nA big part of the design process to create Eventy was to understand different use cases and see how the design can be\nsimplified. For instance, not only does Eventy offer state partitionning for free, it actually comes up with a few\nstratagies that eliminate the need to persist state altogether.\n\n## Inspiration\n\n[Kafka Streams](https://kafka.apache.org/documentation/streams/) was a great influence in making\nEventy. [Celery](http://www.celeryproject.org/) and [Faust](https://github.com/robinhood/faust) are also worth to be\nlooked at if you are looking for an opiniated framework easy to get started with.\n\nHowever, these frameworks only partially solve all the issues you will have with microservices. And, in our opinion,\nthese frameworks are not suitable for designing large critical systems.\n\nThey're both opinanated, and therefore cannot be easily integrated in your existing software. You will have to build\nyour software around the framework, instead of the other way around. They also don't give you the full control on the\nway you can use them: you can only use them as a whole, or not at all.\n\n## What Eventy can do for you\n\nEventy implements multiple features, but all of them simply solve two main problems:\n\n* How to make services communicate with each other\n* How to access and persist state\n\nWith Eventy, you can serialize data the way you want. You can use [Avro](https://avro.apache.org/)\n, [JSON](https://www.json.org/), [gRPC](https://grpc.io/), or whatever customer serializer you like.\n\nWith Eventy, you can use any system you like as a persistency layer, as long as it supports transactions, if you need\nstrong processing guarantees. The most obvious choice is to use [Apache Kafka](https://kafka.apache.org/), but\npersisting messages over [PostgreSQL](https://www.postgresql.org/) is completely feasable, too.\n\nEventy was destined with the mindset of a library of related but independently usable components - and not a framework:\nthe behaviour is explicit and you're the one in charge: you can design your software your own way.\n\nThis explicit behaviour, albeit requiring more boilerplate, gives you better clarity on what is happening. Recipes and\nexamples are provided so that you can understand how to use Eventy for most use cases.\n\nYou're free to use any part of Eventy as well. Even if you end up not using the Eventy protocol at all, simply reading\nthe documentation and understanding the issues that are adressed and how they are adressed can help you to get on the\nright path.\n\n## Main components of Eventy\n\n* a **well-defined communication protocol** for sending various types of persisted messages, called _Records_: _Events_\n  , _Requests_ and _Responses_\n* **persistency of _Records_** that can be stored forever, which lets you keep track of all the changes in your system (\n  especially useful for audits and business analytics)\n* **queues** so that _Records_ can be processed asynchroneously, and aren't lost even if your system is down or\n  overloaded\n* **strong processing guarantees**: a Record can be designed to be processed _at least once_, _at most once_ and _\n  exactly once_ even if your system encounters a process or network failure at any point\n* **self-propagating _Contexts_** that in many cases entirely eliminate the need of persisting state\n* **partitionned state persistency** so that you no longer have a single point of failure in your system (aka _the\n  database_) and can scale up as your business grows\n\n# Contribute\n\nThe project uses [poetry](https://python-poetry.org/)\n\n```\npoetry config pypi-token.pypi my-token\npoetry config testpypi-token.pypi my-token\n```\n",
    'author': 'Qotto Dev Team',
    'author_email': 'dev@qotto.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/qotto/oss/eventy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
