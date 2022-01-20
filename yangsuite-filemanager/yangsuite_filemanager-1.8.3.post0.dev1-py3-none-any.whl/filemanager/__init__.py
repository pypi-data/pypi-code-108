# -*- coding: utf-8 -*-
u"""Code to manage the storage of YANG files.

In essence, the approach we are going with is as follows:

- A user has one or more "YANG file repositories", located at
  ``get_path('repository', user, reponame)``, e.g.
  ``data/users/$USER/repositories/$REPOSITORY/``.
  This is a compromise between storing all files in a single repository
  (which saves the most disk space but becomes cumbersome for the user to
  browse through) and storing files for each set of modules separately
  (which uses more disk space).
- A user can define any number of "YANG sets", each of which is a view of a
  subset of a repository as a whole.
- A yangset is not dynamically updated - it's a static list of YANG files.

Files to add to the repository can be provided in various ways, including:

- :func:`.upload_files_to_repo`
- :func:`ysnetconf.views.download.download_schemas_to_repo`

When creating a new YANG set, the expected workflow is:

1. Select an existing YANG file repository.
2. Select file(s) from this set to act as basis of new set.
3. Check direct dependencies of these files and prompt the user to add these
   to the yangset.
4. Check indirect dependencies (i.e., reverse dependencies - other files in the
   parent yangset that augment or extend the files in this yangset) and prompt
   the user to choose whether to add these to the yangset.
5. Repeat the above until user is satisfied with the yangset thus defined.
6. Prompt the user to confirm saving the yangset.

This is implemented as a group of related classes::

    (pyang.Repository)
     └-- _YSYangSetBase
         ├-- YSYangDirectoryRepository
         |   └-- YSYangRepository
         └-- YSYangSet
             └-- YSMutableYangSet

- :class:`._YSYangSetBase` - semi-abstract base class, provides basic
  implementation of :class:`pyang.Repository` APIs.
  Private class, shouldn't be used elsewhere.
- :class:`.YSYangDirectoryRepository` - immutable, represents an arbitrary
  directory containing YANG files.
- :class:`.YSYangRepository` - immutable, represents a given user YANG file
  repository under the YANG Suite filesystem hierarchy,
  adds APIs for copying .yang files into the repository, listing available
  repositoroes within the filesystem, etc.
- :class:`.YSYangSet` - immutable, adds APIs for

  - initialization from a list of files
  - initialization from a JSON file prevously created from a
    :class:`.YSMutableYangSet`
  - reporting about mandatory dependencies

- :class:`.YSMutableYangSet` - subclass of :class:`.YSYangSet`, adds APIs for

  - discovering upstream and related modules
  - modification of set contents
  - writing a yang set to disk for later use as a
    :class:`.YSYangSet`.
"""

from .utility import (
    repository_path, yangset_path,
    split_user_set, merge_user_set,
    name_and_revision_from_file, list_yang_files, report_yang_files,
    atomic_create, do_validation, validation_status,
)
from .yangset import YSYangSet
from .dir_repository import YSYangDirectoryRepository
from .repository import YSYangRepository
from .mutableyangset import YSMutableYangSet

__all__ = (
    'YSYangSet',
    'YSYangDirectoryRepository',
    'YSYangRepository',
    'YSMutableYangSet',
    'atomic_create',
    'do_validation',
    'list_yang_files',
    'merge_user_set',
    'name_and_revision_from_file',
    'report_yang_files',
    'repository_path',
    'split_user_set',
    'validation_status',
    'yangset_path',
)
