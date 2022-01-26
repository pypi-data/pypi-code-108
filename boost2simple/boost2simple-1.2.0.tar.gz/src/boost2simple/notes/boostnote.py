#  boost2simple - the BoostNote->SimpleNote converter
#  Copyright (c) 2021, Rafael Witak.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import codecs
import json
import os

import scandir

from boost2simple import util


class BoostNote:
    def __init__(self,
                 **kwargs):
        self.content = kwargs.get("content", "")
        self.title = kwargs.get("title", "")
        self.folder_pathname = kwargs.get("folderPathname")
        self.creation_date = kwargs.get("createdAt", util.now_as_iso())
        self.modification_date = kwargs.get("updatedAt", self.creation_date)
        self.tags = kwargs.get("tags", list())
        self.deleted = kwargs.get("trashed") == "true"
        self.id_hash = kwargs.get("_id", "")
        self.revision_hash = kwargs.get("_rev", "")
        self.collection_pathname = kwargs.get("collection_pathname")

    @staticmethod
    def _is_valid_json(content_dict: dict):
        return "content", "title", "createdAt" in content_dict.keys()

    @staticmethod
    def from_json(entry: scandir.PosixDirEntry,
                  collection_name: str = None):
        try:
            with codecs.open(entry.path, encoding="utf-8") as current:
                file_content: str = current.read()
                content_dict = json.loads(file_content)
                if BoostNote._is_valid_json(content_dict):
                    return BoostNote(
                        **content_dict,
                        collection_pathname=collection_name)
        except UnicodeDecodeError:
            pass
        print(f"File '{entry.name}' could not be parsed and was skipped.")
        return None

    class Collection:
        def __init__(self, notes: set[BoostNote]):
            self.notes = notes

        @classmethod
        def from_path(cls, path: os.PathLike) -> BoostNote.Collection:
            notes = set()
            for entry in scandir.scandir_python(path):
                notes.update(cls._from_folder_recursively(entry))
            return cls(notes)

        @classmethod
        def _from_folder_recursively(cls,
                                     path: scandir.PosixDirEntry,
                                     parent_path_name: str = ""
                                     ) -> set[BoostNote]:

            notes: set[BoostNote] = set()

            if path.is_file() and path.name.endswith(".json"):
                try:
                    with codecs.open(path.path, encoding="utf-8"):
                        boost_note = \
                            BoostNote.from_json(path,
                                                collection_name=(
                                                    parent_path_name
                                                    if parent_path_name
                                                    else None))
                    if boost_note:
                        notes.add(boost_note)
                except (FileNotFoundError, AttributeError):
                    pass
            elif path.is_dir():
                for entry in scandir.scandir_python(path.path):
                    new_parent_path_name = (parent_path_name
                                            + "/"
                                            + path.name)
                    notes.update(
                        cls._from_folder_recursively(entry,
                                                     new_parent_path_name))

            return notes
