from django.conf import settings


def make_shedurer_tasks(func=None, when='1s', start=None, args=None, kwargs=None, name=None, repeating=False, threaded=True):
    from isc_common.management.commands.grop_tmp_mat_views import grop_mat_views
    from pyriodic import Scheduler, DurationJob

    s = Scheduler()

    def drop_tbl():
        grop_mat_views(prefix='ready')
        grop_mat_views(prefix='tmp')

    if callable(func):
        s.add_job(DurationJob(func=func, when=when, name=name, start=start, args=args, kwargs=kwargs, repeating=repeating, threaded=threaded))
    else:
        s.add_job(DurationJob(drop_tbl, when=settings.SHEDULLER_PERIOD, name='grop_ready_mat_views'))

    # print(s.next_run_times())
    return s


def st_sheduler():
    try:
        if callable(settings.SHEDULLER):
            from threading import Timer
            def st():
                if callable(settings.SHEDULLER):
                    s = make_shedurer_tasks()
                    settings.SHEDULLER(s)

            t = Timer(10.0, st)
            t.start()
    except AttributeError:
        print('Sheduler not started.')
        pass


st_sheduler()
