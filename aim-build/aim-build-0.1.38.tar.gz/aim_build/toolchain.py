from dataclasses import dataclass


@dataclass
class ToolChain:
    cxx_compiler: str
    c_compiler: str
    archiver: str
