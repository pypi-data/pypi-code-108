# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vmm_manager',
 'vmm_manager.entidade',
 'vmm_manager.infra',
 'vmm_manager.parser',
 'vmm_manager.scvmm',
 'vmm_manager.util']

package_data = \
{'': ['*'], 'vmm_manager': ['includes/*', 'includes/ps_templates/*']}

install_requires = \
['configargparse>=1,<2',
 'jinja2>=3,<4',
 'paramiko>=2,<3',
 'pytz>=2021.3',
 'ruamel.yaml>=0.17,<0.18',
 'tqdm>=4,<5',
 'yamale>=4,<5',
 'yamlable>=1,<2']

entry_points = \
{'console_scripts': ['vmm_manager = vmm_manager.vmm_manager:main']}

setup_kwargs = {
    'name': 'vmm-manager',
    'version': '0.1.8',
    'description': 'Management of resources on System Center Virtual Machine Manager (SCVMM) in a declarative way.',
    'long_description': '# vmm-manager\n\nScript python que gerencia recursos no System Center Virtual Machine Manager (SCVMM), de forma declarativa, com base em um arquivo de configuração YAML.\n\n[![License](https://img.shields.io/github/license/MP-ES/vmm_manager.svg)](LICENSE)\n[![Tests](https://github.com/MP-ES/vmm_manager/workflows/Tests/badge.svg)](https://github.com/MP-ES/vmm_manager/actions?query=workflow%3ATests)\n[![Release](https://github.com/MP-ES/vmm_manager/workflows/Release/badge.svg)](https://github.com/MP-ES/vmm_manager/actions?query=workflow%3ARelease)\n[![Python](https://img.shields.io/pypi/pyversions/vmm-manager.svg)](https://pypi.python.org/pypi/vmm-manager)\n[![PyPI](http://img.shields.io/pypi/v/vmm-manager.svg)](https://pypi.python.org/pypi/vmm-manager)\n\n## Pré-requisitos\n\nÉ necessário ter uma máquina Windows, que servirá como ponto de acesso ao SCVMM, com as seguintes ferramentas:\n\n- OpenSSH\n- Módulo PowerShell do SCVMM (**virtualmachinemanager**), instalado junto com o Console do Virtual Machine Manager (VMM). Você também pode obtê-lo em <https://github.com/MP-ES/VirtualMachineManager-PowerShellModule>\n\n## Instalação\n\n```shell\npip install -U vmm-manager\n```\n\n## Uso\n\nPara consultar as funções e os parâmetros disponíveis, utilize o comando:\n\n```shell\nvmm_manager -h\n```\n\n### Exemplo de arquivo de inventário\n\n```yaml\nagrupamento: vmm_manager_test\nnuvem: "developer"\nimagem_padrao: "vm_linux"\nqtde_cpu_padrao: 1\nqtde_ram_mb_padrao: 512\nredes_padrao:\n  - nome: "vlan1"\n    principal: true\nvms:\n  - nome: VMM_TEST1\n    descricao: "Test VM"\n    redes:\n      - nome: "vlan1"\n        principal: true\n      - nome: "vlan2"\n    regiao: A\n    discos_adicionais:\n      - tipo: SCSI\n        arquivo: "disk_var_dir"\n        caminho: "C:\\\\Storage\\\\disk1"\n        tamanho_mb: 1024\n        tamanho_tipo: DynamicallyExpanding\n  - nome: VMM_TEST2\n    regiao: B\n    ansible:\n      - grupo: "web_server"\n  - nome: VMM_TEST3\n    ansible:\n      - grupo: "database"\n        vars:\n          - nome: "data_dir"\n            valor: "/mnt/data"\n      - grupo: "load_balancer"\n```\n\n## Desenvolvimento\n\n### Instalação e configuração do python-poetry\n\nExecute os comandos a seguir:\n\n```shell\n# instalar o poetry\ncurl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python\necho \'source $HOME/.poetry/env\' >>~/.bashrc\n\n# Configurar autocomplete\n# Bash\n$HOME/.poetry/bin/poetry completions bash | sudo tee /etc/bash_completion.d/poetry.bash-completion\n```\n\n### Variáveis de ambiente\n\nDefina as variáveis de ambiente de acordo com as instruções do arquivo **.env.default**. Você pode criar um arquivo **.env** e executar o comando `export $(cat .env | xargs)` para defini-las antes da execução do script.\n\n### Como executar\n\n```shell\n# Carregando envs (opcional)\nexport $(cat .env | xargs)\n\n# Instalando dependências\npoetry install --no-root\n\n# Executando script\npoetry run python -m vmm_manager -h\n```\n\n### Comandos úteis para DEV\n\n```shell\n# Habilitar shell\npoetry shell\n\n# Incluir uma dependência\npoetry add <pacote> [--dev]\n\n# Executar lint\npylint tests/* vmm_manager/*\n\n# Executar testes\npython -m pytest -vv\n```\n\n## Referências\n\n- [Virtual Machine Manager](https://docs.microsoft.com/en-us/powershell/module/virtualmachinemanager/?view=systemcenter-ps-2019)\n- [Poetry](https://python-poetry.org/)\n',
    'author': 'Estevão Costa',
    'author_email': 'ecosta@mpes.mp.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MP-ES/vmm_manager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
