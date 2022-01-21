#!/usr/bin/env python
# -*- coding:utf-8 -*-

from kombu import Exchange, Queue

# https://www.cnblogs.com/yunlongaimeng/p/11121294.html

# 该框架建议使用celery=4.4.7版本

BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# 任务失败或超时自动确认，默认为True
CELERY_ACKS_ON_FAILURE_OR_TIMEOUT = False

# 任务完成之后再确认
CELERY_ACKS_LATE = True

# worker进程崩掉之后拒绝确认
CELERY_REJECT_ON_WORKER_LOST = True

# 设置默认不存结果(保存在redis内),如果需要保持结果，请在任务中单独指定。@app.task(ignore_result=False)
CELERY_IGNORE_RESULT = True

# 设置结果的保存时间
CELERY_TASK_RESULT_EXPIRES = 24 * 3600

CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，防止OOM

CELERY_QUEUES = (
    Queue("celery", Exchange("celery", type='direct'), routing_key="celery"),
    Queue("for_task_A", Exchange("for_task_A", type='direct'), routing_key="for_task_A"),
    Queue("for_task_B", Exchange("for_task_B", type='direct'), routing_key="for_task_B")
)

CELERY_ROUTES = {
    'tasks.task_x': {"queue": "celery"},
    'tasks.taskA': {"queue": "for_task_A", "routing_key": "for_task_A"},
    'tasks.taskB': {"queue": "for_task_B", "routing_key": "for_task_B"}
}

# 新增加的定时任务部分：celery默认时区为世界标准时间，比东八区慢8小时
# https://www.cnblogs.com/belingud/p/11716303.html
CELERY_TIMEZONE = 'Asia/Shanghai'

# CELERYBEAT_SCHEDULE = {
#     'taskA_schedule' : {
#         'task':'tasks.taskA',
#         'schedule':2,
#         'args':(5,6)
#     },
#     'taskB_scheduler' : {
#         'task':"tasks.taskB",
#         "schedule":10,
#         "args":(10,20,30)
#     },
#     'add_schedule': {
#         "task":"tasks.add",
#         "schedule":5,
#         "args":(1,2)
#     }
# }
