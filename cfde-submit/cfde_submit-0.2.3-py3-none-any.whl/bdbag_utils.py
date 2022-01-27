import os
import logging
import shutil

from bdbag import bdbag_api
import git

from cfde_submit import CONFIG, exc

logger = logging.getLogger(__name__)


def get_bag(data_path, output_dir=None, delete_dir=False,
            handle_git_repos=True, bdbag_kwargs=None):
    """
    Arguments:
        data_path (str): The path to the data to ingest into DERIVA. The path can be:
                1) A directory to be formatted into a BDBag
                2) A Git repository to be copied into a BDBag
                3) A premade BDBag directory
                4) A premade BDBag in an archive file
        output_dir (str): The path to create an output directory in. The resulting
                BDBag archive will be named after this directory.
                If not set, the directory will be turned into a BDBag in-place.
                For Git repositories, this is automatically set, but can be overridden.
                If data_path is a file, this has no effect.
                This dir MUST NOT be in the `data_path` directory or any subdirectories.
                Default None.
        delete_dir (bool): Should the output_dir be deleted after submission?
                Has no effect if output_dir is not specified.
                For Git repositories, this is always True.
                Default False.
        handle_git_repos (bool): Should Git repositories be detected and handled?
                When this is False, Git repositories are handled as simple directories
                instead of Git repositories.
                Default True.
        bdbag_kwargs (dict): Extra args to pass to bdbag
    """
    bdbag_kwargs = bdbag_kwargs or {}
    data_path = os.path.abspath(data_path)
    if not os.path.exists(data_path):
        raise exc.InvalidInput("Path '{}' does not exist".format(data_path))

    if not os.path.isdir(data_path):
        _, ext = os.path.splitext(data_path)
        if ext.lstrip('.') not in ['zip', 'tar', 'tgz']:
            raise exc.InvalidInput(
                ("The dataset '{}' is invalid. Input MUST be a bdbag (archive or directory) "
                 "or a non-bdbag directory. Any other files cannot be submitted."
                 "").format(data_path))

    if handle_git_repos:
        logger.debug("Checking for a Git repository")
        # If Git repo, set output_dir appropriately
        try:
            repo = git.Repo(data_path, search_parent_directories=True)
        # Not Git repo
        except git.InvalidGitRepositoryError:
            logger.debug("Not a Git repo")
        # Path not found, turn into standard FileNotFoundError
        except git.NoSuchPathError:
            raise FileNotFoundError("Path '{}' does not exist".format(data_path))
        # Is Git repo
        else:
            logger.debug("Git repo found, collecting metadata")
            # Needs to not have slash at end - is known Git repo already, slash
            # interferes with os.path.basename/dirname
            if data_path.endswith("/"):
                data_path = data_path[:-1]
            # Set output_dir to new dir named with HEAD commit hash
            new_dir_name = "{}_{}".format(os.path.basename(data_path), str(repo.head.commit))
            output_dir = os.path.join(os.path.dirname(data_path), new_dir_name)
            # Delete temp dir after archival
            delete_dir = True

    # If dir and not already BDBag, make BDBag
    if os.path.isdir(data_path) and not bdbag_api.is_bag(data_path):
        logger.debug("Creating BDBag out of directory '{}'".format(data_path))
        # If output_dir specified, copy data to output dir first
        if output_dir:
            logger.debug("Copying data to '{}' before creating BDBag".format(output_dir))
            output_dir = os.path.abspath(output_dir)
            # If shutil.copytree is called when the destination dir is inside the source dir
            # by more than one layer, it will recurse infinitely.
            # (e.g. /source => /source/dir/dest)
            # Exactly one layer is technically okay (e.g. /source => /source/dest),
            # but it's easier to forbid all parent/child dir cases.
            # Check for this error condition by determining if output_dir is a child
            # of data_path.
            if os.path.commonpath([data_path]) == os.path.commonpath([data_path, output_dir]):
                raise ValueError("The output_dir ('{}') must not be in data_path ('{}')"
                                 .format(output_dir, data_path))
            try:
                shutil.copytree(data_path, output_dir)
            except FileExistsError:
                raise FileExistsError(f"Error: The directory {output_dir} already exists from a "
                                      f"previous cfde-submit run. Please remove this directory and "
                                      f"try again.")
            # Process new dir instead of old path
            data_path = output_dir
        # If output_dir not specified, never delete data dir
        else:
            delete_dir = False
        # Make bag
        bdbag_api.make_bag(data_path, **bdbag_kwargs)
        if not bdbag_api.is_bag(data_path):
            raise ValueError("Failed to create BDBag from {}".format(data_path))
        logger.debug("BDBag created at '{}'".format(data_path))

    # If dir (must be BDBag at this point), archive
    if os.path.isdir(data_path):
        logger.debug("Archiving BDBag at '{}' using '{}'"
                     .format(data_path, CONFIG["ARCHIVE_FORMAT"]))
        new_data_path = bdbag_api.archive_bag(data_path, CONFIG["ARCHIVE_FORMAT"])
        logger.debug("BDBag archived to file '{}'".format(new_data_path))
        # If requested (e.g. Git repo copied dir), delete data dir
        if delete_dir:
            logger.debug("Removing old directory '{}'".format(data_path))
            shutil.rmtree(data_path)
        # Overwrite data_path - don't care about dir for uploading
        data_path = new_data_path
    return data_path
