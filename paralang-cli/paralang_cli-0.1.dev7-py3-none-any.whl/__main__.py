# coding=utf-8
""" Entry file for the CLI - Runs the default 'para' CLI if called directly """
from paralang_base.compiler import ParaCompiler


__all__ = [
    "RUNTIME_COMPILER"
]

RUNTIME_COMPILER: ParaCompiler = ParaCompiler()

if __name__ == "__main__":
    from .scripts.para import cli_run
    cli_run()
