import Rahimcalc as r
def sample():
    a=int(input("Enter the a:"))
    b=int(input("Enter the b:"))
    print(r.sum(a,b))
    print(r.sub(a,b))
    print(r.mul(a,b))
    print(r.complex(a,b))
    print(r.div(a,b))
if __name__=='__main__':
    sample()
