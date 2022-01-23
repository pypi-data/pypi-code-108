"""
interactive.py

Your name: Im Perfect
Your username: imperfect
Submission date: 2021-7-1
"""

# PART 1: Get Input
# Gather input from the user about time spent on different categories of
# activities during each week. Since inputs are "strings", convert them
# immediately to int or float values. There should be a total of 6 questions.

name = input('What is your name? ')
dogs = input('How many dogs do you have? ')
diet = input('On average, how much does each dog eat per day (in cups)? ')
density = input(
    'On average, how much does one cup of dog food weigh (in lbs)? '
)

dogCount = int(dogs)
dietCups = float(diet)
densityLbs = float(density)

lbsPerWeek = dietCups * densityLbs * dogs


print(
    "Your dog(s) eat "
  + str(round(lbsPerWeek, 2))
  + "lbs of dog food every week."
)
