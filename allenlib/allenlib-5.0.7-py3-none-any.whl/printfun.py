import time
def printfun(a):
    for i in range(len(a)):
        print(a[i],end='',flush=True)
        time.sleep(0.1)
    print()