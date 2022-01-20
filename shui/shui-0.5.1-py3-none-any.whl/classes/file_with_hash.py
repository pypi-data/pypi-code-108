"""Class to contain file information for a file and its associated hash file"""
import hashlib


class FileWithHash:
    """Class to contain file information for a file and its associated hash file"""

    def __init__(self, file_, hashfile):
        if not hashfile.is_hashfile:
            raise ValueError(f"{hashfile.name} is not a hashfile!")
        if not hashfile.is_hash_for(file_):
            raise ValueError(
                f"{hashfile.name} is not the correct hashfile for {file_.name}!"
            )
        self.file = file_
        self.hashfile = hashfile

    def __iter__(self):
        yield self.file
        yield self.hashfile

    def remove(self):
        """Remove tarball and SHA512 hash"""
        for fileinfo in self:
            fileinfo.remove()

    def verify(self):
        """Verify that a file matches its SHA512 hash"""
        # Get the file hash
        file_hash = hashlib.sha512()
        buffer_size = 524288  # read in chunks of 512kb
        with self.file.path.open("rb") as input_file:
            input_bytes = True
            while input_bytes:
                input_bytes = input_file.read(buffer_size)
                file_hash.update(input_bytes)
        calculated_hash = file_hash.hexdigest().lower()
        # Read the reference hash
        with self.hashfile.path.open("r") as input_hash:
            reference_hash = (
                "".join(input_hash.readlines())
                .replace("\n", " ")
                .replace(" ", "")
                .split(":")[1]
                .strip()
                .lower()
            )
        return calculated_hash == reference_hash
