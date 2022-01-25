__author__ = "Tomasz Rybotycki"

"""
    This script contains quick test ground of the generator.
"""

from ..src.GuanCodeGenerator import GuanCodeGenerator

for code in GuanCodeGenerator.generate_guan_codes([4, 0, 3, 3, 3]):
    print(code)
