# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import soufi.finders.yum as yum_finder
from soufi import finder

DEFAULT_REPO = "https://cdn-ubi.redhat.com/content/public/ubi/dist"


class RHELFinder(yum_finder.YumFinder):
    """Find Red Hat Enterprise Linux source files.

    By default, uses the public UBI index at https://cdn-ubi.redhat.com
    """

    distro = finder.Distro.rhel.value

    # UBI is kind of sprawling, and they are fairly idiosyncratic with where
    # they like to put their packages, tree-wise.  Once you find the proper
    # subtree, they are delightfully regular with the repo structure, however.
    # Rather than aimlessly poke around their CDN, we'll use this
    # hand-curated list of search paths.
    default_search_dirs = (
        'ubi8/8/x86_64/baseos',
        'ubi8/8/x86_64/appstream',
        'ubi8/8/x86_64/codeready-builder',
        'ubi/server/7/7Server/x86_64',
        'ubi/server/7/7Server/x86_64/extras',
        'ubi/server/7/7Server/x86_64/devtools/1',
        'ubi/server/7/7Server/x86_64/optional',
        'ubi/server/7/7Server/x86_64/rhscl/1',
        'ubi/atomic/7/7Server/x86_64',
    )

    def get_source_repos(self):
        return [
            f"{DEFAULT_REPO}/{dir}/source/SRPMS"
            for dir in self.default_search_dirs
        ]

    def get_binary_repos(self):
        return [f"{DEFAULT_REPO}/{dir}/os" for dir in self.default_search_dirs]
