#!/usr/bin/env python
# coding: utf-8

# # 多线程
# 
# 线程是一种对于非顺序依赖的多个任务进行解耦的技术。多线程可以提高应用的响应效率，当接收用户输入的同时，保持其他任务在后台运行。一个有关的应用场景是，将 I/O 和计算运行在两个并行的线程中。

# ```python
# import threading, zipfile
# 
# class AsyncZip(threading.Thread):
#     def __init__(self, infile, outfile):
#         threading.Thread.__init__(self)
#         self.infile = infile
#         self.outfile = outfile
# 
#     def run(self):
#         f = zipfile.ZipFile(self.outfile, 'w', zipfile.ZIP_DEFLATED)
#         f.write(self.infile)
#         f.close()
#         print('Finished background zip of:', self.infile)
# 
# background = AsyncZip('mydata.txt', 'myarchive.zip')
# background.start()
# print('The main program continues to run in foreground.')
# 
# background.join()    # Wait for the background task to finish
# print('Main program waited until background was done.')
# ```
# 
# 多线程应用面临的主要挑战是，相互协调的多个线程之间需要共享数据或其他资源。为此，threading 模块提供了多个同步操作原语，包括线程锁、事件、条件变量和信号量。
# 
# 尽管这些工具非常强大，但微小的设计错误却可以导致一些难以复现的问题。因此，实现多任务协作的首选方法是将所有对资源的请求集中到一个线程中，然后使用 {mod}`queue` 模块向该线程供应来自其他线程的请求。 应用程序使用 {class}`~queue.Queue` 对象进行线程间通信和协调，更易于设计，更易读，更可靠。

# In[ ]:




