import git


def add_all(path, repo):
    lst = []
    for p in path.rglob("*"):
        print(p.name)
        if not str(p).lower().startswith(".git/"):
            lst.append(str(p.resolve()))

    repo.index.add(lst)
    repo.index.commit("initial commit")


def init(path):
    r = git.Repo.init(path)
    return r
