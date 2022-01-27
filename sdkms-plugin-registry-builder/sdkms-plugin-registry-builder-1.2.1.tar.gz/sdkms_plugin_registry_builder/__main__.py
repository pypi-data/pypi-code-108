#!/usr/bin/env python3
from git import Repo, InvalidGitRepositoryError
from git.exc import GitCommandError
from json import JSONDecodeError

import argparse
import json
import os
import sys
import warnings

marketplace = {}

metadata_structure = {
    'name': str,
    'version': float,
    'short_description': str,
    'release_notes': [
        str
    ]
}

def check_structure(struct, conf):
    if isinstance(struct, dict) and isinstance(conf, dict):
        # struct is a dict of types or other dicts
        return all(k in conf and check_structure(struct[k], conf[k]) for k in struct)
    if isinstance(struct, list) and isinstance(conf, list):
        # struct is list in the form [type or dict]
        return all(check_structure(struct[0], c) for c in conf)
    elif isinstance(struct, type):
        # struct is the type of conf
        return isinstance(conf, struct)
    else:
        # struct is neither a dict, nor list, not type
        return False


# This is used for old-style plugins where the metadata is stored as comments
# along with the plugin code.
def parse_metadata_in_code(file_contents):
    lines = file_contents.splitlines()
    name = lines[0].partition("Name:")[2].strip()
    if not name:
        raise Exception("1st line should start with `-- Name: <name>`")

    version = lines[1].partition("Version:")[2].strip()
    if not version:
        raise Exception("2nd line should start with `-- Version: <major>.<minor>`")

    try:
        major = int(version.partition(".")[0])
        minor = int(version.partition(".")[2])
        if major < 0 or minor < 0:
            raise ValueError
    except ValueError:
        raise Exception("2nd line should start with `-- Version: <major>.<minor>`")

    description = lines[2].partition("Description:")[2].strip()

    if description:
        in_block = False
        for desc in file_contents.splitlines()[3:]:
            if desc.startswith("--[["):
                in_block = True
                continue
            if desc.startswith("]]--"):
                in_block = False
                continue

            if desc.startswith("--"):
                description += "\n"
                description += desc[2:].strip()
            elif in_block:
                description += "\n"
                description += desc
            else:
                break
    else:
        description = "Plugin description is not available"
    return (name, version, description)


def traverse_tree(repo, hexsha, tree):
   for blob in tree.blobs:
        if blob.path.endswith(".lua"):
            file_contents = repo.git.show('{}:{}'.format(hexsha, blob.path))
            plugin_data = {}
            name = None
            version = None

            # try the inline method first
            try:
                name, version, description = parse_metadata_in_code(file_contents)
                plugin_data["path"] = blob.path
                plugin_data["description"] = description
                plugin_data["commit"] = hexsha
            except BaseException as inline_method_err:
                # try the metadata.json file
                readme_path = os.path.dirname(blob.path) + "/README.md"
                metadata_path = os.path.dirname(blob.path) + "/metadata.json"
                license_path = os.path.dirname(blob.path) + "/LICENSE"
                try:
                    metadata = json.loads(repo.git.show('{}:{}'.format(hexsha, metadata_path)))
                    if not check_structure(metadata_structure, metadata):
                        raise Exception("Invalid metadata.json for plugin " + blob.path)
                    name = metadata["name"]
                    version = str(metadata["version"])
                    short_description = metadata["short_description"]
                    release_notes = metadata["release_notes"]
                    try:
                        description = repo.git.show('{}:{}'.format(hexsha, readme_path))
                    except:
                        description = "Plugin description is not available"
                    plugin_data["path"] = blob.path
                    plugin_data["description"] = description
                    plugin_data["short_description"] = short_description
                    plugin_data["release_notes"] = release_notes
                    plugin_data["commit"] = hexsha
                    try:
                        plugin_data["license"] = repo.git.show('{}:{}'.format(hexsha, license_path))
                    except:
                        pass # if no license file the MPL shall be used
                except GitCommandError as e:
                    if e.status == 128: # Metadata not found
                        print(
                            "Skipping " + blob.path + " in commit " + hexsha + ": no metadata.json was found" +
                            " and parse_metadata_in_code() returned error: " + str(inline_method_err)
                        )
                        continue
                except:
                    raise
            plugin = marketplace.get(name, {})
            plugin[version] = plugin_data
            marketplace[name] = plugin

   for subtree in tree.trees:
       traverse_tree(repo, hexsha, subtree)


def plugin_array_to_dict(array):
    d = {}
    for plugin in array:
        d[plugin.get("name")] = plugin.get("versions")
    return d


def diff_manifest(old, new):
    old = plugin_array_to_dict(old)
    new = plugin_array_to_dict(new)
    changes = []
    for name in old.keys() & new.keys():
        old_versions = old[name]
        new_versions = new[name]
        if old_versions == new_versions:
            continue

        for version in old_versions.keys() & new_versions.keys():
            old_ver = old_versions[version]
            new_ver = new_versions[version]
            if old_ver == new_ver:
                continue
            if old_ver["path"] != new_ver["path"]:
                changes.append("- `{}` v{}: path updated".format(name, version))
            if old_ver["description"] != new_ver["description"]:
                changes.append("- `{}` v{}: description updated".format(name, version))
            if old_ver.get("short_description") != new_ver.get("short_description"):
                changes.append("- `{}` v{}: short description changed".format(name, version))
            if old_ver.get("release_notes") != new_ver.get("release_notes"):
                changes.append("- `{}` v{}: release notes changed".format(name, version))
            # NOTE: ignoring changes to `commit` intentionally.

        for version in old_versions.keys() - new_versions.keys():
            changes.append("- `{}` v{} was removed".format(name, version))
        for version in new_versions.keys() - old_versions.keys():
            changes.append("- `{}` v{} was added".format(name, version))

    for name in old.keys() - new.keys():
        changes.append("- `{}` was removed entirely".format(name))
    for name in new.keys() - old.keys():
        changes.append("- `{}` was added".format(name))

    return "Changes:\n" + ("\n".join(changes) if len(changes) > 0 else "none")


def verify_commits(repo, fail_quick):
    print("verifying commits...")
    not_verified = 0
    for commit in repo.iter_commits():
        ok = True
        try:
            repo.git.verify_commit("--raw", commit)
        except GitCommandError as e:
            if e.status != 0:
                ok = False
            else:
                raise e
        print("Commit: {} -- {}".format(commit, "OK" if ok else "Error"))
        if not ok:
            not_verified += 1
        if not ok and fail_quick:
            break
    if not_verified > 0:
        print("Found {} commits with invalid signatures".format(not_verified))
        sys.exit(1)

    print("Everything checks out")


def main():
    parser = argparse.ArgumentParser(description=help, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "--verify", action="store_true",
        help="Verify commit signatures instead of signing commits"
    )
    parser.add_argument(
        "--fail-quick", action="store_true",
        help="Stop checking more commits when an invalid signature is found"
    )
    parser.add_argument(
        "--repo-dir", action="store",
        required = True,
        help="Path to the plugin registry git repo"
    )
    parser.add_argument(
        "--base-branch", action="store",
        default="master",
        help="Base branch for `git rebase`"
    )
    parser.add_argument(
        "--remote-name", action="store",
        default="origin",
        help="Name of the remote repository used for `git fetch` and `git rebase`"
    )

    args = parser.parse_args()
    repo_dir = os.path.realpath(args.repo_dir)

    try:
        repo = Repo(repo_dir)
    except InvalidGitRepositoryError as e:
        print("Invalid git repo. Error: " + str(e))
        exit(1)

    assert not repo.bare

    if args.verify:
        verify_commits(repo, args.fail_quick)
        return

    # Fetch latest changes from remote repo.
    repo.remote(args.remote_name).fetch()

    # Rebase on base branch and sign commits
    with repo.git.custom_environment(EDITOR='true', GIT_SEQUENCE_EDITOR='true'):
        repo.git.rebase("--exec", "/usr/local/bin/git commit --amend --no-edit -n -S", "-i", args.remote_name + "/" + args.base_branch)

    # Build the manifest
    for commit in repo.iter_commits(None, reverse=True):
        print("Scanning commit: {}".format(commit))
        traverse_tree(repo, commit.hexsha, commit.tree)

    manifest = []

    for (plugin_name, versions) in marketplace.items():
        plugin = {"name": plugin_name, "versions": versions}
        manifest.append(plugin)

    # Find the diff between last manifest and the computed one
    try:
        old_manifest = json.loads(repo.git.show('HEAD:manifest'))
    except:
        old_manifest = []

    diff = diff_manifest(old_manifest, manifest)

    print(diff)

    # Create manifest/commit
    filepath = os.path.join(repo_dir, 'manifest')
    f = open(filepath, "w")
    f.write(json.dumps(manifest, indent=4))
    f.close()

    repo.index.add([filepath])
    repo.git.commit("-S", "-m", "Updated manifest\n\n" + diff)

if __name__ == '__main__':
    main()
