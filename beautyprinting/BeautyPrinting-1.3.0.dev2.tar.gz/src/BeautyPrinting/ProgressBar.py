from colorama import Fore, init
import enlighten
import time
import os
init(True)


def loading_bar(text: str='', items: int=0, sleep: float=0.01, color: str='cyan', rounds: int=2, function: object=None, *args, **kwargs) -> None:
    """这是loading_bar函数，为您提供了一个炫酷加载进度条。预览效果如下：

       正在加载中......35%[70/200]

       text：您希望在加载时显示的提示语；

       items：您希望加载的次数；

       sleep：您希望每次加载后等待的时间；

       color：您希望进度条显示的颜色。可能的值为：

           default（系统默认）

           black（黑色）

           white（白色）

           red（红色）

           green（绿色）

           yellow（黄色）

           blue（蓝色）

           pink（梅红色）

           cyan（浅蓝色）

       rounds：百分数现实的精度；

       function：您希望在每次加载时执行的函数；

       args和kwargs：您希望传递给函数的参数。"""

    if color == 'default':
        color = Fore.RESET
    elif color == 'black':
        color = Fore.BLACK
    elif color == 'white':
        color = Fore.WHITE
    elif color == 'red':
        color = Fore.RED
    elif color == 'green':
        color = Fore.RESET
    elif color == 'yellow':
        color = Fore.YELLOW
    elif color == 'blue':
        color = Fore.BLUE
    elif color == 'pink':
        color = Fore.MAGENTA
    elif color == 'cyan':
        color = Fore.CYAN
    else:
        color = ''
    
    for item in range(1, items+1):
        if function:
            function(*args, **kwargs)
        os.system('clear')
        per = str(round((item/items)*100, rounds)) + '%'
        print(f'{text}{color}{per}[{item}/{items}]')
        time.sleep(sleep)
    os.system('clear')


def enlighten_loading_bar(text: str='Loading......', items: int=0, sleep: float=0.01, color: str='white', function: object=None, *args, **kwargs) -> None:
    """这是enlighten_loading_bar函数，为您提供了一个enlighten炫酷加载进度条。您可以在加载进度条的同时打印其他内容，超赞！

       text：您希望在加载时显示的提示语；

       items：您希望加载的次数；

       sleep：您希望每次加载后等待的时间；

       color：您希望进度条显示的颜色。

       function：您希望在每次加载时执行的函数；

       args和kwargs：您希望传递给函数的参数。"""

    pbar = enlighten.Counter(total=items, desc=text, unit='ticks', color=color)
    for num in range(items):
        if function:
            function(*args, **kwargs)
        time.sleep(sleep)
        pbar.update()


def enlighten_loading_bars(numbers: int=1, list: bool=False, text: str='Loading......', texts: list=None, items: int=0, item_list: list=None, sleep: float=0.01, sleep_list: list=None, color: str='white', colors: list=None):
    """这是enlighten_loading_bars函数，为您提供了一个enlighten炫酷加载进度条。您可以同时打印多个进度条，超赞！

       numbers：您希望显示的加载条数量；

       list：决定是否使用列表为参数赋值。如果为False，则使用text、items、sleep、color参数为所有进度条提供一样的初始化。如果为True，则使用texts、item_lists、sleep_lists、colors为每个进度条提供不同的初始化。

       text：您希望在加载时显示的提示语；

       texts：加载的提示语列表；

       items：您希望加载的次数；

       item-list：您希望加载的次数列表；

       sleep：您希望每次加载后等待的时间；

       sleep-list：您希望每次加载后等待的时间列表；

       color：您希望进度条显示的颜色。
       
       colors：您希望进度条显示的颜色列表。"""

    manager = enlighten.get_manager()
    for which in range(numbers):
        if list:
            bar = manager.counter(total=item_list[which], desc=texts[which], unit='ticks', color=colors[which])
            for num in range(item_list[which]):
                time.sleep(sleep_list[which])
                bar.update()
        else:
            bar = manager.counter(total=items, desc=text, unit='ticks', color=color)
            for num in range(items):
                time.sleep(sleep)
                bar.update()