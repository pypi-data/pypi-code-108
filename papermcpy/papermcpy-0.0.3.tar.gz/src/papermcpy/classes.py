#

class Project():
    def __init__(self, proj_id, proj_name, v_groups, vs):
        self.id = proj_id
        self.name = proj_name
        self.v_groups = v_groups
        self.versions = vs

class Version():
    def __init__(self, proj_id, proj_name, version, builds):
        self.id = proj_id
        self.name = proj_name
        self.version = version
        self.builds = builds

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

class Download():
    def __init__(self, download):
        self.download = download

class Family():
    def __init__(self, proj_id, proj_name, v_group, vs):
        self.id = proj_id
        self.name = proj_name
        self.group = v_group
        self.versions = vs

class FBuild():
    def __init__(self, version, build, time, channel, promoted, changes, downloads):
        self.version = version
        self.build = build
        self.time = time
        self.channel = channel
        self.promoted = promoted
        self.changes = changes
        self.downloads = downloads

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
