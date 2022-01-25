"""
Authors: Peter Mawhorter
Consulted:
Date: 2121-11-6
Purpose: Demonstration of variable-definition-based grading.
"""

# String value
var1 = "val" + "1"

# Another string value
var2 = "val" + "2"

# List value w/ other vars
var3 = ["val1", "val2"]

# Recursive list value
final = [["val1", "val2"]]
final.append(final)
var4 = final
