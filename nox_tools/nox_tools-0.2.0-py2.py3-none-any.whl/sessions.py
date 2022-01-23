#!/usr/bin/env python3
from dataclasses import dataclass, field
from glob import glob
from os.path import join
from typing import Callable, List, Optional

import nox

Session = Callable[[nox.Session], None]


@dataclass
class Config:
    """Session configuration

    :param module: user's module name
    """
    module: Optional[str] = None
    _sessions: List[Session] = field(init=False, repr=False,
                                     default_factory=list)

    @property
    def python_files(self):
        if self.module is None:
            raise RuntimeError('User must set config.module')
        return self.module, 'tests', *glob('*.py')

    @property
    def sessions(self) -> List[Session]:
        return self._sessions

    @sessions.setter
    def sessions(self, configured_sessions: List[Session]):
        for session in configured_sessions:
            nox.session(session)
        self._sessions = configured_sessions


config = Config()


def install_requirements(requirements_file: str, session: nox.Session) -> None:
    session.install('-r', join('requirements', requirements_file))


def install_current_package(session: nox.Session) -> None:
    install_requirements('requirements.txt', session)
    session.install('.')


def install_test_packages(session: nox.Session) -> None:
    install_requirements('test_requirements.txt', session)


def tests(session: nox.Session) -> None:
    install_current_package(session)
    install_test_packages(session)
    session.run('coverage', 'run', '-m', 'pytest')
    session.run('coverage', 'report')


def typing(session: nox.Session) -> None:
    install_current_package(session)
    install_test_packages(session)
    install_requirements('typing_requirements.txt', session)
    install_requirements('toolchain_requirements.txt', session)
    session.run('mypy')


def linting(session: nox.Session) -> None:
    install_requirements('linting_requirements.txt', session)
    session.run('isort', '--check-only', *config.python_files)
    session.run('flake8', *config.python_files)
