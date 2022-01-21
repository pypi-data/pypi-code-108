def solve_version_factory(version, update_prevonly, recursive_solve_version):
    """generate solve_version function
    version is version of module
    update_prevonly is update function which is applied on one
        previous version of data structure
    recursive_solve_version is solve_version of previous version
    """
    def solve_version(d):
        """ test version of d, and apply proper update chain recursively
        """
        v = d.get('version', 0)
        if v >= version:
            return d
        else:
            # get preview version by recursive call of (prev_version)._update
            return update_prevonly(recursive_solve_version(d))

    return solve_version
