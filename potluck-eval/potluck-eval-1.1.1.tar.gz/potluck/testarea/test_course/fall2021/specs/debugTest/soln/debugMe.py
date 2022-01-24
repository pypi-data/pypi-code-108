"""
debugMe.py

Your name: Peter Mawhorter
Your username: pmwh
Submission date: 2021-6-22
"""

# Buggy debugMe.py for potluck system testing.
# Fix the bugs in this file so that its output matches what's shown in
# the problem set.

print("Let's practice some math!")

# Get inputs and convert them to integers:
firstNum = input('Enter an integer between 1 and 20: ')
firstNum = int(firstNum)
secondNum = input('Enter another integer between 1 and 20: ')
secondNum = int(secondNum)

# Print a blank line:
print()

# Print some info about the numbers:
print('The numbers you entered are', firstNum, 'and', secondNum)
print('The larger number is', max(firstNum, secondNum))
print('The smaller number is', min(firstNum, secondNum))
print('These bars show how big they are:')
print('=' * firstNum)
print('=' * secondNum)
print() # Blank line

# Test sum:
prompt = '[Addition] What is ' + str(firstNum) + '+' + str(secondNum) + ' ? '
input(prompt) # Note: we intentionally don't store or check the result
sumResult = firstNum + secondNum
print('[Addition] The answer is:', sumResult)
print() # Blank line
