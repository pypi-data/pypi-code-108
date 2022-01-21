# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kubectlfr']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['kubectlfr = kubectlfr:main']}

setup_kwargs = {
    'name': 'kubectlfr',
    'version': '1.0.2',
    'description': 'Utilitaire de contrôle de Kubernetes',
    'long_description': "# Utilitaire de contrôle de Kubernetes\n\n> ** What is this ??? **\n> Every time we use a word in English our manager tells us to use the French translation of it. So, here is a version of kubectl ... in French !\n\nLe fonctionnement est très simple : `kubectlfr` traduit les mots qu'il a dans son dictionnaire puis les passe à `kubectl`. Vous pouvez donc utiliser `kubectlfr` exactement vous utilisez `kubectl` tout en vous gardant la possibilité de défendre le beau pays du vin :wine_glass: et du fromage :cheese:.\n\nVous pourrez retrouver tous les mots traduits [ici](https://github.com/theophanevie/kubectlfr/blob/main/kubectlfr/translation.py).\n\nN'hésitez pas à en ajouter, Molière sera fier de vous :fountain_pen: ! Attention aux accents et au pluriel !\n\n### Parce que quelques exemples valent mieux que mille mots \n\nkubectl get pods : \n```shell\n$ kubectlfr récupérer gousses\nNAME                                                              READY    STATUS          RESTARTS      AGE\nceci-est-une-gousse                                                1/1     Running            0          1h\n...\nceci-est-une-autre-gousse                                          1/1     Running            0           9d\n\n```\n\nkubectl create namespace test : \n```shell\n$ kubectlfr créer espace-de-nom test\nnamespace/test created\n```\n\n### Installation\n\n```shell\n$ pip install kubectlfr\n```\n\n### Référence\n\n[kubectl](https://kubernetes.io/docs/tasks/tools/)\n",
    'author': 'Théophane Vié',
    'author_email': 'theophane.vie@petit-nuage.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theophanevie/kubectlfr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
