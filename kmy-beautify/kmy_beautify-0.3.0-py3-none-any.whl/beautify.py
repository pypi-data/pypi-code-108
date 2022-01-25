from os import system
from random import choice
from time import sleep
from timeit import default_timer
from art import *
from shell import shell
from stringcolor import cs


class Loading:
    def __init__(self):
        global color,bg_color;
        color = None;
        bg_color = None;

    def loading(self,timeout:int or float=0.5,clor:str='blue',bg:str=None):
        '''
        timeout -> int/float -> default 0.5
        clor -> str -> default blue
        bg -> str -> default None
        '''
        global color,bg_color;
        color = clor;
        bg_color = bg;
        def distv(c,b):
            for i in range(5):
                system('clear')
                dsview = f"{text2art(f'{i+1*5}0%','fancy5')} {art(f'loading{i+1}')} {text2art('loading...','fancy90')}"
                print(cs(dsview, c,b))
                sleep(timeout)
        distv(color, bg_color)

    def show(self,callback):
        '''
        return callback
        '''
        self.strt = default_timer()
        self.callback = callback
        self.stop = default_timer()
        system('clear')
        dsview = f"{text2art('100%','fancy5')} {art('loading6')} {text2art('complete!','fancy90')}"
        print(cs(dsview, color,bg_color))
        sleep(float(f'{self.strt - self.stop}'.strip('-')))
        system('clear')
        return self.callback;


class Beautify:
    
    def colors(self,random:bool=False) -> bool:
        '''
        random -> type boolean
        True -> return random color
        False -> return list color
        '''
        if random == True:
            return choice((
                'blue', 'blueviolet', 'lightblue', 'lightseagreen', 'limegreen', 
                'magenta', 'maroon', 'mediumseagreen', 'mediumslateblue', 'orange', 
                'orangered', 'olivedrab', 'cyan', 'crimson', 'saddlebrown', 'darkcyan', 
                'darkgreen', 'darkolivegreen', 'darkslategrey', 'darkturquoise', 
                'darkviolet', 'darkgrey', 'darkorchid'))
        else:
            return (
                'blue', 'blueviolet', 'lightblue', 'lightseagreen', 'limegreen', 
                'magenta', 'maroon', 'mediumseagreen', 'mediumslateblue', 'orange', 
                'orangered', 'olivedrab', 'cyan', 'crimson', 'saddlebrown', 'darkcyan', 
                'darkgreen', 'darkolivegreen', 'darkslategrey', 'darkturquoise', 
                'darkviolet', 'darkgrey', 'darkorchid')

    def txtclr(self,text:str='hello worlds!',color='#00e6e6',bg=None,**kwargs):
        '''
        text color params:
        text -> type str -> default "hello worlds!"
        color -> type str 
        bg -> type str 
        font -> type str -> view font list https://github.com/sepandhaghighi/art/blob/master/FontList.ipynb - https://www.4r7.ir/FontList.html
        chr_ignore -> boolean
        sep -> type str -> separator
        decoration -> view decoration list https://github.com/sepandhaghighi/art/blob/master/DecorList.ipynb - https://www.4r7.ir/DecorList.html
        '''
        if not kwargs.keys():
            return cs(text2art(text,'fancy90'), color,bg)
        else:
            if 'font' in kwargs.keys():
                return cs(text2art(text,**kwargs), color,bg)
            else:
                return cs(text2art(text,'fancy90',**kwargs), color,bg)

    def banner(self,name:str='eagle2',color:str='blue',bg:str=None) -> str:
        try:
            shell('tar -xzvf beautify/banner.tar.gz ')
            with open(f'banner/{name}.txt','r') as f:
                return cs(f.read(), color,bg)
        except:
            return NameError(f'Invalid > {name}')

    def print_menu(self,add_menu:list[str]=None,separator='*',rw_num=True,color:str='white',bg:str=None):
        '''
        Params:
        add_menu -> type list -> default None
        separator -> type str -> default *
        rw_num -> type boolean -> default True
        color -> type str -> default white,available hex/rgb/name color
        bg -> type str -> default None,available hex/rgb/name color
        '''
        self.line = [];
        if add_menu == None:print(cs('please add menu!','red'))
        else:
            for i in add_menu:self.line.append(len(i))
            self.separator = f'{separator*sorted(self.line)[-1]*2}';
            print(cs(f'\n{self.separator}',color,bg))
            for (i,d) in enumerate(add_menu):
                if rw_num == True:
                    abstr = f'0{i+1} - {d}'
                    absbr = f'{i+1} - {d}'
                    if i+1 < 10:
                        rst = int(len(self.separator)) - int(len(abstr)) - 1
                        print(cs(f'{abstr}'+' '*rst+'|', color,bg))
                    else:
                        rst = int(len(self.separator)) - int(len(absbr)) - 1
                        print(cs(f'{absbr}'+' '*rst+'|', color,bg))
                else:
                    print(cs(d, color,bg))
                print(cs(self.separator,color,bg))

