import re

from release_mgr.git import get_commit_for_tag, get_tags, git


class Version:
    """A semver object."""

    release_ver = re.compile(r"^(v)?[0-9]+\.[0-9]+\.[0-9]+(-[A-z0-9]+)?$")

    def __init__(self, major, minor, patch, suffix=None, use_v_prefix=False):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.suffix = suffix
        self.use_v_prefix = use_v_prefix

    @staticmethod
    def is_version_string(verstr):
        return bool(Version.release_ver.match(verstr))

    @classmethod
    def latest_version(cls):
        tags = [
            tag[len("refs/tags/") :] for tag in get_tags() if tag[len("refs/tags/") :]
        ]
        if not tags:
            commits = git("log", "--reverse", "--format=%H").split("\n")
            return (
                commits[0],
                cls(0, 0, 0),
            )

        versions = sorted(map(Version.from_str, tags))
        latest_version = versions[-1]
        last_version_commit = get_commit_for_tag(str(latest_version))
        return (
            last_version_commit,
            latest_version,
        )

    @classmethod
    def from_str(cls, verstr):
        if not Version.is_version_string(verstr):
            raise Exception("Got unexpected input: {verstr}".format(verstr=verstr))

        major, minor, patch = verstr.split(".")
        suffix = None
        if "-" in patch:
            patch, suffix = patch.split("-")

        use_v_prefix = False
        if major.startswith("v"):
            major = major[1:]
            use_v_prefix = True

        return cls(
            int(major),
            int(minor),
            int(patch),
            suffix,
            use_v_prefix=use_v_prefix,
        )

    def increment_patch(self):
        self.patch += 1

    def increment_minor(self):
        self.minor += 1
        self.patch = 0

    def increment_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0

    def __str__(self):
        return "{prefix}{major}.{minor}.{patch}{suffix}".format(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            suffix="-" + self.suffix if self.suffix else "",
            prefix="v" if self.use_v_prefix else "",
        )

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False

        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.suffix == other.suffix
        )

    def __lt__(self, other):
        for version_part in ["major", "minor", "patch"]:
            ours = getattr(self, version_part)
            theirs = getattr(other, version_part)
            if ours > theirs:
                return False

            if theirs > ours:
                return True

            # Same version part value

        if self.suffix == other.suffix:
            return False

        suffix_precedence = {
            "beta": -1,
            "tc": 0,
            "rc": 1,
            None: 2,
        }

        our_suffix = suffix_precedence.get(self.suffix, -2)
        their_suffix = suffix_precedence.get(other.suffix, -2)
        return our_suffix < their_suffix

    def __le__(self, other):
        return self == other or self < other
