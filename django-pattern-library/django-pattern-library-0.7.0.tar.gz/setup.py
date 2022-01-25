# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pattern_library',
 'pattern_library.management',
 'pattern_library.management.commands']

package_data = \
{'': ['*'],
 'pattern_library': ['static/pattern_library/dist/bundle.js',
                     'templates/pattern_library/*']}

install_requires = \
['Django>=2.2,<4.1', 'Markdown>=3.1,<4.0', 'PyYAML>=5.1,<7.0']

setup_kwargs = {
    'name': 'django-pattern-library',
    'version': '0.7.0',
    'description': 'A module for Django that allows to build pattern libraries for your projects.',
    'long_description': '# [django-pattern-library](https://torchbox.github.io/django-pattern-library/)\n\n[![PyPI](https://img.shields.io/pypi/v/django-pattern-library.svg)](https://pypi.org/project/django-pattern-library/) [![PyPI downloads](https://img.shields.io/pypi/dm/django-pattern-library.svg)](https://pypi.org/project/django-pattern-library/) [![Build status](https://github.com/torchbox/django-pattern-library/workflows/CI/badge.svg)](https://github.com/torchbox/django-pattern-library/actions)\n\n> UI pattern libraries for Django templates. Try our [online demo](https://torchbox.github.io/django-pattern-library/demo/).\n\n![Screenshot of the pattern library UI, with navigation, pattern rendering, and configuration](https://raw.githubusercontent.com/torchbox/django-pattern-library/main/.github/pattern-library-screenshot.webp)\n\n## Features\n\nThis package automates the maintenance of UI pattern libraries or styleguides for Django projects, and allows developers to experiment with Django templates without having to create Django views and models.\n\n- Create reusable patterns by creating Django templates files as usual.\n- All patterns automatically show up in the pattern library’s interface.\n- Define data as YAML files for the templates to render with the relevant Django context.\n- Override Django templates tags as needed to mock the template’s dependencies.\n- Document your patterns with Markdown.\n\n## Why you need this\n\nPattern libraries will change your workflow for the better:\n\n- They help separate concerns, both in code, and between members of a development team.\n- If needed, they make it possible for UI development to happen before models and views are created.\n- They encourage code reuse – defining independent UI components, that can be reused across apps, or ported to other projects.\n- It makes it much simpler to test UI components –\xa0no need to figure out where they’re used across a site or app.\n\nLearn more by watching our presentation – [Reusable UI components: A journey from React to Wagtail](https://www.youtube.com/watch?v=isrOufI7TKc).\n\n## Online demo\n\nThe pattern library is dependent on Django for rendering – but also supports exporting as a static site if needed. Try out our online demo:\n\n- For a component, [accordion.html](https://torchbox.github.io/django-pattern-library/demo/pattern/patterns/molecules/accordion/accordion.html)\n- For a page-level template, [person_page.html](https://torchbox.github.io/django-pattern-library/demo/pattern/patterns/pages/people/person_page.html)\n\n## Documentation\n\nDocumentation is available at [torchbox.github.io/django-pattern-library](https://torchbox.github.io/django-pattern-library/), with source files in the `docs` directory.\n\n- **[Getting started](https://torchbox.github.io/django-pattern-library/getting-started/)**\n- **Guides**\n  - [Defining template context](https://torchbox.github.io/django-pattern-library/guides/defining-template-context/)\n  - [Overriding template tags](https://torchbox.github.io/django-pattern-library/guides/overriding-template-tags/)\n  - [Customizing template rendering](https://torchbox.github.io/django-pattern-library/guides/customizing-template-rendering/)\n  - [Usage tips](https://torchbox.github.io/django-pattern-library/guides/usage-tips/)\n- **Reference**\n  - [API & settings](https://torchbox.github.io/django-pattern-library/reference/api/)\n  - [Known issues and limitations](https://torchbox.github.io/django-pattern-library/reference/known-issues/)\n\n## Contributing\n\nSee anything you like in here? Anything missing? We welcome all support, whether on bug reports, feature requests, code, design, reviews, tests, documentation, and more. Please have a look at our [contribution guidelines](https://github.com/torchbox/django-pattern-library/blob/main/CONTRIBUTING.md).\n\nIf you want to set up the project on your own computer, the contribution guidelines also contain all of the setup commands.\n\n### Nightly builds\n\nTo try out the latest features before a release, we also create builds from every commit to `main`. Note we make no guarantee as to the quality of those pre-releases, and the pre-releases are overwritten on every build so shouldn’t be relied on for reproducible builds. [Download the latest `django_pattern_library-0.0.0.dev0-py3-none-any.whl`](http://torchbox.github.io/django-pattern-library/dist/django_pattern_library-0.0.0.dev0-py3-none-any.whl).\n\n## Credits\n\nView the full list of [contributors](https://github.com/torchbox/django-pattern-library/graphs/contributors). [BSD](https://github.com/torchbox/django-pattern-library/blob/main/LICENSE) licensed.\n\nProject logo from [FxEmoji](https://github.com/mozilla/fxemoji). Documentation website built with [MkDocs](https://www.mkdocs.org/), and hosted in [GitHub Pages](https://pages.github.com/).\n',
    'author': 'Ben Dickinson',
    'author_email': 'ben.dickinson@torchbox.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/torchbox/django-pattern-library',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
