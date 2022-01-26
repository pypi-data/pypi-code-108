import sys
# this needs to be done again, otherwise the default sys.path will include an empty element after IPython starts
sys.path=[p for p in sys.path if len(p) > 0]
