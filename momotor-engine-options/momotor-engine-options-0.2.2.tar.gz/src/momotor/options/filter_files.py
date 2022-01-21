import typing
from momotor.bundles.elements.files import FilesType, File
from momotor.bundles.utils.filters import F


def file_class_name_filters(class_name) -> typing.Iterable[F]:
    if '#' in class_name:
        class_, name = class_name.split('#', 1)
    else:
        class_, name = class_name, None

    if name:
        yield F(name__glob=name.strip())

    if class_:
        yield F(class_=class_.strip())


def filter_files(files: FilesType, class_name: str) -> FilesType:
    return files.filter(*file_class_name_filters(class_name))


def ifilter_files(files: FilesType, class_name: str) -> typing.Iterable[File]:
    return files.ifilter(*file_class_name_filters(class_name))
