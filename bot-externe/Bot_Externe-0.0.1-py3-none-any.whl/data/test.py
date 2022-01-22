import socket
import sys
if __name__ == "__main__":
    print(sys.path)
    index = sys.path[0].split("\\").index("noyau_devII_2TM2")

    print(sys.path[0].split("\\")[:index+1])

