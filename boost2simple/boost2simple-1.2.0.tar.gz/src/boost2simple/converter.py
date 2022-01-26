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

from boost2simple.notes.boostnote import BoostNote
from boost2simple.notes.simplenote import SimpleNote


class Converter:
    def __init__(self,
                 boost_note_dir,
                 simple_note_dir,
                 markdown=True,
                 show_title=True):
        self.boost_note_dir = boost_note_dir
        self.simple_note_dir = simple_note_dir
        self.markdown = markdown
        self.title = show_title
        self.status = "No BoostNotes could be converted."

    def convert_and_export(self) -> int:
        boost_notes = BoostNote.Collection.from_path(self.boost_note_dir).notes
        print(f"{len(boost_notes)} BoostNotes found.")

        simple_notes = SimpleNote.Collection.from_boost_notes(boost_notes,
                                                              markdown=self.markdown,
                                                              title=self.title)
        simple_notes.export_zip(target_dir=self.simple_note_dir)

        count = (len(simple_notes.active_notes) + len(simple_notes.trashed_notes))
        if count > 0:
            self.status = f"Successfully converted and zipped {count} of {len(boost_notes)} notes!"
            return 0
        else:
            return 1
