from cosu import utils
from csip import Client
from typing import List, Dict, Tuple
import queue, os


def csip_worker(reqq: queue.Queue, thread_no: int, stop, full_trace,
                url, files, arg_params, conf: Dict, metainfo: Dict) -> None:
    async_call = conf.get('async_call', True)  # default is async
    save_resp = conf.get('save_response_to', None)  # save response, set it to a folder if responses should be saved.

    while not stop():
        try:
            (rnd, step, iteration, particle, x, step_param_names, calib_params, objfunc, resq) = reqq.get(True, 0.5)
            # print(thread_no, particle)

            c = Client(metainfo=metainfo)

            # static params (from args)
            for param in arg_params:
                c.add_data(param['name'], param['value'])

            # particle params  (generated from steps)
            # for i, value in enumerate(x):
            for idx, value in enumerate(x[particle, :]):
                c.add_data(step_param_names[idx], value)

            # other, previously calibrated params (other steps)
            for name, value in calib_params.items():
                c.add_data(name, value)

            # objective function info
            for of in objfunc:
                c.add_cosu(of['name'], of['of'], of['data'])
                # c.add_data(of['name'], (of['data'][0], of['data'][1]))

            print('.', end='', flush=True)

            try:
                # print(c)
                if async_call:
                    res = c.execute_async(url, files=files, conf=conf)
                else:
                    res = c.execute(url, files=files, conf=conf)

                if res.is_failed():
                    print(res)

                if save_resp:
                    res.save_to(os.path.join(save_resp, 'r{}s{}i{}p{}.json'.format(rnd, step, iteration, particle)))

                # print(res)
                print(u'\u2714', end='', flush=True)
                cost = utils.calc_cost(res, objfunc)

                if full_trace is not None:
                    all_params = {}
                    # for i, value in enumerate(x):
                    for idx, value in enumerate(x[particle, :]):
                        all_params[step_param_names[idx]] = value
                    for name, value in calib_params.items():
                        all_params[name] = value
                    full_trace.append((all_params, cost))

                resq.put((particle, cost))
            except:
                print(res)
            reqq.task_done()
        except queue.Empty:
            continue
