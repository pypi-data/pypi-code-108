import threading, traceback, time, sys
from datetime import datetime, timedelta


def dump_stack(thread_id,output_path, timeout):
    with open(output_path,'a+') as f:
        started = datetime.now()
        while datetime.now()  - started < timedelta(seconds=timeout):
            frame = sys._current_frames().get(thread_id)
            if not frame:
                return
            f.write(str(datetime.now()))
            f.write('\n')
            for stack in traceback.extract_stack(frame):
                line = stack[0]
                line_num = stack[1]
                method_name = stack[2]

                stack = '{} ({}:{})\n'.format(method_name, line, line_num)
                f.write(stack)
                f.write('\n')
            time.sleep(0.5)

def dumpThreadStack(timeout, output_path):
    thread_id = threading.get_ident()

    thr = threading.Thread(target=dump_stack, args=(thread_id,output_path, timeout), kwargs={})
    thr.setDaemon(True)
    thr.start()


def printStack():
    thread_id = threading.get_ident()

    frame = sys._current_frames().get(thread_id)
    if not frame:
        return
    import io
    f = io.StringIO()
    f.write(str(datetime.now()))
    f.write('\n')
    for stack in traceback.extract_stack(frame):
        line = stack[0]
        line_num = stack[1]
        method_name = stack[2]

        stack = '{} ({}:{})\n'.format(method_name, line, line_num)
        f.write(stack)
        f.write('\n')
    print(f.getvalue())


def printAllStack():
    for t in threading.enumerate():
        thread_id = t.ident

        frame = sys._current_frames().get(thread_id)
        if not frame:
            return
            
        import io
        f = io.StringIO()
        f.write(str(datetime.now()))
        f.write('\n')
        for stack in traceback.extract_stack(frame):
            line = stack[0]
            line_num = stack[1]
            method_name = stack[2]

            stack = '{} ({}:{})\n'.format(method_name, line, line_num)
            f.write(stack)
            f.write('\n')
        print(f.getvalue())
