import hw_fortran_t as hw
#from hw_wwj import hw_fortran_t as hw

def test():
    a=1.0
    b=2.0
    print('call func hw1')
    hw.hw1(a,b)
    print('******************') 
    print('call func hw2')
    hw.hw2(a,b)
    print('******************') 
    print('call func hw3') 
    c=hw.hw3(a,b)
    print('c',c)


      
