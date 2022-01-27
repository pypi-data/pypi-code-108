#
# $Id:$
#
# This file is part of the Cloud Services Integration Platform (CSIP),
# a Model-as-a-Service framework, API, and application suite.
#
# 2012-2020, OMSLab, Colorado State University.
#
# OMSLab licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
#

from ..utils import utils
from .csip_access import csip_worker
from pyswarms.single.global_best import GlobalBestPSO
from os import path
from threading import Thread
from typing import Dict, List, Set, Tuple
import numpy as np
import copy
import datetime
import queue
import json
import os


def eval_cost(x, iteration, step_param_names, step_objfunc, calib_params, req_queue, files, url, param, conf: Dict, rnd,
              step):
    particles = len(x[:, 0])

    pfail_count = conf.get('particles_fail', 1)  # Number of particles allowed to fail.
    pfail_retry = conf.get('particles_retry', 3)  # retry number of times if more than allowed fail

    while pfail_retry > 0:
        cost = np.ones(particles)
        res_queue = queue.Queue()

        print('   ', end='', flush=True)

        # submit for processing
        # for i_particle, v in enumerate(x[:, 0]):
        for particle in range(particles):
            req_queue.put((rnd, step, iteration, particle, x, step_param_names, calib_params, step_objfunc, res_queue))
            # req_queue.put((i_particle, x[i_particle,:], step_param_names, calib_params, step_objfunc, res_queue))

        # wait for the cost value to come back
        # for i, v in enumerate(x[:, 0]):
        for idx in range(particles):
            (particle, p_cost) = res_queue.get()
            cost[particle] = p_cost
            res_queue.task_done()

        res_queue.join()

        # replace the 'nan' cost values (failed/missing runs) with the mean of the
        # rest of the cost values, hence ignore it

        # print("cost ", cost)
        nan_idx = np.where(np.isnan(cost))
        failed_particles = len(nan_idx[0])

        # leave the loop if fails acceptable
        if failed_particles <= pfail_count:
            break
        print("Re-running particles, since ", failed_particles, ' out of ', particles, ' particles failed.')
        pfail_retry -= 1

    if pfail_retry == 0:
        print('Particle evaluation failed ', conf.get('particles_retry', 3), ' times. PSO stopped.')
        return None

    # print("mean ", mean)
    # assign the mean value to all failed runs.
    mean = np.nanmean(cost)
    cost[nan_idx[0]] = mean

    print(flush=True)
    return cost


def global_best(steps: Dict, rounds: Tuple, args: Dict, n_particles: int, iters: int, options: Dict,
                oh_strategy: Dict = None, n_threads: int = 4, rtol: float = 0.001, ftol: float = -np.inf,
                ftol_iter: int = 1, full_trace: List = None, rtol_iter: int = 1,
                conf: Dict = None, metainfo: Dict = None, cost_target: float = -np.inf) -> Tuple:
    """Performs a stepwise particle swarm optimization PSO using a global best approach.

        Parameters
        ----------
        steps : Dict
            step definitions
        rounds : tuple
            round definition,  (min,max) or max
        args : Dict
            static service args
        n_particles : int
            number of particles
        iters : int
            number of iterations
        options : Dict
            PSO options (see pyswarms)
        oh_strategy : Dict
            PSO Option handling strategy (see pyswarms)
        n_threads : int
            size of thread pool (default: 4)
        rtol : float
            percentage of change of sum(best_cost) between rounds for
            convergence. (Default is 0.001 0.1%)
        ftol : float
            PSO tolerance (default: -np.inf)
        ftol_iter : float
            number of iterations over which the relative error in
            objective_func is acceptable for convergence. (default: 1)
        full_trace : List
            trace of all runs, list of tuples
            first is dictionary of parameter names to parameter values
            second is the cost value (default: None)
        rtol_iter : int
            the number of subsequent rounds with sum(best_cost) < rtol
            (default: 1)
        conf : Dict
            configuration settings (default: {} )
        metainfo : Dict
             additional metainfo for the csip client (default: {} )
        cost_target: float
             the cost target (default: -np.inf)
        Returns
        -------
        Tuple
            optimizer: List, step_trace: Dict

    """

    utils.check_url(args['url'])

    step_file = conf.get('step_trace', None)

    min_rounds = 1
    if type(rounds) == tuple:
        min_rounds = rounds[0]
        max_rounds = rounds[1]
    else:
        max_rounds = rounds

    if min_rounds < 1:
        raise Exception('min rounds >= 1 expected, was "{}"'.format(min_rounds))

    if max_rounds > 20:
        raise Exception('max rounds <= 20 expected, was "{}"'.format(max_rounds))

    if n_threads < 1:
        raise Exception('n_threads >= 1, was "{}"'.format(n_threads))

    if rtol_iter < 1:
        raise Exception('rtol_iter >= 1, was "{}"'.format(rtol_iter))

    if full_trace is not None and not isinstance(full_trace, list):
        raise Exception('full_trace must be of type, was "{}"'.format(type(full_trace)))

    best_cost = np.ones(len(steps)) * np.inf
    optimizer = np.empty(len(steps), dtype=object)

    # trace of steps info
    step_trace = {}

    step_trace['dir'] = os.getcwd()
    step_trace['start'] = str(datetime.datetime.now())
    step_trace['min_rounds'] = min_rounds
    step_trace['max_rounds'] = max_rounds
    step_trace['iters'] = iters
    step_trace['ftol'] = ftol
    step_trace['ftol_iter'] = ftol_iter
    step_trace['rtol'] = rtol
    step_trace['rtol_iter'] = rtol_iter
    step_trace['n_threads'] = n_threads
    step_trace['n_particles'] = n_particles
    step_trace['n_steps'] = len(steps)
    step_trace['steps'] = copy.deepcopy(steps)
    step_trace['args'] = args

    if step_file is not None:
        with open(step_file, "w") as fo:
            json.dump(step_trace, fo)

    # best round cost
    best_round_cost = np.inf

    # request queue for worker
    req_queue = queue.Queue()

    conf = conf or {}
    done = False
    thread_pool = []
    for thread_no in range(n_threads):
        worker = Thread(target=csip_worker, args=(req_queue, thread_no, lambda: done,
                                                  full_trace, args['url'], args.get('files', None), args['param'],
                                                  conf, metainfo)
                        )
        thread_pool.append(worker)
        worker.start()

    r_below = 0
    early_exit = False
    start_time = datetime.datetime.now()
    for r in range(max_rounds):
        no_improvement = np.full(len(steps), True)
        for s, step in enumerate(steps):

            # check if forced exit.
            if path.exists("stop"):
                print('\n>>>>> stop file found, exit now.')
                early_exit = True
                break

            param_names, bounds, objfunc = utils.get_step_info(steps, s)
            # maybe clone args?
            args['step_param_names'] = param_names
            args['step_objfunc'] = objfunc
            # get calibrated parameter from all other steps
            args['calib_params'] = utils.get_calibrated_params(steps, s)

            args['req_queue'] = req_queue
            args['conf'] = conf

            # create optimizer in the first round.
            if optimizer[s] is None:
                optimizer[s] = GlobalBestPSO(step.get('n_particles', n_particles),
                                             len(param_names),
                                             oh_strategy=step.get('oh_strategy', oh_strategy),
                                             options=step.get('options', options),
                                             bounds=bounds,
                                             ftol=step.get('ftol', ftol),
                                             ftol_iter=step.get('ftol_iter', ftol_iter),
                                             cost_target=step.get('cost_target', cost_target))
            print('\n>>>>> R{}/S{}  particle params: {}  calibrated params: {}\n'.format(r + 1, s + 1, param_names,
                                                                                         args['calib_params']))

            args['rnd'] = r + 1
            args['step'] = s + 1

            # perform optimization
            cost, pos = optimizer[s].optimize(eval_cost, iters=step.get('iters', iters), **args)
            if cost is None:
                early_exit = True
                break

            # capture the best cost
            # if cost < best_cost[s] and np.abs(cost - best_cost[s]) > rtol:
            if cost < best_cost[s]:
                best_cost[s] = cost
                no_improvement[s] = False
                utils.annotate_step(best_cost[s], pos, steps, s)

            print('\n     Step summary, best particle values: {} '.format(pos))

            key = "r{}s{}".format(r + 1, s + 1)
            step_trace[key] = {}
            step_trace[key]['time'] = str(datetime.datetime.now())
            step_trace[key]['best_costs'] = best_cost
            step_trace[key]['steps'] = copy.deepcopy(steps)

            if step_file is not None:
                with open(step_file, "w") as fo:
                    json.dump(step_trace, fo)

            # print(json.dumps(steps, sort_keys=False, indent=2))

        if early_exit:
            step_trace['exit'] = '1'
            break

        round_cost = np.sum(best_cost)

        # if no improvement in all steps, break out of rounds prematurely
        # but start checking only after min_rounds
        # if (r + 1 >= min_rounds) and all(no_improvement):
        rel_round_tol = 1 - round_cost / best_round_cost

        print('\n  Round summary - round_cost:{}, step_costs: {}, step improvement:{}'
              .format(round_cost, best_cost, np.invert(no_improvement)))
        print('\n  Progress -  best_round_cost:{}, rel_round_tol:{}, rtol:{}'
              .format(best_round_cost, rel_round_tol, rtol))

        key = "r{}".format(r + 1)
        step_trace[key] = {}
        step_trace[key]['time'] = str(datetime.datetime.now())
        step_trace[key]['round_cost'] = round_cost
        step_trace[key]['best_costs'] = best_cost
        step_trace[key]['improvements'] = no_improvement
        if step_file is not None:
            with open(step_file, "w") as fo:
                json.dump(step_trace, fo)

        if (r + 1 >= min_rounds) and 0 <= rel_round_tol < rtol:
            r_below += 1
            if r_below >= rtol_iter:
                break
        else:
            # reset
            r_below = 0

        if round_cost < best_round_cost:
            best_round_cost = round_cost

    end_time = datetime.datetime.now()
    elapsed = str(end_time - start_time)

    print('Done in {} after {} out of {} rounds'.format(elapsed, r + 1, max_rounds))

    done = True
    for worker in thread_pool:
        worker.join()

    step_trace['rounds'] = r + 1
    step_trace['end'] = str(datetime.datetime.now())
    step_trace['time'] = elapsed

    if step_file is not None:
        with open(step_file, "w") as fo:
            json.dump(step_trace, fo)

    return optimizer, step_trace

# def p_global_best(steps: Dict, rounds: Tuple, args: Dict, n_particles: int, iters: int, options: Dict,
#                   n_threads: int = 4, rtol: float = 0.001, ftol: float = -np.inf,
#                   full_trace: List = None, rounds_below: int = 1) -> Tuple:
#     """Performs a parallel stepwise particle swarm optimization PSO using a global best approach.
#
#         Parameters
#         ----------
#         steps : Dict
#             step definitions
#         rounds : tuple
#             round definition,  (min,max) or max
#         args : Dict
#             static service args
#         n_particles : int
#             number of particles
#         iters : int
#             number of iterations
#         options : Dict
#             PSO options (see pyswarms)
#         n_threads : int
#             size of thread pool (default: 4)
#         rtol : float
#             percentage of change of sum(best_cost) between rounds for
#             convergence. (Default is 0.001 0.1%)
#         ftol : float
#             PSO tolerance (default: -np.inf)
#         full_trace : List
#             trace of all runs, list of tuples
#             first is dictionary of parameter names to parameter values
#             second is the cost value (default: None)
#         rounds_below : int
#             the number of subsequent rounds with sum(best_cost) < rtol
#             (default: 1)
#         Returns
#         -------
#         Tuple
#             optimizer: List, step_trace: Dict
#     """
#
#     utils.check_url(args['url'])
#
#     min_rounds = 1
#     if type(rounds) == tuple:
#         min_rounds = rounds[0]
#         max_rounds = rounds[1]
#     else:
#         max_rounds = rounds
#
#     if min_rounds < 1:
#         raise Exception('min rounds >= 1 expected, was "{}"'.format(min_rounds))
#
#     if max_rounds > 20:
#         raise Exception('max rounds <= 20 expected, was "{}"'.format(max_rounds))
#
#     if n_threads < 1:
#         raise Exception('n_threads >= 1, was "{}"'.format(n_threads))
#
#     if rounds_below < 1:
#         raise Exception('rounds_below >= 1, was "{}"'.format(rounds_below))
#
#     if full_trace is not None and not isinstance(full_trace, list):
#         raise Exception('full_trace must be of type, was "{}"'.format(type(full_trace)))
#
#     best_cost = np.ones(len(steps))
#     cost = np.ones(len(steps))
#     optimizer = np.empty(len(steps), dtype=object)
#     pos = np.empty(len(steps), dtype=object)
#     args_s = np.empty(len(steps), dtype=object)
#
#     # trace of steps info
#     step_trace = {}
#
#     # best round cost
#     best_round_cost = 1000
#
#     # request queue for worker
#     req_queue = queue.Queue()
#
#     # Threadpool management
#     done = False
#     thread_pool = []
#     for thread_no in range(n_threads):
#         worker = Thread(target=csip_worker, args=(req_queue, thread_no, lambda: done,
#                                                   full_trace, args['url'], args['files'], args['param']))
#         thread_pool.append(worker)
#         worker.start()
#
#     start_time = datetime.datetime.now()
#
#     # setup Step PSOs
#     for s, step in enumerate(steps):
#         param_names, bounds, objfunc = utils.get_step_info(steps, s)
#         optimizer[s] = GlobalBestPSO(n_particles,
#                                      len(param_names),
#                                      options=options,
#                                      bounds=bounds,
#                                      ftol=ftol)
#
#     def step_thread(s, args):
#         cost[s], pos[s] = optimizer[s].optimize(eval_cost, iters=iters, **args)
#
#     # Run PSOs in parallel
#     r_below = 0
#     for r in range(max_rounds):
#         no_improvement = np.full(len(steps), True)
#         # check if forced exit.
#         if path.exists("stop"):
#             print('\n>>>>> stop file found, exit now.')
#             break
#
#         # cross copy calibrated parameter, setup the arguments
#         for s, step in enumerate(steps):
#             param_names, bounds, objfunc = utils.get_step_info(steps, s)
#             # maybe clone args?
#             args_s[s] = args
#             args_s[s]['step_param_names'] = param_names
#             args_s[s]['step_objfunc'] = objfunc
#             # get calibrated parameter from all other steps
#             args_s[s]['calib_params'] = utils.get_calibrated_params(steps, s)
#
#             args_s[s]['req_queue'] = req_queue
#
#             # create optimizer in the first round.
#             print('\n>>>>> R{}/S{}  particle params: {} calibrated params: {}\n'.format(r + 1, s + 1, param_names,
#                                                                                         args_s[s]['calib_params']))
#
#         # perform optimization
#         s_threads = []
#         for s, step in enumerate(steps):
#             s_thread = threading.Thread(target=step_thread, args=(s, args_s[s]))
#             s_threads.append(s_thread)
#             s_thread.start()
#
#         for t in s_threads:
#             t.join()
#
#         # eval cost
#         for s, step in enumerate(steps):
#             # capture the best cost
#             # if cost < best_cost[s] and np.abs(cost - best_cost[s]) > rtol:
#             if cost[s] < best_cost[s]:
#                 best_cost[s] = cost[s]
#                 no_improvement[s] = False
#                 utils.annotate_step(best_cost[s], pos[s], steps, s)
#
#             print('\n     Step {} summary, best particle values: {} '.format(s, pos[s]))
#
#             key = "r{}s{}".format(r + 1, s + 1)
#             step_trace[key] = copy.deepcopy(steps)
#
#             # print(json.dumps(steps, sort_keys=False, indent=2))
#
#         round_cost = np.sum(best_cost)
#
#         # if no improvement in all steps, break out of rounds prematurely
#         # but start checking only after min_rounds
#         # if (r + 1 >= min_rounds) and all(no_improvement):
#         rel_round_tol = 1 - round_cost / best_round_cost
#
#         print('\n  Round summary - round_cost:{}, step_costs: {}, step improvement:{}'
#               .format(round_cost, best_cost, np.invert(no_improvement)))
#         print('\n  Progress -  best_round_cost:{}, rel_round_tol:{}, rtol:{}'
#               .format(best_round_cost, rel_round_tol, rtol))
#
#         if (r + 1 >= min_rounds) and 0 <= rel_round_tol < rtol:
#             r_below += 1
#             if r_below == rounds_below:
#                 break
#         else:
#             # reset
#             r_below = 0
#
#         if round_cost < best_round_cost:
#             best_round_cost = round_cost
#
#     end_time = datetime.datetime.now()
#     elapsed = str(end_time - start_time)
#
#     print('Done in {} after {} out of {} rounds'.format(elapsed, r + 1, max_rounds))
#
#     done = True
#     for worker in thread_pool:
#         worker.join()
#
#     step_trace['rounds'] = r + 1
#     step_trace['steps'] = len(steps)
#     step_trace['iters'] = iters
#     step_trace['particles'] = n_particles
#     step_trace['time'] = elapsed
#
#     return optimizer, step_trace
