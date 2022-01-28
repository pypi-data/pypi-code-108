def add(num1, num2):
  sum = num1+num2
  print('sum of '+str(num1)+' and '+str(num2)+' is '+str(sum))

def subtract(num1, num2):
  diff = num1-num2
  print('difference between '+str(num1)+' and '+str(num2)+' is '+str(diff))

def multiply(num1, num2):
  prod = num1*num2
  print('product of '+str(num1)+' and '+str(num2)+' is '+str(prod))

def divide(num1, num2):
  print('dividend is '+str(num1))
  print('divisor is '+str(num2))
  ans = int(num1)/int(num2)
  print('division of '+str(num1)+' and '+str(num2)+' is '+str(ans))