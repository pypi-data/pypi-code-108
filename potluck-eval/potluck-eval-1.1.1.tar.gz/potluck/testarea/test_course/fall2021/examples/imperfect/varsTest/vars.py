"""
Authors: Peter Mawhorter
Consulted:
Date: 2121-11-6
Purpose: Imperfect solution for vars test.
"""

# String value
var1 = "val1" # correct

# Another string value
var2 = "val3" # wrong

# List value w/ other vars
var3 = [var1, var2] # wrong by proxy

# Recursive list value
extra = [["val1", "val2"]]
extra.append(extra)
var4 = [["val1", "val2"], extra]
# subtly wrong but equivalent recursive structure
