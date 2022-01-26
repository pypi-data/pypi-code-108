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

import json
import os
import uuid
import zipfile
from io import BytesIO

from boost2simple import util
from boost2simple.notes.boostnote import BoostNote


class SimpleNote:
    ENCODER = json.JSONEncoder(indent=2, ensure_ascii=False)

    def __init__(self,
                 **kwargs):

        self.content = kwargs.get("content", "")
        self.id_hash = kwargs.get("id", "")
        self.creation_date = kwargs.get("creationDate", util.now_as_iso())
        self.modification_date = kwargs.get("lastModified", self.creation_date)
        self.pinned = kwargs.get("pinned", False)
        self.markdown = kwargs.get("markdown", True)
        self.tags = kwargs.get("tags", list())
        self.deleted = kwargs.get("deleted", False)
        self.published = kwargs.get("published", False)
        self.shared = kwargs.get("shared", False)
        self._title = kwargs.get("title", "")

    def _as_dict(self) -> dict:
        dict_ = {"id": self.id_hash,
                 "content": self.content,
                 "creationDate": self.creation_date,
                 "lastModified": self.modification_date}

        if self.tags:
            dict_["tags"] = self.tags
        if self.markdown:
            dict_["markdown"] = True
        if self.pinned:
            dict_["pinned"] = self.pinned

        return dict_

    @classmethod
    def _from_boost_note(cls,
                         boost_note: BoostNote,
                         markdown: bool = True,
                         title=True) -> SimpleNote:
        content = cls._get_content_from_boost_note(boost_note, markdown, title)
        tags = SimpleNote.get_simple_tags_for_boost(boost_note)

        return SimpleNote(
            content=content,
            id=uuid.uuid4().hex,
            creationDate=boost_note.creation_date,
            lastModified=boost_note.modification_date,
            pinned=False,
            markdown=True,
            tags=tags,
            published=False,
            shared=False,
            deleted=boost_note.deleted,
            title=boost_note.title)

    @classmethod
    def get_simple_tags_for_boost(cls, boost_note):
        tags = boost_note.tags
        if boost_note.collection_pathname:
            full_pathname: str = boost_note.collection_pathname
            if boost_note.folder_pathname:
                full_pathname += boost_note.folder_pathname
            tags.append(full_pathname.replace(" ", "_"))
        return tags

    @staticmethod
    def _get_content_from_boost_note(boost_note, markdown, title):
        safe_content = boost_note.content.replace("\n", "\r\n")
        if not title:
            return safe_content
        else:
            return (("# " if markdown else "")
                    + boost_note.title
                    + "\r\n\r\n"
                    + safe_content)

    def _win_safe_txt_filename(self):
        safe_title = self._title
        for c in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            safe_title = safe_title.replace(c, '_')
        return safe_title + ".txt"

    class Collection:
        def __init__(self):
            self.active_notes: list[SimpleNote] = []
            self.trashed_notes: list[SimpleNote] = []

        def _add_note(self, note: SimpleNote):
            if note.deleted:
                self.trashed_notes.append(note)
            else:
                self.active_notes.append(note)

        @classmethod
        def from_boost_notes(cls,
                             boost_notes: set[BoostNote],
                             markdown: bool = True,
                             title: bool = True) -> __class__:

            snc = cls()

            for note in boost_notes:
                snc._add_note(
                    SimpleNote._from_boost_note(note,
                                                markdown=markdown,
                                                title=title))
            return snc

        def as_dict(self) -> dict:
            full_collection = {
                "activeNotes": [
                    note._as_dict() for note in self.active_notes],
                "trashedNotes": [
                    note._as_dict() for note in self.trashed_notes]}

            return dict(full_collection)

        def to_json(self) -> str:
            return SimpleNote.ENCODER.encode(self.as_dict())

        def _to_flat_string_dict(self) -> dict[str, str]:

            active_streams = {note._win_safe_txt_filename():
                              note.content
                              for note in self.active_notes}
            trashed_streams = {"trash/" + note._win_safe_txt_filename():
                               note.content
                               for note in self.trashed_notes}
            source = {"source/notes.json":
                      SimpleNote.Collection.to_json(self)}

            return {**active_streams, **trashed_streams, **source}

        def _to_zip_bytestream(self) -> BytesIO:
            archive = BytesIO()
            stream = self._to_flat_string_dict()

            with zipfile.ZipFile(archive, 'w') as zip_archive:
                with zip_archive.open("trash/", 'w') as t:
                    t.close()
                with zip_archive.open("source/", 'w') as t:
                    t.close()

                for filename, content in stream.items():
                    with zip_archive.open(filename, 'w') as f:
                        f.write(bytes(content, 'utf-8'))

            return archive

        def export_zip(self,
                       filename: str = "notes.zip",
                       target_dir = ""):

            archive: BytesIO = self._to_zip_bytestream()
            cwd = os.getcwd()
            os.chdir(target_dir)
            if os.path.exists(filename):
                i = 1
                while os.path.exists(f"({i}) {filename}"):
                    i += 1
                filename = f"({i}) {filename}"
            with open(filename, "wb") as f:
                f.write(archive.getbuffer().tobytes())
            os.chdir(cwd)
