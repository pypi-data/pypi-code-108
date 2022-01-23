from params import *
from calc import calcs

firstname = fn()
lastname = ln()
m = mass()
h = height()
bmi = calcs(m,h)


if 16 <= bmi < 25:
    print(f"\n{firstname}, თქვენი bmi არის {bmi} და თქვენი წონა ნორმის ფარგლებშია")
elif 25 <= bmi < 30:
    print(f"\n{firstname}, თქვენი bmi არის {bmi} და თქვენ გაქვთ ითვლებით ჭარბწონიანად")
elif 30 <= bmi < 35:
    print(f"\n{firstname}, თქვენი bmi არის {bmi} და თქვენ გაქვთ პირველი ხარისხის სიმსუქნე")
elif 35 <= bmi < 40:
    print(f"\n{firstname}, თქვენი bmi არის {bmi} და თქვენ გაქვთ მეორე ხარისხის სიმსუქნე")