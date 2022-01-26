import logging

import numpy as np
import time
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    wins: int
    losses: int
    episode_timedout: int
    mean_return: float
    mean_steps: float
    evaluation_timedout: bool


def _episode(env, agent, max_steps, gamma=0.99, timeout=float("inf")):
    """
    Run a single episode for at most max_steps

    Args:
        env: environment in which episode takes place
        agent: the acting agent
        max_steps (int): episode is cut off after this maximum number of steps have been carried out
        gamma (float): discounting factor when calculating return

    Returns:

    """
    done = False
    ret = 0

    t_start = time.time()
    for t in range(max_steps):
        action = agent.act_with_env(env.clone())
        r, _, done = env.step(action)
        ret += r * np.power(gamma, t)
        elapsed = time.time() - t_start
        if done or elapsed > timeout:
            break

    return ret, t, int(ret > 0), int(ret < 0), int(not done), elapsed


class Evaluator:
    def __init__(self, env):
        """Init the Evaluator class

        Args:
            env (env): environment to evaluate upon.
        """
        self.agents = []
        self.names = []
        self._results = []
        self._timedout = []
        self._evaluated = []
        self.env = env

    def __len__(self):
        return len(self.agents)

    def add_agent(self, agent):
        """add an agent for evaluation. Agents must implement the `act_with_env` and `get_name` method.

        Args:
            agent (Agent): agent to add.
        """
        self.agents.append(agent)
        self.names.append(agent.get_name())
        self._timedout.append(False)
        self._evaluated.append(False)

    def reset(self):
        """reset the evaluator for new evaluations."""
        self._results = [([], [0, 0, 0], []) for _ in range(len(self))]
        self._timedout = [False for _ in range(len(self))]
        self._evaluated = [False for _ in range(len(self))]

    def evaluate(self, number, max_steps=100, GAMMA=0.99, verbose=False):
        """evaluate using number many episodes with at most max_steps many steps.
        Return will be discounted using gamma.

        Args:
            number (int): number of episodes to use for eval
            max_steps (int, optional): maximal number of steps per episode. Defaults to 100.
            GAMMA (float, optional): Discount factor for calculating the return. Defaults to 0.99.
            verbose (bool, optional): Control output

        Returns:
            array [float, (int, int, int), float]: array containing 1. the return received in average, 2. the win-lose-timeout numbers, 3. the average number of taken steps in the winning case.
        """
        self.reset()
        env = self.env
        divider = int(0.1 * number)

        for i in range(number):
            env.reset()

            for a, agent in enumerate(self.agents):

                current_env = env.clone()

                done = False
                ret = 0

                for t in range(max_steps):
                    action = agent.act_with_env(current_env.clone())

                    r, _, done = current_env.step(action)
                    ret += r * np.power(GAMMA, t)
                    if done:
                        break
                # entry 0 is the place for the returns
                self._results[a][0].append(ret)

                if r > 0:
                    # win counter
                    self._results[a][1][0] += 1
                    # include step counter only when winning
                    # entry 2 for t
                    self._results[a][2].append(t)
                else:
                    if r < 0:
                        # loose counter
                        self._results[a][1][1] += 1
                    else:
                        # time_out counter
                        self._results[a][1][2] += 1

            if verbose and i % divider == 0:
                print(i, "/", number)

        self._evaluated = [True for _ in range(len(self))]
        self.print()
        return self._results

    def results_as_dict(self):
        return {
            name: result
            for name, result, eval_done in zip(
                self.names, self._results, self._evaluated
            )
            if eval_done
        }

    def results(self):
        return {
            name: EvaluationResult(
                wins=res[1][0],
                losses=res[1][1],
                episode_timedout=res[1][2],
                mean_return=np.mean(res[0]),
                mean_steps=np.mean(res[2]),
                evaluation_timedout=timedout,
            )
            for name, res, timedout, eval_done in zip(
                self.names, self._results, self._timedout, self._evaluated
            )
            if eval_done
        }

    def print(self):
        """display the results. Works only, if some eval was done."""
        print(self.format_all())

    @staticmethod
    def format(name, wins, losses, timeouts, mean_return, mean_steps):
        return (
            "Agent %s won %i, lost %i and timed out %i games, by receiving an average return of %.2f.\nIn the winning case, %.2f steps were taken on average"
            % (name, wins, losses, timeouts, mean_return, mean_steps)
        )

    def format_all(self):
        if self._results == []:
            return "No agents were evaluated"
        else:
            lines = []
            for _, name, res, eval_done in zip(
                self.agents, self.names, self._results, self._evaluated
            ):
                if eval_done:
                    lines.append(
                        Evaluator.format(
                            name,
                            res[1][0],
                            res[1][1],
                            res[1][2],
                            np.mean(res[0]),
                            np.mean(res[2]),
                        )
                    )
                else:
                    lines.append("Agent %s was not evaluated" % name)
            return "\n\n".join(lines)


class TimedEvaluator(Evaluator):
    """
    Evaluator with per-agent timeout
    """

    def __init__(self, env):
        super(TimedEvaluator, self).__init__(env)

    def add_agent(self, agent):
        super(TimedEvaluator, self).add_agent(agent)

    @staticmethod
    def _evaluate_agent(env, agent, number, max_steps, gamma, timeout):
        t_total = 0.0
        result = [[], [0, 0, 0], []]
        timed_out = False
        for _ in range(number):
            if t_total >= timeout:
                logging.warning(
                    "Agent %s timed out after %.4f seconds."
                    % (agent.get_name(), t_total)
                )
                timed_out = True
                break

            env.reset()
            ret, steps, win, loose, ep_timeout, elapsed = _episode(
                env, agent, max_steps, gamma, timeout - t_total
            )
            t_total += elapsed

            result[0].append(ret)
            result[1][0] += win
            result[1][1] += loose
            result[1][2] += ep_timeout
            if win == 1:
                result[2].append(steps)

        if not timed_out:
            logging.info(
                "Finished evaluation of '%s' within %.4f seconds."
                % (agent.get_name(), t_total)
            )

        return result, timed_out

    def evaluate(
        self, number, max_steps=100, GAMMA=0.99, verbose=False, timeout=float("inf")
    ):
        """evaluate using number many episodes with at most max_steps many steps.
        Return will be discounted using gamma.

        Args:
            number (int): number of episodes to use for eval
            max_steps (int, optional): maximal number of steps per episode. Defaults to 100.
            GAMMA (float, optional): Discount factor for calculating the return. Defaults to 0.99.
            verbose (bool, optional): Control output
            timeout (float, optional): Per-agent timeout in minutes. If this limit is exceeded, the

        Returns:
            array [float, (int, int, int), float]: array containing 1. the return received in average, 2. the win-lose-timeout numbers, 3. the average number of taken steps in the winning case.
        """
        self.reset()

        timeout = timeout * 60

        for (
            a,
            agent,
        ) in enumerate(self.agents):
            try:
                result, timed_out = TimedEvaluator._evaluate_agent(
                    self.env.clone(), agent, number, max_steps, GAMMA, timeout
                )
                self._results[a] = result
                self._timedout[a] = timed_out
                self._evaluated[a] = True
            except:
                logging.exception(
                    "An exception occurred while evaluating agent '%s'"
                    % agent.get_name()
                )

        return self._results
