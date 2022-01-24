# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_release']

package_data = \
{'': ['*']}

install_requires = \
['databind.json>=1.4.0,<2.0.0',
 'nr.util>=0.4.5,<0.5.0',
 'poetry>=1.2.0a2,<2.0.0',
 'tomli>=2.0.0,<3.0.0']

entry_points = \
{'poetry.application.plugin': ['release-command = '
                               'poetry_release._poetry_plugin:ReleasePlugin']}

setup_kwargs = {
    'name': 'nr.poetry-release',
    'version': '0.1.2',
    'description': 'A Poetry plugin to automate the release process of Python packages.',
    'long_description': '# nr.poetry-release\n\nA Poetry plugin to automate releasing new versions of Python packages.\n\n__Features__\n\n* Update the version number in all relevant places\n  * Built-in support for `pyproject.toml` (like the `poetry version`command) & in your package source code\n  * Configuration option to match and bump version numbers in other files\n  * Plugin infrastructure to dispatch additional logic on version bump (used by e.g. `poetry-changelog`)\n* Automatically commit, tag and push version bumps\n* Easily release from CI\n\n## Installation\n\nPlugins work with Poetry version `1.2.0a2` or above.\n\n    $ poetry plugin add nr.poetry-release\n\n## Usage\n\n    $ poetry release patch --tag --push\n\nThis will\n\n1. Increment the patch version number in `pyproject.toml` and synchronize all other built-in and configured places\n   where the version number is referenced\n2. Commit the changes and create a Git tag with the new version number, then push the branch to the remote repository\n\nIn addition to the version rules already supported by `poetry version`, the `poetry release` plugin supports a `git`\nrule which will construct a version number based on the last Git tag and the commit distance. Note that this version\nnumber is not PyPI compatible, but can be used to publish for example to Artifactory.\n\nUsing the `--verify` option will instead check if the specified version number is used consistently across all version\nreferences and is useful in CI.\n\n## Configuration\n\n__Release branch__\n\nIf in a Git project, unless `--no-branch-check` is passed, `poetry release` will prevent you from creating the\nrelease unless the worktree is currently on the configured release branch (`develop` by default). The release\nbranch can be changed by setting the `tool.nr.poetry-release.branch` option in `pyproject.toml`.\n\n```toml\n[tool.nr.poetry-release]\nbranch = "main"\n```\n\n__Tag format__\n\nWhen using the `--tag` option, a Git tag will be created with the target version as its name. The name assigned to the\nnew tag can be changed by setting the `tool.nr.poetry-release.tag-format` option in `pyproject.toml`. For example, if the\ntarget version is `1.0.0` but the tag name should be `v1.0.0`, the configuration to use is:\n\n```toml\n[tool.nr.poetry-release]\ntag-format = "v{version}"\n```\n\n__Additional version references__\n\nYou can configure additional references to the version number in your project using the `tool.nr.poetry-release.references`\noption. It must be a list of tables that define the files and a regular expression to find the version number.\n\n```toml\n[tool.nr.poetry-release]\nreferences = [\n  { file = "../frontend/package.json", pattern = "  \\"version\\": \\"{version}\\"," }\n]\n```\n\nIn addition to this configuration option, plugins of type `peotry_release.plugin_api.PoetryReleasePlugin` registered\nunder the `poetry_release.plugins` entrypoint will be used to detect additional version number references, or register\na callback to modify file(s) with respect to the target version number.\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
