from distutils.command.sdist import sdist as sdist_orig

import setuptools


class sdist(sdist_orig):
    def run(self):
        self.spawn(['ls', 'lopp'])
        # super().run()


setuptools.setup(
    use_scm_version=dict(local_scheme="no-local-version"),
    setup_requires=['setuptools_scm']
)  # options are in setup.cfg
