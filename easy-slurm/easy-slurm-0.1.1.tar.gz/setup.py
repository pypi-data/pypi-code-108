# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_slurm', 'easy_slurm.templates']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easy-slurm',
    'version': '0.1.1',
    'description': 'Easily manage and submit robust jobs to Slurm using Python and Bash.',
    'long_description': '# Easy Slurm\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![PyPI](https://img.shields.io/pypi/v/easy-slurm)](https://pypi.org/project/easy-slurm)\n\nEasily manage and submit robust jobs to Slurm using Python and Bash.\n\n## Features\n\n - **Freezes** source code and assets by copying to separate `JOB_DIR`.\n - Applies **performance tweaks** like copying data to local filesystem of compute node (`SLURM_TMPDIR`) for fast I/O.\n - **Exposes hooks** for custom bash code: `setup`/`setup_resume`, `on_run`/`on_run_resume`, and `teardown`.\n - Interrupts running worker process **before job time runs out**.\n - **Auto-saves results** back to `JOB_DIR`.\n - **Auto-submits** another job if current job times out.\n - **Restores** intermediate results and resumes running the `*_resume` hooks.\n - Supports **interactive** jobs for easy debugging.\n\n## Installation\n\n```bash\npip install easy-slurm\n```\n\n## Usage\n\nTo submit a job, simply fill in the various parameters shown in the example below.\n\n```python\nimport easy_slurm\n\neasy_slurm.submit_job(\n    job_root="$HOME/.local/share/easy_slurm/example-simple",\n    src="./src",\n    assets="./assets",\n    dataset="./data.tar.gz",\n    setup="""\n        virtualenv "$SLURM_TMPDIR/env"\n        source "$SLURM_TMPDIR/env/bin/activate"\n        pip install -r "$SLURM_TMPDIR/src/requirements.txt"\n    """,\n    setup_resume="""\n        # Runs only on subsequent runs. Call setup and do anything else needed.\n        setup\n    """,\n    on_run="python main.py",\n    on_run_resume="python main.py --resume",\n    teardown="""\n        # Copy files to results directory.\n        cp "$SLURM_TMPDIR/src/*.log" "$SLURM_TMPDIR/results/"\n    """,\n    sbatch_options={\n        "job-name": "example-simple",\n        "account": "your-username",\n        "time": "3:00:00",\n        "nodes": "1",\n    },\n)\n```\n\nAll job files will be kept in the `job_root` directory. Provide directory paths to `src` and `assets` -- these will be archived and copied to the `job_root` directory. Provide a file path to an archive containing the `dataset`. Also provide Bash code in the hooks, which will be run in the following order:\n\n```\nsetup / setup_resume\non_run / on_run_resume\nteardown\n```\n\nFull examples can be found [here](./examples), including a [simple example](./examples/simple) to run "training epochs" on a cluster.\n\n',
    'author': 'Mateen Ulhaq',
    'author_email': 'mulhaq2005@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/YodaEmbedding/easy-slurm',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
