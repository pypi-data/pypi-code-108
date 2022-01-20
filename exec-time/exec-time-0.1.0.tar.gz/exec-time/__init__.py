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