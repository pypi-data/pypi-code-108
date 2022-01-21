"""
Using local imports we offer via run function access to functions within
a nested class tree
"""


class API:
    from devapp.components.gitlab import GitLab
    from devapp.components.cloudfoundry import CloudFoundry


def run():
    from devapp.cli import run_cls_tree

    return run_cls_tree(API)


run()
