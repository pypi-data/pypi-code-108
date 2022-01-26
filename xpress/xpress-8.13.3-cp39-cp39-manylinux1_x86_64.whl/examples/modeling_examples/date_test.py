'''******************************************************
   Python NI Examples

   File date_test.py

   (c) 2018 Fair Isaac Corporation
*******************************************************'''

from __future__ import print_function
import datetime as dt

today = dt.date.today()
d = dt.date(2000, 1, 1)
print("today is: ", today)
print("d is    : ", d)

if d == today:
    print('d and today are the same')
elif d < today:
    print("d is before today")
else:
    print("d is after today")

# Access some detailed info
print("The current year is ", today.year)
