"""
Authors: Peter Mawhorter
Consulted:
Date: 2121-11-6
Purpose: Demonstration of variable-definition-based grading.
"""

# String value
var1 = "val1"

# Another string value
var2 = "val2"

# List value w/ other vars
var3 = [var1, var2]

# Recursive list value
var4 = [var3]
var4.append(var4)
