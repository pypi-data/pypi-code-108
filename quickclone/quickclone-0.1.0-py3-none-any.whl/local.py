from pathlib import Path


def make_path(path: str) -> str:
    """
    Really roundabout way of processing paths for `options.local.remotes_dir`.
    """
    if path == "":
        return ""
    else:
        ppath = Path(path).expanduser()
        if ppath.suffix in {".git"}:
            return str(ppath.with_suffix(""))
        else:
            return str(ppath)


def local_dest_path(
    user_input: str,
    remotes_dir: str,
    host: str,
    path: str,
    ignore_config: bool
) -> str:
    """
    Get the path where the remote repository should be cloned to
    from a variety of inputs.
    
    Parameters
    ----------
    user_input: str
        The destination path given by the user.
    
    remotes_dir: str
        The directory to local clones of remote repositories.
    
    host: str
        The host name of the site storing the remote repository.
    
    path: str
        The path to the remote repository (in the URL).
    
    ignore_config: bool
        Whether to ignore the `options.local.remotes_dir` config.
    
    Returns
    -------
    str
        The destination path to the cloned repository.
    """
    if ignore_config:
        return make_path(user_input)
    else:
        if user_input != "":
            return make_path(user_input)
        else:
            return make_path(Path(remotes_dir) / Path(host) / Path(path))
