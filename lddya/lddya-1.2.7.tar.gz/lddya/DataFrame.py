class N_Base():
    '''
        一个N(N<9)进制数(正数)，由于只为做调度问题的状态码，因此，仅考虑了N<9的情况。
    '''
    def __init__(self,num_0 = '0',base = 2) -> None:
        '''
            Function
            ---------
            对一个n(n<9)进制数进行初始赋值。

            Params
            ------
            num_0 : str --> n进制下的数值
            base  : int --> 进制 
        '''
        self.value = num_0 if type(num_0)==str else str(num_0)
        self.base  = base
    
    def add(self,delta = 1):
        '''
            Function
            --------
            对该n进制数进行加法操作。

            Params
            ------
            delta  : int --> 要加的数(十进制)，可以是负数，但不能导致该n进制数进行运算后成了负数。
        '''
        e1 = self.eval()+delta
        self.value = ''
        while True:
            a1 = e1//self.base
            a2 = e1%self.base
            self.value = str(a2) + self.value
            if a1 == 0:
                break
            e1 = a1
    def eval(self):
        '''
        Function
        --------
        对该n进制数进行求值并返回。
        '''
        real_value = 0
        for i in range(1,len(self.value)+1):
            real_value += pow(self.base,i-1)*eval(self.value[-i])
        return real_value
