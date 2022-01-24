def make_collection_name(git_repo: str, git_repo_dir: str, kitchen_name: str) -> str:
    """
    Generate the name of a mongodb collection from git and kitchen details.
    It's a simple function, but here to make sure the name is constructed consistently.

    :param git_repo: Git repository name
    :param git_repo_dir: Git repository directory name
    :param kitchen_name: Kitchen name
    :return: collection name.
    """
    return f"{git_repo}{git_repo_dir}{kitchen_name}"
