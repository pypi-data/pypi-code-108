class JavaVersion:
    def __init__(self, major: int, minor: int, build: str):
        self._major = major
        self._minor = minor
        self._build = build

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def build(self):
        return self._build

    def get_build_dir(self):
        return f"jdk{self._major}u{self._minor}-b{self._build}"

    def get_file_sufix(self):
        return f"{self._major}u{self._minor}b{self._build}"
