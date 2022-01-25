import os
import time
def wait_login():
    while True:
        t = os.popen('who').read().strip()
        if len(t)<2:
            time.sleep(1)
        else:
            break
    t = t.split()
    return t
def main():
    s = wait_login()
    print(s)
if __name__=='__main__':
    main()