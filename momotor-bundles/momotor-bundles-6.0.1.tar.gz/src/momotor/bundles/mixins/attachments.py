from dataclasses import dataclass

import pathvalidate
import shutil
import time
import typing
import warnings
import zipfile
from pathlib import Path, PurePath, PurePosixPath

import momotor.bundles
from momotor.bundles.typing.element import ElementMixinProtocol
from momotor.bundles.utils.arguments import FileConstructionArguments
from momotor.bundles.utils.zipwrapper import ZipWrapper

CT = typing.TypeVar('CT')


class ZippedAttachment(FileNotFoundError):
    pass


def safe_path_name(name: str) -> str:
    """ Make a path name safe for use in ZIP files by converting it to pure ASCII

    Splits the string into parts separated by a period, then removes any character thats unsafe for use in a zip
    file name. If that changes the name, it adds a short hashcode to the part

    :param name:
    :return:
    """
    def safe_path_part(part: str) -> str:
        new_part = part.encode('ascii', 'replace').decode().replace('?', '')

        if part != new_part:
            import hashlib
            sig = hashlib.md5(part.encode('utf-8')).hexdigest()
            return f'{new_part}-{sig[:6]}'

        return new_part

    return '.'.join(safe_path_part(part) for part in name.split('.'))


@dataclass(frozen=True, init=False)
class AttachmentSrc:
    path: typing.Optional[PurePath] = None
    bundle: typing.Optional["momotor.bundles.Bundle"] = None

    def __init__(self, path: PurePath = None, bundle: "momotor.bundles.Bundle" = None, *, validate=True):
        if path is None or path.is_absolute():
            # Ignore bundle if there is no path or it's absolute
            bundle = None
        elif hasattr(path, 'as_posix'):
            # Convert `path` to a `PurePosixPath` if possible
            path = PurePosixPath(path.as_posix())

        try:
            self.__validate(path, bundle)
        except FileNotFoundError as e:
            if validate:
                raise

            warnings.warn(str(e))
            path = None

        object.__setattr__(self, 'path', path)
        object.__setattr__(self, 'bundle', bundle)

    # noinspection PyProtectedMember
    @staticmethod
    def __validate(path: typing.Optional[PurePath], bundle: typing.Optional["momotor.bundles.Bundle"]):
        if path is None:
            pass

        elif path.is_absolute():
            if not typing.cast(Path, path).exists():
                raise FileNotFoundError(f"attachment file or directory '{path!s}' does not exist")

        elif bundle is None:
            raise FileNotFoundError(f"attachment file or directory '{path!s}' is relative but no bundle is provided")

        elif bundle._base:
            if not (bundle._base / path).exists():
                raise FileNotFoundError(f"attachment file or directory '{path!s}' does not exist in related bundle {bundle}")

        elif bundle._zip_wrapper:
            with bundle._zip_wrapper as zip_file:
                name_list = zip_file.namelist()
                zip_path = str(path)
                zip_path_dir = zip_path + '/'
                for name in name_list:
                    if name == zip_path or name.startswith(zip_path_dir):
                        return

                raise FileNotFoundError(
                    f"attachment file or directory '{path!s}' does not exist in related zip bundle {bundle}. "
                )

        else:
            raise FileNotFoundError(f"attachment file or directory {path!r} does not exist in related bundle {bundle}")


class SrcAttachmentMixin:
    """ Mixin to provide attributes to refer to external files using the `src` attribute

    See :ref:`attachments` for how attachments are handled differently depending on whether the bundle
    is new or an existing one.
    """
    # TODO: use zipfile.Path once we no longer support Python 3.7

    _src: AttachmentSrc = None  # The current location of the attachment
    _export_src: typing.Optional[PurePosixPath] = None  # The location in the export bundle, converted to be safe
    _orig_src: typing.Optional[PurePosixPath] = None  # The original export path before making it safe

    @property
    def src(self) -> typing.Optional[PurePath]:
        """ `src` attribute: file path of the content.

        An absolute path (Path object) when referencing a standalone file, or a relative path (PurePosixPath object)
        when referencing a file in a bundle
        """
        assert self._src, '`src` not set'
        return self._src.path

    @property
    def src_bundle(self) -> typing.Optional["momotor.bundles.Bundle"]:
        """ The bundle `src` references to if it's a relative path
        """
        assert self._src, '`src` not set'
        return self._src.bundle

    # noinspection PyProtectedMember
    def __zip_wrapper(self) -> ZipWrapper:
        return self.src_bundle._zip_wrapper

    def has_bundle(self) -> bool:
        return self.src_bundle is not None

    def has_zip_bundle(self) -> bool:
        return self.has_bundle() and self.__zip_wrapper() is not None

    @src.setter
    def src(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"],
            src: typing.Union[None, PurePath, AttachmentSrc]):
        assert not self._src, "Immutable attribute `src`"
        assert src is None or isinstance(src, (PurePath, AttachmentSrc,))

        if not isinstance(src, AttachmentSrc):
            src = AttachmentSrc(src, self.bundle)

        self._src = src

        # noinspection PyProtectedMember
        self.bundle._register_attachment(self)

    @property
    def export_src(self) -> typing.Optional[PurePosixPath]:
        assert self._export_src is not None, '`export_src` not set'
        return self._export_src

    def has_attachment_content(self) -> bool:
        assert self._src, '`src` not set'
        return self._src.path is not None

    def has_writable_content(self) -> bool:
        return self.has_attachment_content()

    # noinspection PyProtectedMember
    @property
    def absolute_path(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"]) -> Path:
        path = self.src
        if path is None:
            raise FileNotFoundError(path)

        bundle = self.src_bundle
        if bundle:
            if bundle._zip_wrapper:
                raise ZippedAttachment

            if not bundle._base:
                raise FileNotFoundError(bundle._base)

            path = bundle._base / path

        return path.resolve(strict=True)

    def __get_fs_path(self, path: typing.Union[None, str, PurePosixPath]) -> Path:
        src = self.absolute_path
        if path:
            src = src / path
        return src

    def __get_zip_path(self, path: typing.Union[None, str, PurePosixPath]) -> str:
        src = self.src
        if path:
            src = src / path
        return str(src)

    def is_dir(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"],
               path: typing.Union[str, PurePosixPath] = None) -> bool:
        if not self.has_attachment_content() or (path and not self.is_dir(None)):
            raise FileNotFoundError(path)

        if self.has_zip_bundle():
            with self.__zip_wrapper() as zip_file:
                name_list = zip_file.namelist()
                expected_path = self.__get_zip_path(path) + '/'
                for name in name_list:
                    if name.startswith(expected_path):
                        return True

                return False

        else:
            return self.__get_fs_path(path).is_dir()

    def iterdir(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"]) \
            -> typing.Generator[PurePosixPath, None, None]:
        """ Recursively iterate the contents of a directory attachment.
        The returned paths are relative to `self.absolute_path`
        """
        if not self.has_attachment_content() and self.is_dir():
            raise FileNotFoundError

        if self.has_zip_bundle():
            src = self.src

            with self.__zip_wrapper() as zip_file:
                for child_info in zip_file.infolist():
                    if not child_info.is_dir():
                        child_info = PurePosixPath(child_info.filename)
                        try:
                            rel_child = child_info.relative_to(src)
                        except ValueError:
                            pass
                        else:
                            yield rel_child

        else:
            src = self.absolute_path

            def _walk_dir(path: Path):
                for dir_child in path.iterdir():
                    if dir_child.is_dir():
                        yield from _walk_dir(dir_child)
                    else:
                        yield dir_child

            for child in _walk_dir(src):
                rel_child = child.relative_to(src)
                if hasattr(rel_child, 'as_posix'):
                    rel_child = rel_child.as_posix()

                yield rel_child

    def __validate_path(self, path: typing.Union[str, PurePosixPath]):
        assert path is None or isinstance(path, (str, PurePosixPath))

        is_dir = self.is_dir()
        if not self.has_attachment_content() or (is_dir and path is None) or (not is_dir and path):
            raise FileNotFoundError

    def open(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"],
             path: typing.Union[str, PurePosixPath] = None) -> typing.BinaryIO:
        """ Open the attachment file for reading. Handles opening files directly from filesystem
        and from zipped bundles

        :param path: for directory attachments, `path` selects a file in that directory
        :return: the opened file
        :raises FileNotFoundError: if the element has no attachment (when `src` is None), or when it's a directory
            and `path` does not exist in that directory
        """
        self.__validate_path(path)

        if self.has_zip_bundle():
            with self.__zip_wrapper() as zip_file:
                return zip_file.open(self.__get_zip_path(path), 'r')
        else:
            return self.__get_fs_path(path).open('rb')

    def read(self, path: typing.Union[str, PurePosixPath] = None) -> bytes:
        """ Read the contents of the attachment

        :param path: for directory attachments, `path` selects a file in that directory
        :return: A bytes object with the full file contents
        """
        with self.open(path) as f:
            return f.read()

    # Copying attachment into local filesystem

    def _dest_name(self) -> typing.Optional[PurePath]:
        if not self.is_dir() and self.src:
            return PurePath(self.src.name)

        return None

    def copy_to(self, destination: Path, *, name: PurePath = None) -> Path:
        """ Copy attachment to given directory

        If attachment is a file, creates a new file in the given directory. If `name` is provided this will be
        the name of the new file, otherwise the name of the source file is used.

        If attachment is a directory, copies the contents of the source directory to the destination directory.
        If `name` is provided it is created as a new directory inside the destination directory.

        Will not overwrite an existing file or directory.

        :param destination: base destination directory
        :param name: name
        :raises ValueError: when the attachment is not writeable as a file
        :raises FileExistsError: when a file already exists
        """
        if not self.has_writable_content():
            raise ValueError('Non-writable content')

        if not name:
            name = self._dest_name()

        dest_path = destination / name if name else destination
        if dest_path.exists():
            raise FileExistsError(dest_path)

        if self.is_dir():
            self._copy_dir(dest_path)
        else:
            self._copy_file(dest_path)

        return dest_path

    def _export_to_dir(self, destination: Path):
        """ Exports attachment to a new destination

        :param destination: base destination directory
        :raises FileExistsError: when a file already exists
        """
        if self.has_writable_content():
            export_dest = destination / self.export_src
            if self.is_dir():
                self._copy_dir(export_dest)
            else:
                self._copy_file(export_dest)

    def __copy_file_obj(self, name: typing.Optional[PurePosixPath], dest_path: Path):
        dest_path.parent.mkdir(exist_ok=True, parents=True)
        with self.open(name) as reader, dest_path.open('wb') as writer:
            shutil.copyfileobj(reader, writer)

    def _copy_file(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"], dest_path: Path):
        self.__copy_file_obj(None, dest_path)

    def _copy_dir(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"], dest_path: Path):
        for name in self.iterdir():
            self.__copy_file_obj(name, dest_path / name)

    def _export_to_zip(self, zip_file: zipfile.ZipFile, args: FileConstructionArguments):
        """ Exports attachment to a zip file

        :param destination: base destination directory
        :raises ValueError: when the attachment is not writeable as a file
        :raises FileExistsError: when a file already exists
        """
        if self.has_writable_content():
            if self.is_dir():
                self._copy_dir_zip(self.export_src, zip_file, args)
            else:
                self._copy_file_zip(self.export_src, zip_file, args)

    def __copy_file_obj_zip(self, name: typing.Optional[PurePosixPath], dest_path: PurePath,
                            zip_file: zipfile.ZipFile, args: FileConstructionArguments):
        size, ctime = self.file_size(name), self.file_ctime(name)

        zinfo = zipfile.ZipInfo(str(dest_path), ctime or (1980, 1, 1, 0, 0, 0))
        zinfo.compress_type = args.compression
        zinfo._compresslevel = args.compresslevel
        zinfo.file_size = size

        with self.open(name) as src, zip_file.open(zinfo, 'w') as dest:
            shutil.copyfileobj(src, dest)

    def _copy_file_zip(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"], dest_path: PurePath,
                       zip_file: zipfile.ZipFile, args: FileConstructionArguments):
        self.__copy_file_obj_zip(None, dest_path, zip_file, args)

    def _copy_dir_zip(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"], dest_path: PurePath,
                      zip_file: zipfile.ZipFile, args: FileConstructionArguments):
        for name in self.iterdir():
            self.__copy_file_obj_zip(name, dest_path / name, zip_file, args)

    def file_size(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"],
                  path: typing.Union[str, PurePosixPath] = None) -> typing.Optional[int]:
        """ Get file size for the attachment.

        Returns None if content is unsizeable or not found
        """
        if not self.has_attachment_content():
            raise FileNotFoundError

        try:
            if self.has_zip_bundle():
                with self.__zip_wrapper() as zip_file:
                    info = zip_file.getinfo(self.__get_zip_path(path))

                return info.file_size

            return self.__get_fs_path(path).stat().st_size

        except FileNotFoundError:
            return None

    def file_ctime(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"],
                   path: typing.Union[str, PurePosixPath] = None) -> typing.Optional[time.struct_time]:
        """ Get file creation time for the attachment.

        Returns None if content is unsizeable or not found
        """
        if not self.has_attachment_content():
            raise FileNotFoundError

        try:
            if self.has_zip_bundle():
                with self.__zip_wrapper() as zip_file:
                    info = zip_file.getinfo(self.__get_zip_path(path))

                # ZipInfo.date_time is a 6-tuple. Convert it into a proper time.time_struct
                dt: typing.Tuple[int, int, int, int, int, int] = info.date_time
                try:
                    return time.localtime(time.mktime((dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], -1, -1, -1)))
                except (ValueError, OverflowError):
                    return None

            return time.localtime(self.__get_fs_path(path).stat().st_ctime)

        except FileNotFoundError:
            return None

    def file_hashes(self, hash_names: typing.Iterable[str]) -> typing.Dict[str, str]:
        """ Calculate the hashes of the file.

        Only for file attachments. Will return an empty dictionary if the file does not exist.

        :param hash_names: Names of the hashes to calculate. Should be valid arguments to :py:func:`hashlib.new()`
        :return: A dictionary `hash-algorithm` -> `hash`
        """
        import hashlib

        hash_objects = {
            hn: hashlib.new(hn)
            for hn in hash_names
        }

        try:
            with self.open() as f:
                # Non-public const, but it will normally work, and otherwise fall back to a sane default
                bufsize = getattr(shutil, 'COPY_BUFSIZE', 64 * 1024)

                while True:
                    d = f.read(bufsize)
                    if d:
                        for hasher in hash_objects.values():
                            hasher.update(d)
                    else:
                        break

        except FileNotFoundError:
            return {}

        else:
            return {
                hn: hash_obj.hexdigest()
                for hn, hash_obj in hash_objects.items()
            }

    def validate_hashes(self, expected_hashes: typing.Dict[str, str]) -> bool:
        """ Validate hash values of the file.

        Only for file attachments

        :param expected_hashes: A dictionary of `hash-algorithm` -> `hash` items
        :return: True of the hashes are the expected values
        """
        file_hashes = self.file_hashes(expected_hashes.keys())
        return file_hashes == expected_hashes

    # Exporting attachment into a bundle

    # noinspection PyProtectedMember
    def _export_path(self: typing.Union[ElementMixinProtocol, "SrcAttachmentMixin"], path: PurePosixPath) \
            -> PurePosixPath:
        if self._orig_src is None:
            self._orig_src = path

            safe_path = PurePosixPath(
                pathvalidate.sanitize_filepath(
                    '/'.join(safe_path_name(part) for part in path.parts),
                    platform='universal', max_len=255
                )
            )

            index, export_src = 0, safe_path
            while True:
                try:
                    self.bundle._register_attachment_export_path(export_src)
                except FileExistsError:
                    index += 1
                    export_src = path.parent / f'{path.name}-{index}'
                else:
                    self._export_src = export_src
                    break

        else:
            assert self._orig_src == path, '`path` changed between calls'

        return self._export_src


AT = typing.TypeVar('AT', bound=SrcAttachmentMixin)


class SrcAttachmentsMixin(typing.Generic[AT]):
    # noinspection PyMethodMayBeStatic
    def _copy_to(self, attachments: typing.Sequence[AT], destination: Path, **kwargs):
        for attachment in attachments:
            attachment.copy_to(destination, **kwargs)
