import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "logs", "server_dist", "unit_tests"],
}
setup(
    name="mess_server",
    version="0.8.8",
    description="mess_server",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server_run.py',
                            base='Win32GUI',
                            targetName='server_dist.exe',
                            )]
)
