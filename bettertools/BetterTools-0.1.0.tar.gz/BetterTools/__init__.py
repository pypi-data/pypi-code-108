import os
import time


def initLogs(date, write_file, text):
    """
    make global : -> now that represent the time that you choose using date argument,
                  -> file that is the file where you want to write your logs
                  -> TextLogs which is the text that you want to write in your logs by default
    If you don't want to setup one of these, you can pass the argument as ="", like:
        initLogs(date=["lot of things"], write_file="smt.txt", log_text="")
    """
    global now
    time_config = ""
    sep = False
    while len(date) != 0:
        
        if sep:
            if time_config == "":
                pass
            else:
                time_config += sep
        else:
            sep = ":"
                
        if date[0] == "day" or date[0] == "d":
            time_config += "%e"
            
        elif date[0] == "month" or date[0] == "m":
            time_config += "%m"
            
        elif date[0] == "year" or date[0] == "y":
            time_config += "%Y"
            
        elif date[0] == "hour" or date[0] == "h":
            time_config += "%H"
            
        elif date[0] == "minute" or date[0] == "M":
            time_config += "%M"
            
        elif date[0] == "second" or date[0] == "s":
            time_config += "%S"
            
        elif date[0] == "current time":
            if sep:
                time_config += f"%H{sep}%M{sep}%S"
            else:
                time_config += "%H:%M:%S"
                
        elif date[0] == "current date":
            if sep:
                time_config += f"%e{sep}%m{sep}%Y"
            else:
                time_config += "%e:%m:%Y"
                
        elif date[0].startswith("sep"):
           sep = date[0][4:]
            
        else:
            time_config += date[0]
        
        date.pop(0)
    t = time.localtime()
    now = time.strftime(time_config, t)
    
    global file
    if write_file:
        file = write_file
        
    global TextLogs
    if text:
        TextLogs = text
    
def Btype(var, out=False):
    """
    Like type()function but return the name only name of a var like: int, not <class 'int'>
    But can print automatically, or return
    """
    if out:
        print(type(var).__name__)
    else:
        return type(var).__name__
    

def cls():
    """
    Function to clear console, work on Windows, MacOS and some other
    """
    if os.name in ('nt', 'dos'):
        os.system("cls")
    else:
        os.system("clear")


def Binput(message="", Input_type=str, error_message="", clear=False, delay=0,
           func=False, **kwargs):
    """
    I recommend to write all arguments if you want to callback a func,
    for the function arguments you have to assign var to values, like :
    Binput(message=..., ..., delay=..., func=function to callback, func_args="hahahahahaha", other_func_args="test")
    For the Input_type and func argument, you have to write them without ""
    """
    try:
        return Input_type(input(message))
    except:
        if clear:
            cls()
            
        if error_message:
            print(error_message)
            if delay > 0:
                time.sleep(delay)
        else:
            if delay > 0:
                time.sleep(delay)
            print(f"You didn't write an {Input_type.__name__} !")
            
        if func:
            func(**kwargs)
        

def Bprint(text, speed=0):
    """
    BetterPrint : print(text, speed=0)
    text can be a str, so it will print letters by letters the text, with a waiting time
    (speed) between
    Or text can be a list, you can put several words, the last one is the delay between every printing of items of your list 
    If you want to remove the last item just write your can put just before the delay (in your list) "repalce"
    ex: Bprint(["First item in my list", "an other one", "other", "replace", 2])
    """
    
    if Btype(text) == "list":   # if you want to write some words and replace them one by one,
                                # or add a delay between every words
        delay = 0
                                
        if Btype(text[-1]) == "int":
            delay = int(text[-1])
            text.pop(-1)
        
        if text[-1] == "replace":
            text.pop(-1)
            
            for i in text:
                blank = ""
                for _ in range(len(i)):
                    blank += " "
                p(blank, end="\r")
                for l in i:
                    p(l, end="", flush=True)
                    time.sleep(speed)
                
                if delay:
                    time.sleep(delay)
                p("", end="\r")
                
        else:
            for i in text:
                for l in i:
                    p(l, end="", flush=True)
                    time.sleep(speed)
                p(" ", end="")
                time.sleep(delay)
                
    else:
        for i in text:
            p(i, end="", flush=True)
            time.sleep(speed)

def logs(TextLogs, file, now):
    """
    You can use initLogs() to create now, file, and TextLogs variable to use this function
    Can print the logs if file="", or write them in the given file
    """
    if file:
        if now:
            with open(file, "a+") as f:
                if TextLogs:
                    f.write(now + TextLogs)
                else:
                    f.write(now)
    else:
        if now:
            print(now + TextLogs)
        else:
            print(TextLogs)
            
def loading(percentage: int):
    """
    create a loading print()
    the percentage need to be between 0 and 100
    ex: for i in range(1000000):
            loading(i/10000)
    """
    if percentage > 100 or percentage < 0:
        print(f"Percentage need to be between 0 and 100 !")
    else:
        load = ""
        for _ in range(int(percentage/10)):
            load += "██"
        for _ in range(20-len(load)):
            load += " "
        print(f"| {load} | {percentage}%", end="\r")
    if round(percentage) == 100:
        print(f"| {load} | 100%                                                                     ", end="\r")
        
        
# some function to make coding faster, but not more easier to understand
def i(text):
    """
    return to be able to do response = i("test")
    """
    return input(text)

def p(*objects, sep=' ', end='\n', flush=False):
    """
    Same as print() function, but it's call p()
    """
    print(*objects, sep=sep, end=end, flush=flush)
    