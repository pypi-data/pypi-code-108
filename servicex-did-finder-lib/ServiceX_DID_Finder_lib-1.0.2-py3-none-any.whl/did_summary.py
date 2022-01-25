# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from typing import Any, Dict


class DIDSummary:
    def __init__(self, did: str):
        '''__init__ Track files we are reporting back to the system

        Object that tracks statistics about the files we are injecting for processing
        into Servicex.

        Args:
            did (string): The DID of the dataset we are tracking
        '''
        self._did = did
        self._total_bytes = 0
        self._total_events = 0
        self._files = 0
        self._files_skipped = 0

    def __str__(self):
        return ("DID {} - {:.0f} Mb {} Events in {} files ({} skipped)".format(
            self._did,
            self._total_bytes / 1e6,
            self._total_events,
            self._files,
            self._files_skipped))

    @property
    def file_count(self) -> int:
        return self._files

    @property
    def files_skipped(self) -> int:
        return self._files_skipped

    @property
    def total_bytes(self) -> int:
        return self._total_bytes

    @property
    def total_events(self) -> int:
        return self._total_events

    def _accumulate(self, file_record: Dict[str, Any]):
        '''accumulate Update statistics counters

        Track total file size and events

        Args:
            file_record (Dict[str, Any]): Statistics reported back from loading
                                          a particular for.
        '''
        file_size_key = 'file_size' if 'file_size' in file_record else 'bytes'
        file_events_key = 'file_events' if 'file_events' in file_record else 'events'

        self._total_bytes += int(file_record[file_size_key] or 0)
        self._total_events += int(file_record[file_events_key] or 0)

    def add_file(self, file_record: Dict[str, Any]):
        '''add_file Update all stats with new file

        Count number of files and track data for the file

        Args:
            file_record (Dict[str, Any]): Statistics for a particular file
        '''
        self._files += 1
        self._accumulate(file_record)
