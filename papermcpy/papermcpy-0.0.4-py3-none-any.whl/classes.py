#

class Project():
    def __init__(self, proj_id, proj_name, v_groups, vs):
        self.id = proj_id
        self.name = proj_name
        self.v_groups = v_groups
        self.versions = vs

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'v_groups', self.v_groups
        yield 'versions', self.versions

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"

class Version():
    def __init__(self, proj_id, proj_name, version, builds):
        self.id = proj_id
        self.name = proj_name
        self.version = version
        self.builds = builds

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'version', self.version
        yield 'builds', self.builds

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"

class Build():
    def __init__(self, proj_id, proj_name, version, build, time, channel, promoted, changes, downloads):
        self.id = proj_id
        self.name = proj_name
        self.version = version
        self.build = build
        self.time = time
        self.channel = channel
        self.promoted = promoted
        self.changes = changes
        self.downloads = downloads

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'version', self.version
        yield 'build', self.build
        yield 'time', self.time
        yield 'channel', self.channel
        yield 'promoted', self.promoted
        yield 'changes', self.changes
        yield 'downloads', self.downloads

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"

class Download():
    def __init__(self, download):
        self.download = download

    def __iter__(self):
        yield 'download', self.download

class Family():
    def __init__(self, proj_id, proj_name, v_group, vs):
        self.id = proj_id
        self.name = proj_name
        self.group = v_group
        self.versions = vs

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'group', self.group
        yield 'versions', self.versions

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"

class FBuild():
    def __init__(self, version, build, time, channel, promoted, changes, downloads):
        self.version = version
        self.build = build
        self.time = time
        self.channel = channel
        self.promoted = promoted
        self.changes = changes
        self.downloads = downloads

    def __iter__(self):
        yield 'version', self.version
        yield 'build', self.build
        yield 'time', self.time
        yield 'channel', self.channel
        yield 'promoted', self.promoted
        yield 'changes', self.changes
        yield 'downloads', self.downloads

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"

class FBuilds():
    def __init__(self, proj_id, proj_name, v_group, vs, builds):
        self.id = proj_id
        self.name = proj_name
        self.group = v_group
        self.versions = vs
        if not isinstance(builds, list):
            raise TypeError("Builds has to be a list of FBuild objects")
        for b in builds:
            if not isinstance(b, FBuild):
                raise TypeError(f"One of objects in list of Builds isn't a FBuild object")
        self.builds = builds

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'group', self.group
        yield 'versions', self.versions
        yield 'builds', self.builds

    #def __repr__(self):
    #    return f"{dict(self)}"

    def __str__(self):
        return f"{dict(self)}"
