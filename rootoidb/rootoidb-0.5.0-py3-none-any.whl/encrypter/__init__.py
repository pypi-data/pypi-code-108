import string
def caesar_cipher(text,default_shift=13):
    '''
    this is function works on the principle of 
    the caesar cipher which is the basic encrypt 
    algorithum. 
    
    it takes 1 arguments which is the text that
    you want to encrypt. it takes one parameter 
    names as default_shift which is set 13.
    make sure this parameters should be int

    it works on the on the principle of shifting 
    the aplhabets in the text by the default_shift
    parameter. 
    '''
    __encrypts1 = [list(string.printable)[list(string.printable).index(i)+default_shift] for i in str(text)]
    __encrypts2 = ''
    for i in __encrypts1:
        __encrypts2 += str(i)
    return __encrypts2