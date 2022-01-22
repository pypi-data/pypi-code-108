"""
Core semantic version functionality.

Author: Tom Fleet
Created: 08/10/2021
"""

from __future__ import annotations

import json
import re
import sys
from typing import Optional, Tuple

# Compatibility with python 3.7
if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import TypedDict
else:
    from typing_extensions import TypedDict  # pragma: no cover

# See https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
# The only thing we've added is the optional v at the start
_SEMVER_REGEX = re.compile(
    r"""^v?(?P<major>0|[1-9]\d*)\. # Major
    (?P<minor>0|[1-9]\d*)\. # Minor
    (?P<patch>0|[1-9]\d*) # Patch
    (?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))? # Optional pre-release # noqa: E501
    (?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$""",  # Optional build metadata
    flags=re.VERBOSE,
)


class VersionDict(TypedDict):
    """
    Schema for the dictionary a `Version` object
    expects to unpack
    """

    major: int
    minor: int
    patch: int
    prerelease: str | None
    buildmetadata: str | None


VersionTuple = Tuple[int, int, int, Optional[str], Optional[str]]


class Version:
    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: str | None = None,
        buildmetadata: str | None = None,
    ) -> None:
        """
        A data container for a semantic version.

        Args:
            major (int): The major version, to be incremented when making
                backwards incompatible (breaking) changes.
            minor (int): The minor version, to be incremented when introducing
                backwards compatible features.
            patch (int): The patch version, to be incremented when making
                backwards compatible bug fixes.
            prerelease (Optional[str], optional): Any pre-release tags
                e.g. 'rc.1'. Defaults to None.
            buildmetadata (Optional[str], optional): Any build meta tags
                e.g. 'build.123'. Defaults to None.

        Raises:
            ValueError: If any numeric version part < 0.
        """
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.buildmetadata = buildmetadata

        if any(part < 0 for part in (self.major, self.minor, self.patch)):
            raise ValueError(
                f"Version {self!r} is invalid. Parts cannot be less than 0."
            )

    __slots__ = ("major", "minor", "patch", "prerelease", "buildmetadata")

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(major={self.major!r}, minor={self.minor!r}, patch={self.patch!r}, "
            + f"prerelease={self.prerelease!r}, buildmetadata={self.buildmetadata!r})"
        )

    def __str__(self) -> str:
        ver = f"v{self.major}.{self.minor}.{self.patch}"

        if self.prerelease:
            ver += f"-{self.prerelease}"

        if self.buildmetadata:
            ver += f"+{self.buildmetadata}"

        return ver

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise TypeError(f"Cannot compare object of type Version and {type(other)}")

        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
            self.buildmetadata,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
            other.buildmetadata,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise TypeError(f"Cannot compare object of type Version and {type(other)}")

        if (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        ):
            return True

        pre_release_comp = self._compare_prerelease(other)
        if pre_release_comp == -1:
            return True

        build_comp = self._compare_build(other)
        if build_comp == -1:
            return True

        return False

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise TypeError(f"Cannot compare object of type Version and {type(other)}")

        if (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        ):
            return True

        pre_release_comp = self._compare_prerelease(other)
        if pre_release_comp == 1:
            return True

        build_comp = self._compare_build(other)
        if build_comp == 1:
            return True

        return False

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise TypeError(f"Cannot compare object of type Version and {type(other)}")

        if self == other:
            return True

        if self < other:
            return True

        return False

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise TypeError(f"Cannot compare object of type Version and {type(other)}")

        if self == other:
            return True

        if self > other:
            return True

        return False

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def _compare_prerelease(self, other: Version) -> int:
        """
        Helper to try and compare the pre-release versions.

        It will check for string equality, whether or not
        the different versions have pre-releases, check
        for integers in the text and compare based on them,
        and if none of this works will raise a ValueError.

        Note: This is only called if the numeric version
        is equal.
        """
        if self.prerelease == other.prerelease:
            # The pre release strings are equal
            return 0
        elif self.prerelease and not other.prerelease:
            # Ours has a pre-release but the other doesn't
            # meaning ours is less
            return -1
        elif not self.prerelease and other.prerelease:
            # Ours doesn't have a pre-release but the other
            # does meaning ours is greater
            return 1

        # Try and extract a number to compare
        if self.prerelease and other.prerelease:
            ours = re.findall(pattern=r"\d+", string=self.prerelease)
            others = re.findall(pattern=r"\d+", string=other.prerelease)

            if not ours or not others:
                raise ValueError("Could not parse comparable pre-release version info.")

            if len(ours) > 1 or len(others) > 1:
                raise ValueError("Multiple integers found in pre-release version.")

            our_version = int(ours.pop())
            other_version = int(others.pop())

            if our_version == other_version:
                return 0
            elif our_version > other_version:
                return 1
            elif our_version < other_version:
                return -1

        # If we get here, we couldn't parse the pre-release
        raise ValueError(
            f"Could not compare {self.prerelease} and {other.prerelease}"
        )  # pragma: no cover

    def _compare_build(self, other: Version) -> int:
        """
        Helper to try and compare the build metadata versions.

        It will check for string equality, whether or not
        the different versions have pre-releases, check
        for integers in the text and compare based on them,
        and if none of this works will raise a ValueError.

        Note: This is only called if both the numeric version
        and the pre-release strings are equal.
        """
        if self.buildmetadata == other.buildmetadata:
            # The pre release strings are equal
            return 0
        elif self.buildmetadata and not other.buildmetadata:
            # Ours has a pre-release but the other doesn't
            # meaning ours is less
            return -1
        elif not self.buildmetadata and other.buildmetadata:
            # Ours doesn't have a pre-release but the other
            # does meaning ours is greater
            return 1

        # Try and extract a number to compare
        if self.buildmetadata and other.buildmetadata:
            ours = re.findall(pattern=r"\d+", string=self.buildmetadata)
            others = re.findall(pattern=r"\d+", string=other.buildmetadata)

            if not ours or not others:
                raise ValueError(
                    "Could not parse comparable build metadata version info."
                )

            if len(ours) > 1 or len(others) > 1:
                raise ValueError("Multiple integers found in build metadata version.")

            our_version = int(ours.pop())
            other_version = int(others.pop())

            if our_version == other_version:
                return 0
            elif our_version > other_version:
                return 1
            elif our_version < other_version:
                return -1

        # If we get here, we couldn't parse the pre-release
        raise ValueError(
            f"Could not compare {self.buildmetadata} and {other.buildmetadata}"
        )  # pragma: no cover

    def is_valid(self) -> bool:
        """
        Checks the `Version` against the official
        semver regex pattern and reports whether or not it
        is a valid semver.

        Returns:
            bool: True if `Version` is valid, else False

        Examples:

        ```python
        >>> v = Version(1, 2, 4)
        >>> v.is_valid()
        True

        ```

        ```python
        >>> v = Version(1, 2, 4, "blah198y_+-2-", "build---19790")
        >>> v.is_valid()
        False

        ```
        """
        return bool(_SEMVER_REGEX.match(self.to_string()))

    def bump_major(self) -> Version:
        """
        Return a new `Version` with the major version
        number bumped.

        Returns:
            Version: New bumped version.

        Examples:

        ```python
        >>> v1 = Version(1, 2, 4)
        >>> v1.bump_major()
        Version(major=2, minor=0, patch=0, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v1 = Version(0, 7, 6, "rc.1", "build.123")
        >>> v1.bump_major()
        Version(major=1, minor=0, patch=0, prerelease=None, buildmetadata=None)

        ```
        """
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> Version:
        """
        Return a new `Version` with the minor version
        number bumped.

        Returns:
            Version: New bumped version.

        Examples:

        ```python
        >>> v1 = Version(1, 2, 4)
        >>> v1.bump_minor()
        Version(major=1, minor=3, patch=0, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v1 = Version(0, 7, 6, "rc.1", "build.123")
        >>> v1.bump_major()
        Version(major=1, minor=0, patch=0, prerelease=None, buildmetadata=None)

        ```
        """
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> Version:
        """
        Return a new `Version` with the patch version
        number bumped.

        Returns:
            Version: New bumped version.

        Examples:

        ```python
        >>> v1 = Version(1, 2, 4)
        >>> v1.bump_patch()
        Version(major=1, minor=2, patch=5, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v1 = Version(0, 7, 6, "rc.1", "build.123")
        >>> v1.bump_major()
        Version(major=1, minor=0, patch=0, prerelease=None, buildmetadata=None)

        ```
        """
        return Version(self.major, self.minor, self.patch + 1)

    def to_string(self) -> str:
        """
        Generate a string representation of the
        `Version`.

        Returns:
            str: Version string.

        Examples:

        ```python
        >>> v = Version(1, 2, 4)
        >>> v.to_string()
        'v1.2.4'

        ```

        ```python
        >>> v = Version(1, 2, 4, "rc.2", "build.6")
        >>> v.to_string()
        'v1.2.4-rc.2+build.6'

        ```
        """
        return str(self)

    def to_tuple(self) -> VersionTuple:
        """
        Return the `Version` as a tuple of it's
        fields.

        Returns:
            VersionTuple: The Version tuple.

        Examples:

        ```python
        >>> v = Version(1, 2, 4)
        >>> v.to_tuple()
        (1, 2, 4, None, None)

        ```

        ```python
        >>> v = Version(1, 2, 4, "rc.2", "build.6")
        >>> v.to_tuple()
        (1, 2, 4, 'rc.2', 'build.6')

        ```
        """
        return (self.major, self.minor, self.patch, self.prerelease, self.buildmetadata)

    def to_dict(self) -> VersionDict:
        """
        Return the `Version` as a dictionary.

        Returns:
            VersionDict: The Version dictionary.

        Examples:

        ```python
        >>> v = Version(1, 2, 4)
        >>> v.to_dict()
        {'major': 1, 'minor': 2, 'patch': 4, 'prerelease': None, 'buildmetadata': None}

        ```

        ```python
        >>> v = Version(1, 2, 4, "rc.1", "build.2")
        >>> v.to_dict()
        {'major': 1, 'minor': 2, 'patch': 4, 'prerelease': 'rc.1', 'buildmetadata': 'build.2'}

        ```
        """
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "prerelease": self.prerelease,
            "buildmetadata": self.buildmetadata,
        }

    def to_json(self) -> str:
        """
        Return the `Version` as a JSON string.

        Returns:
            str: The Version JSON string.

        Examples:

        ```python
        >>> v = Version(1, 2, 4)
        >>> v.to_json()
        '{"major": 1, "minor": 2, "patch": 4, "prerelease": null, "buildmetadata": null}'

        ```

        ```python
        >>> v = Version(1, 2, 4, "rc.1", "build.2")
        >>> v.to_json()
        '{"major": 1, "minor": 2, "patch": 4, "prerelease": "rc.1", "buildmetadata": "build.2"}'

        ```
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, version_dict: VersionDict) -> Version:
        """
        Construct and return a `Version` from a dictionary
        of it's parts.

        Expects a dictionary with keys: `major`, `minor`, `patch`,
        `prerelease` and `buildmetadata`.

        Args:
            version_dict (VersionDict): Version as a dictionary of it's
                parts.

        Returns:
            Version: Constructed Version.

        Raises:
            TypeError: If the passed dictionary does not
                have keys matching the required parts.

        Examples:

        ```python
        >>> v = {"major": 1, "minor": 2, "patch": 4}
        >>> Version.from_dict(v)
        Version(major=1, minor=2, patch=4, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v = {"major": 1, "minor": 2, "patch": 4, "prerelease": "rc.1", "buildmetadata": "build.123"}
        >>> Version.from_dict(v)
        Version(major=1, minor=2, patch=4, prerelease='rc.1', buildmetadata='build.123')

        ```
        """
        return Version(**version_dict)

    @classmethod
    def from_string(cls, string: str) -> Version:
        """
        Construct and return a `Version` from a valid semver
        string.

        Args:
            string (str): The semver string.

        Raises:
            ValueError: If the semver string does not
                pass the official semver regex.

        Returns:
            Version: The constructed Version.

        Examples:

        ```python
        >>> Version.from_string("v1.2.4")
        Version(major=1, minor=2, patch=4, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> Version.from_string("v1.2.4-rc.1+build.123")
        Version(major=1, minor=2, patch=4, prerelease='rc.1', buildmetadata='build.123')

        ```
        """
        match = _SEMVER_REGEX.match(string)
        if not match:
            raise ValueError(f"{string!r} is not a valid semver string.")

        return Version.from_dict(
            VersionDict(
                major=int(match.group("major")),
                minor=int(match.group("minor")),
                patch=int(match.group("patch")),
                prerelease=match.group("prerelease"),
                buildmetadata=match.group("buildmetadata"),
            )
        )

    @classmethod
    def from_tuple(cls, tup: VersionTuple) -> Version:
        """
        Construct and return a `Version` from a tuple of it's
        parts.

        Args:
            tup (VersionTuple): The tuple to construct the Version
                from.

        Returns:
            Version: The constructed Version.

        Examples:

        ```python
        >>> v = (1, 2, 4)
        >>> Version.from_tuple(v)
        Version(major=1, minor=2, patch=4, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v = (1, 2, 4, "rc.1", "build.123")
        >>> Version.from_tuple(v)
        Version(major=1, minor=2, patch=4, prerelease='rc.1', buildmetadata='build.123')

        ```
        """
        return Version(*tup)

    @classmethod
    def from_json(cls, json_string: str) -> Version:
        """
        Construct and return a `Version` from a json string
        of it's parts.

        Args:
            json_string (str): The json string.

        Returns:
            Version: The constructed Version.

        Examples:

        ```python
        >>> v = '{"major": 1, "minor": 2, "patch": 4}'
        >>> Version.from_json(v)
        Version(major=1, minor=2, patch=4, prerelease=None, buildmetadata=None)

        ```

        ```python
        >>> v = '{"major": 1, "minor": 2, "patch": 4, "prerelease": "rc.1", "buildmetadata": "build.123"}'
        >>> Version.from_json(v)
        Version(major=1, minor=2, patch=4, prerelease='rc.1', buildmetadata='build.123')

        ```
        """
        data: VersionDict = json.loads(json_string)
        return Version(**data)
