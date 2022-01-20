__version__ = '1.0.0'

result = []
entered = input("Enter a string\n")
currNum = 0
currStr = ""
for i in range(len(entered)):
  if entered[currNum] == "(" or entered[currNum] == ")":
    result.append(currStr)
    currStr = ""
  else:
    currStr = currStr + entered[currNum]
  currNum = currNum + 1
result.append(currStr)
print("\n" * 5)
for i in range(len(result)):
  print(result[i])