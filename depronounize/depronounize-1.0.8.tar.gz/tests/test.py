
from depronounize import replace_pronouns


input = """
I went to the store to buy jam, but they were out of it.
The sun went down and it was an amazing red fireball.  It was beautiful.
I visited my inlaws to grab dinner.  It was delicious and they were very courteous.
"""

print("Input:\n%s\n\n" % input)

output = replace_pronouns(input)

print("Output:\n%s" % output)

