import time

def exec_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = function(*args, **kwargs) # executing function
        end_time = time.perf_counter()

        difference = str((end_time - start_time) * 1000) # their difference
        print(f"{function.__name__} function executed in : {difference} mil sec")

        return result
    
    return wrapper

def exec_time_for(function, time_in='seconds'):
    start_time = time.perf_counter()
    function()
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    
    if time_in == 'milliseconds':
        execution_time *= 1000
    elif time_in == 'seconds':
        pass
    elif time_in == 'minutes':
        execution_time /= 60
    else:
        raise Exception('exec_time_for() function only accepts ONE of (\'milliseconds\', seconds\', \'minutes\') as 2 positional parameter')
    
    return execution_time

def func():
    x = 0
    for i in range(1000000):
        x += 1

print(exec_time_for(func, time_in='sd'))