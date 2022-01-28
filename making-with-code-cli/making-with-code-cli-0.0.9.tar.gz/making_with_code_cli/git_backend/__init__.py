from .github_backend import GithubBackend

def get_backend(name):
    return {
        'github': GithubBackend,
    }[name]
