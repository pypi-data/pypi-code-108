from timer import ManualTimer

timer = ManualTimer("Test")
timer.start()
print(timer.start_time())

for i in range(1000):
    print(i)
    
timer.stop()
print(timer.elapsed_time())
print(timer.end_time())