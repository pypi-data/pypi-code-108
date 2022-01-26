from gitlab_evaluate.lib.cmd import execute

def clone(repo_url):
    return execute(f"git clone {repo_url}")

def get_repo_folder(repo_url):
    return repo_url.split("/")[-1].replace(".git", '')

