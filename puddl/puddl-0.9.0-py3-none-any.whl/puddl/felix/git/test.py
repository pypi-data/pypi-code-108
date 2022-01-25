from .repo2rows import Repo


def test_repo_log(here):
    repo = Repo(here)
    df = repo.as_df()
    print(df.astype({'dt': 'str'}).dtypes)
