import logging
from pathlib import Path

import pandas as pd

from puddl import App
from puddl.felix.git import GitError
from puddl.felix.git.repo2rows import Repo

log = logging.getLogger(__package__)


class GitApp(App):
    def __init__(self, name='git'):
        super().__init__(name)

    def truncate(self):
        self.engine.execute('TRUNCATE raw')

    def load(self, paths: [Path], author=None, since_commit=None):
        for path in paths:
            try:
                repo = Repo(path, author, since_commit)
                df = repo.as_df()
                if df.empty:
                    continue
                df['dt'] = pd.to_datetime(df['dt'], utc=True).dt.tz_convert('Europe/Berlin')
                self.df_append(df, 'raw')
                log.info(f'{path} with {len(df)} records')
            except GitError:
                pass
