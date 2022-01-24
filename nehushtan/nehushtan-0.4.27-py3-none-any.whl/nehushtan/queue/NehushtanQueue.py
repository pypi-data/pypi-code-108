import os
import time
from multiprocessing import Process

from nehushtan.queue.NehushtanQueueDelegate import NehushtanQueueDelegate
from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask
from nehushtan.queue.NehushtanQueueTaskDelegate import NehushtanQueueTaskDelegate
from nehushtan.queue.situation.NoNextTaskSituation import NoNextTaskSituation


class NehushtanQueue:
    def __init__(self, delegate: NehushtanQueueDelegate, task_delegate: NehushtanQueueTaskDelegate):
        """
        Since 0.4.11 add task_delegate
        """
        self.delegate = delegate
        self.task_delegate = task_delegate
        self.current_workers = {}
        self._is_running_exclusive_task = False

    def get_logger(self):
        return self.delegate.logger

    def get_pool_capacity(self) -> int:
        """
        How many processes could run in the same time.
        Decided by the delegate
        """
        if self._is_running_exclusive_task is True:
            return 1

        return self.delegate.read_config_of_delegate((NehushtanQueueDelegate.CONFIG_KEY_POOL_CAPACITY,), 1)

    def _scan_workers(self):
        """
        Scan registered workers, and remove dead ones from dictionary.
        Finally, return the total running processes count.
        """
        if len(self.current_workers.items()) > 0:
            delete_keys = []
            for task_id, task_process in self.current_workers.items():
                if not task_process.is_alive():
                    task_process_pid = task_process.pid
                    task_process_exit_code = task_process.exitcode
                    self.get_logger().warning(f'Worker Process for task [{task_id}] Dead', {'pid': task_process_pid})
                    self.delegate.when_worker_process_confirmed_dead(
                        task_id,
                        {'pid': task_process_pid, 'exitcode': task_process_exit_code}
                    )
                    delete_keys.append(task_id)
            for delete_key in delete_keys:
                del self.current_workers[delete_key]
                self.get_logger().debug('remove removable finished tasks', {'task_id': delete_key})

        return len(self.current_workers.items())

    def _terminate_worker_process_of_task(self, task_reference):
        p = self.current_workers.get(task_reference)
        if p:

            # 终止进程
            # https://docs.python.org/zh-cn/3/library/multiprocessing.html#multiprocessing.Process.terminate
            #
            #   在Unix上
            #       这是使用 SIGTERM 信号完成的；
            #   在Windows上
            #       使用 TerminateProcess() 。请注意，不会执行退出处理程序和finally子句等。
            #       这个函数可以用来终止或者说杀死一个进程，它不会留给进程及其所有线程清理的时间，
            #       系统会马上终止(杀死)这个进程的所有线程，致使进程终止。
            #
            # 请注意，进程的后代进程将不会被终止 —— 它们将简单地变成孤立的。
            p.terminate()

            self.get_logger().info(
                'NehushtanQueue._terminate_worker_process_of_task executed',
                {'task': task_reference, 'pid': p.pid, 'exitcode': p.exitcode, 'is_alive': p.is_alive()}
            )
            self.delegate.when_killed_worker_process(task_reference, worker_pid=p.pid)
            self.register_news(
                'when_killed_worker_process',
                f'Sent signal TERMINATE(15) to worker for task {task_reference}, target pid {p.pid}'
            )
        else:
            self.get_logger().warning(
                'NehushtanQueue._terminate_worker_process_of_task target task not found amongst current workers',
                {'task': task_reference}
            )
            self.delegate.when_killed_worker_process(task_reference, not_found=True)

    def _loop_maintain(self, wait_till_processes_become_less_than: int = 0):
        """
        Since 0.4.27 Use `while True` to avoid stack overflow
        @see https://qiita.com/komorin0521/items/9f2ea1e2a37fd7f13fe2
        For Issue: `Fatal Python error: Cannot recover from stack overflow. Python runtime state: initialized`
        """
        while True:
            self._scan_workers()

            if self.delegate.handle_command_queue() > 0:
                # Since 0.2.18 the news only be sent when any command(s) done
                self.register_news('handle_command_queue', 'Handled Command Queue')

            kill_list = self.delegate.should_kill_any_worker_processes()
            if len(kill_list) > 0:
                for kill_task_id in kill_list:
                    self._terminate_worker_process_of_task(kill_task_id)

            total_alive_current_workers = self._scan_workers()

            # need to do some wait
            if total_alive_current_workers >= wait_till_processes_become_less_than > 0:
                time.sleep(2)
            else:
                return total_alive_current_workers

    def register_news(self, title: str, content: str):
        """
        Since 0.2.9
        """
        worker_count = len(self.current_workers.items())
        busy_rate = 1.0 * worker_count / self.get_pool_capacity()
        self.delegate.register_queue_news(title, content, worker_count, busy_rate)

    def loop(self):
        self.delegate.when_loop_starts()
        self.register_news('when_loop_starts', 'Loop Started')

        while True:
            try:
                # 1. check current workers status
                total_current_workers = len(self.current_workers.items())
                self.get_logger().info('Current workers totally count', {'total': total_current_workers})

                # 2. handle command queue and kill list
                self._loop_maintain()

                # 3. check elihu command
                self.delegate.read_latest_command()
                if self.delegate.should_terminate():
                    if self.delegate.should_wait_for_all_workers_before_terminating():
                        self.register_news('terminating',
                                           'Waiting for all running tasks finishing, then terminate loop')
                        self._loop_maintain(1)
                    break

                # 4. check queue if new task there
                if not self.delegate.is_runnable():
                    self.register_news('should_not_run', 'Loop is ordered to sleep for a while')
                    self.delegate.when_loop_should_not_run()
                    continue

                total_current_workers = len(self.current_workers.items())
                if total_current_workers >= self.get_pool_capacity():
                    self.register_news('all_workers_busy', 'All workers are busy, wait till anyone become available')
                    self._loop_maintain(self.get_pool_capacity())

                    if self._is_running_exclusive_task and len(self.current_workers.items()) <= 0:
                        self._is_running_exclusive_task = False
                        self.register_news('exit_exclusive_mode', 'Exit exclusive mode as no task running now')

                try:
                    self.delegate.before_seeking_next_tasks()
                    task_candidates = self.delegate.check_next_task_candidates()

                    newly_locked = {}
                    for task_candidate in task_candidates:

                        # Since 0.3.1
                        # check locks and maintain a newly locked dict to avoid trying start up for known new locks
                        this_lock_list = task_candidate.get_lock_list()

                        already_locked = False
                        for x in this_lock_list:
                            if newly_locked.get(x, False) is True:
                                already_locked = True
                                break
                        if already_locked:
                            self.get_logger().debug(
                                f'Task Candidate {task_candidate.get_task_reference()} '
                                f'locked by newly running tasks, passover'
                            )
                            continue
                        else:
                            for x in this_lock_list:
                                newly_locked[x] = True

                            self.__run_one_task(task_candidate)
                            # here is a problem:
                            # when __run_one_task return False, the task_candidate actually did not start up,
                            # the locks are really not locked newly

                            if self._is_running_exclusive_task:
                                break
                            if self.get_pool_capacity() <= len(self.current_workers.items()):
                                break

                except NoNextTaskSituation:
                    self.register_news('when_no_task_to_do', 'There is no task in queue able to deal now')
                    self.delegate.when_no_task_to_do()
                    continue

            except Exception as loop_round_error:
                self.register_news('when_loop_reports_error', f'Loop meets error: {loop_round_error}')
                self.delegate.when_loop_reports_error(loop_round_error.__str__(), loop_round_error)

        self.register_news('loop_terminating', 'Loop is about to terminate')
        self.delegate.when_loop_terminates()
        self.register_news('when_loop_terminated', 'Loop terminated')

    def __run_one_task(self, task: NehushtanQueueTask) -> bool:
        """
        Since 0.3.0
        When a found task:
            successfully genereate a process to execute, return True.
            not executable, return False.
        """
        task_id = task.get_task_reference()

        if task.is_exclusive():
            # now daemon should wait for the other tasks to be over
            self.register_news('before_enter_exclusive_mode',
                               f'Task {task_id} is exclusive, waiting for all running workers finish')
            self._loop_maintain(1)
            self.register_news('enter_exclusive_mode',
                               f'Enter exclusive mode for task {task_id} as all other workers finished')
            self._is_running_exclusive_task = True

        if not task.before_execute():
            self.register_news('when_task_not_executable', f'Task {task_id} is not executable')
            self.delegate.when_task_not_executable(task)

            if self._is_running_exclusive_task:
                self._is_running_exclusive_task = False
                self.register_news('exit_exclusive_mode',
                                   f'Exit exclusive mode as task {task_id} is not executable')

            return False

        p = Process(target=NehushtanQueue.embedded_task_execute, args=(task, self.task_delegate))
        p.start()
        self.current_workers[task.get_task_reference()] = p

        self.register_news(
            'when_worker_process_created',
            f'Task [{task.get_task_reference()}] -> Process {p.name} PID is [{p.pid}]'
        )
        self.delegate.when_worker_process_created(
            task.get_task_reference(),
            f'Task [{task.get_task_reference()}] -> Process {p.name} PID is [{p.pid}]'
        )

        return True

    @staticmethod
    def embedded_task_execute(embedded_task: NehushtanQueueTask, task_delegate: NehushtanQueueTaskDelegate):
        """
        This works in WORKER
        Since 0.4.11 use NehushtanQueueTaskDelegate
        """
        try:
            """
            Since 0.4.5 Add try block to catch outer_exception
            """
            task_delegate.when_to_execute_task(embedded_task, os.getpid())
            try:
                embedded_task.execute()
            except Exception as e:
                task_delegate.when_task_raised_exception(embedded_task, e)
            task_delegate.when_task_executed(embedded_task, os.getpid())

        except Exception as outer_exception:
            task_delegate.logger.exception(
                'In embedded_task_execute exception occurs outside the embedded_task '
                f'[{embedded_task.get_task_reference()}] on Process {os.getpid()}',
                outer_exception
            )
