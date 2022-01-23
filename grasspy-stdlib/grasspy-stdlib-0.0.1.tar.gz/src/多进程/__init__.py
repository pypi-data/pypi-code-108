从 multiprocessing 导入 *

类 〇进程(Process):
    """
    进程对象代表在单独进程中运行的活动
    """
    套路 __init__(分身, 组=None, 目标=None, 名称=None,
                 参数=(), 关键词参数={}, *, 守护=None):
        super().__init__(group=组, target=目标, name=名称,
                 args=参数, kwargs=关键词参数, daemon=守护)

    套路 run(分身):
        分身.运行()

    套路 运行(分身):
        """
        要在进程中运行的方法
        """
        如果 分身._target:
            分身._target(*分身._args, **分身._kwargs)      

    套路 开始(分身):
        """
        启动进程
        """
        分身.start()
    
    套路 终止(分身):
        """
        终止进程; 发送 SIGTERM 信号或使用 TerminateProcess()
        """
        分身.terminate()
    
    套路 杀死(分身):
        """
        终止进程; 发送 SIGKILL 信号或使用 TerminateProcess()
        """
        分身.kill()
    
    套路 并入(分身, 超时=None):
        """
        等待直到进程终止
        """
        分身.join(timeout=超时)
    
    套路 是活着(分身):
        """
        返回进程状态 - 是否还活着
        """
        返回 分身.is_alive()

    套路 关闭(分身):
        """
        关闭进程对象. 此方法会释放进程对象持有的资源.
        如果进程仍在运行, 调用此方法会出错.
        """
        分身.close()

    @property
    套路 名称(分身):
        返回 分身.name

    @名称.赋值器
    套路 名称(分身, 名称):
        分身.name = 名称
    
    @property
    套路 守护(分身):
        返回 分身.daemon

    @守护.赋值器
    套路 守护(分身, 守护性):
        分身.daemon = 守护性
    
    @property
    套路 授权密钥(分身):
        返回 分身.authkey

    @授权密钥.赋值器
    套路 授权密钥(分身, 密钥):
        分身.authkey = 密钥
    
    @property
    套路 退出码(分身):
        返回 分身.exitcode
    
    @property
    套路 标识(分身):
        返回 分身.pid
    
    @property
    套路 哨兵(分身):
        返回 分身.sentinel

当前进程 = current_process
活动子进程列表 = active_children
父进程 = parent_process
cpu数 = cpu_count


〇锁 = Lock

套路 〇池(进程数=空, 初始化函数=空, 初始化参数=(),
        子进程最大任务数=空) -> Pool:
    返回 Pool(进程数, 初始化函数, 初始化参数, 子进程最大任务数)

〇队列 = Queue
〇可并入队列 = JoinableQueue
〇简单队列 = SimpleQueue

套路 〇栅栏(进程数, 动作=空, 超时=空):
    返回 Barrier(进程数, 动作, 超时)

套路 〇有界信号量(值):
    返回 BoundedSemaphore(值)

套路 〇信号量(值):
    返回 Semaphore(值)

套路 〇条件(锁):
    返回 Condition(锁)

〇事件 = Event

