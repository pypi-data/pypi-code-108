#import subprocess
#
#subprocess.Popen(f'C:\Windows\system32\calc.exe')
#
#
#
#
#
#
#
#\ is a escape character. You have three options.
#
#1) use /. This, as a bonus works for linux as well:
# 'D:/xxx/xxxx/asd/asd.exe'
# 
#2) escape the backslash
# 'D:\\xxx\\xxxx\\asd\\asd.exe'
# 
#3) use raw strings:
#r'D:\xxx\xxxx\asd\asd.exe'





#import json 
#
#with open('/src/environment/data.json', 'r+') as f:
#    lst = json.load(f)
#    print(lst.index(bee))


#import pyfiglet
#  
#result = pyfiglet.figlet_format("fort", font = "small"  )
#print(result)
