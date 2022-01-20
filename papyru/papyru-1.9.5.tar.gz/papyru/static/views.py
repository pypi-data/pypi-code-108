import mimetypes
import os
from collections import namedtuple
from enum import Enum
from wsgiref.util import FileWrapper

from django.conf import settings

from papyru import JSONContext, PlainContext, Problem, Resource

DEFAULT_ALLOW_LIST_STATIC_FILES = False


Kind = Enum('PapyruStaticKind', ['FILE', 'DIRECTORY'])

Candidate = namedtuple('PapyruStaticCandidate', ['path',
                                                 'kind',
                                                 'mimetype'])


class StaticFilesList(Resource):
    def get(self, request, file_name):
        candidate = _lookup_candidate(file_name)

        if candidate.kind == Kind.FILE:
            with open(candidate.path, 'rb') as static_file:
                return PlainContext(candidate.mimetype).response(
                    FileWrapper(static_file))
        else:
            if not _may_list_files():
                raise Problem.forbidden()
            listing = os.listdir(candidate.path)
            return JSONContext().response({'items': listing})

    def head(self, request, file_name):
        candidate = _lookup_candidate(file_name)

        if candidate.kind == Kind.FILE:
            return PlainContext(candidate.mimetype).response()
        else:
            if not _may_list_files():
                raise Problem.forbidden()

            return PlainContext('application/json').response()


def _may_list_files():
    return getattr(settings,
                   'PAPYRU_STATIC_FILES_ALLOW_LISTING',
                   DEFAULT_ALLOW_LIST_STATIC_FILES)


def _lookup_candidate(file_name):
    paths = map(lambda directory: os.path.join(directory, file_name),
                settings.PAPYRU_STATIC_FILES_DIRS)

    candidates = set(filter(lambda it: os.path.exists(it), paths))

    if len(candidates) < 1:
        raise Problem.not_found(file_name)

    if len(candidates) > 1:
        raise Problem.internal_error(
            'static file "%s" is ambigous: %s' % (file_name, candidates))

    path = next(iter(candidates))
    is_dir = os.path.isdir(path)

    return Candidate(path=path,
                     mimetype=(mimetypes.guess_type(path)[0]
                               if not is_dir
                               else None),
                     kind=(Kind.FILE if not is_dir else Kind.DIRECTORY))
