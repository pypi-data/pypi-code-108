"""
Code to compile configs and layouts into DLPoly inputs
Main interface
"""

from .builder import build
from .cli import get_command_args


def main():
    """Run main config buider  """
    argList = get_command_args()
    for source in argList.sources:
        with open(source, 'r') as sourceFile:
            system = build(sourceFile)
            system.config.write(argList.output.strip() + '.config')
            system.field.write(argList.output.strip() + '.field')


if __name__ == "__main__":
    main()
