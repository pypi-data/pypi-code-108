"""
test_debugMe.py

Your name: Peter Mawhorter
Your username: pmwh
Submission date: 2022-1-23

Provided tests for debugMe file.
"""

import optimism as opt

m = opt.testFile("debugMe.py")
m.case()
m.provideInputs('5', '12', '')
m.checkOutputLines(
    "Let's practice some math!",
    'Enter an integer between 1 and 20: 5',
    'Enter another integer between 1 and 20: 12',
    '',
    'The numbers you entered are 5 and 12',
    'The larger number is 12',
    'The smaller number is 5',
    'These bars show how big they are:'
    '=' * 5,
    '=' * 12,
    '',
    '[Addition] What is 5 + 12 ? ',
    '[Addition] The answer is: 17',
    ''
)
