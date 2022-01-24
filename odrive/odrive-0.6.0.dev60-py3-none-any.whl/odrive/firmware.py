
import abc
import io
import json
import os
import tempfile
from typing import Iterator, Tuple

import odrive.cloud_api_base

class FirmwareFile(abc.ABC):
    @staticmethod
    def from_file(file):
        return _LocalFirmwareFile(file, {
            'app': 'default',
            'product': None,
            'channel': None,
            'release_commit': None
        })

    def __init__(self, json_data: dict):
        self.app = json_data['app']
        self.product = json_data['product']
        self.channel = json_data['channel']
        self.release_commit = json_data['release_commit']

    @abc.abstractmethod
    async def load(self):
        pass

    @abc.abstractmethod
    def as_buffer(self) -> bytes:
        pass

    @abc.abstractmethod
    def as_stream(self):
        pass

    @abc.abstractmethod
    def as_file(self):
        pass
    
    def get_flash_sections(self) -> Iterator[Tuple[int, bytes]]:
        """
        Scans the ELF file for sections to be loaded and returns them as an
        iterator of tuples (addr: int, content: bytes).
        """
        import elftools.elf.elffile
        
        with self.as_stream() as stream:
            elffile = elftools.elf.elffile.ELFFile(stream)
            for segment in elffile.iter_segments():
                if segment.header['p_type'] != 'PT_LOAD':
                    continue # skip no-load sections
                #print(segment.header)

                segment_vaddr = segment.header['p_vaddr']
                segment_addr = segment.header['p_paddr']
                segment_size = segment.header['p_filesz']

                for section in elffile.iter_sections():
                    if segment.section_in_segment(section):
                        section_addr = section.header['sh_addr'] - segment_vaddr + segment_addr # convert virt addr to phys addr
                        section_size = section.header['sh_size']

                        # Prune the section based on the containing segment's range.
                        # For instance the .bss section has a non-zero size even
                        # though it's in a segment with p_filesz==0.
                        if section_addr < segment_addr:
                            section_size -= segment_addr - section_addr # can get <0
                            section_addr = segment_addr
                        if section_addr + section_size > segment_addr + segment_size:
                            section_size = segment_addr + segment_size - section_addr
                        
                        if section_size <= 0:
                            continue # skip sections with zero bytes to load

                        yield section.name, section_addr, section.data()

class _LocalFirmwareFile(FirmwareFile):
    def __init__(self, path: str, json_data: dict):
        FirmwareFile.__init__(self, json_data)
        self.name = path
    
    async def load(self):
        pass

    def as_buffer(self):
        return self

    def as_stream(self):
        return open(self.name, 'rb')

    def as_file(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class _OnlineFirmwareFile(FirmwareFile):
    def __init__(self, api_base, url, json_data):
        FirmwareFile.__init__(self, json_data)
        self._api_base = api_base
        self._url = url
        self._content = None
    
    async def load(self):
        self._content = await self._api_base.download(self._url)

    def as_buffer(self):
        assert not self._content is None, "file not loaded"
        return self._content

    def as_stream(self):
        assert not self._content is None, "file not loaded"
        return io.BytesIO(self._content)

    def as_file(self):
        assert not self._content is None, "file not loaded"
        return _TempFile(self._content)

class _TempFile():
    def __init__(self, content: bytes):
        self._content = content
        self.name = None

    def __enter__(self):
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(self._content)
            self.name = fp.name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.name)
        self.name = None

class FirmwareIndex():
    @staticmethod
    async def from_server(api_base: odrive.cloud_api_base.APIBase):
        """
        Loads a firmware index from the firmware server.
        session must remain valid until the last call to file.load() on any
        of the index's returned files.
        """
        index_data = await api_base.call('GET', '/firmware/index')

        return FirmwareIndex([
            _OnlineFirmwareFile(api_base, 'https://cdn.odriverobotics.com/firmware/' + file['file'], file)
            for file in index_data['files']
        ])

    @staticmethod
    async def from_directory(path: str):
        """
        Loads a firmware index from the specified directory. The directory tree
        is scanned for files called "index.json".
        """
        def get_all_indices(basepath, *subpath):
            for name in os.listdir(os.path.join(basepath, *subpath)):
                fullname = os.path.join(basepath, *subpath, name)
                if os.path.isfile(fullname) and name == 'index.json':
                    yield subpath
                elif os.path.isdir(fullname):
                    yield from get_all_indices(basepath, *subpath, name)

        index = {"files": []}
        for subpath in get_all_indices(path):
            with open(os.path.join(path, *subpath, 'index.json')) as fp:
                subindex = json.load(fp)
            for file in subindex['files']:
                file['file'] = os.path.join(*subpath, file['file'])
            index["files"].extend(subindex['files'])
        
        return FirmwareIndex([
            _LocalFirmwareFile(os.path.join(path, file['file']), file)
            for file in index['files']
        ])

    def __init__(self, files):
        self.files = files

    def find_all(self, app: str = None, product: str = None, channel: str = None) -> Iterator[FirmwareFile]:
        """
        Returns all firmware files with the matching "app", "product" and
        "channel" property. If any of the arguments is None, it is ignored.
        """
        for file in self.files:
            if file.app != app:
                continue
            if file.product != product:
                continue
            if channel is None:
                match = (file.app, file.product) == (app, product)
            else:
                match = (file.app, file.product, file.channel) == (app, product, channel)
            if match:
                yield file

    def find(self, app: str, product: str, channel: str) -> FirmwareFile:
        """
        Returns exactly one FirmwareFile that matches the specified parameters.
        If zero or more than one matches were found, the function throws an
        Exception.
        """
        matches = list(self.find_all(app, product, channel))
        if len(matches) == 0:
            raise Exception("No matching firmware found.")
        elif len(matches) > 1:
            raise Exception("Multiple matches found.")
        return matches[0]
