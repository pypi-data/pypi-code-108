import torch
import numpy as np
import numpy
import logging

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.INFO)


class Pseudo_agent:
    """
    Pseudo agent for evaluation - assumes the agent is based on q-values.
    Can either work with discrete state variables or with the environemnt.
    """

    def __init__(self, network, name=None):
        self.network = network
        if name is None:
            self.name = "Pseudo Agent"
        else:
            self.name = name

    def get_name(self):
        """
        get the chosen name

        Returns:
            string: name
        """
        return self.name

    def act_with_env(self, env):
        """same as act, but with env option only

        Args:
            env ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.act(env=env)

    def act(self, state=None, env=None, applicable_actions=None):
        """
        method to decide for an action.
        Either specify state (and possible the available actions) or environment.

        Args:
            state (array, optional): values representing the state. Defaults to =None.
            env (Environment, optional): environment to extract the state from. Defaults to =None.
            blocked_actions (array, optional): ids if the actions that aren't applicable in the current state. Defaults to = None. (which assumes all actions are applicable)

        Returns:
            int: id of action to be applied
        """
        x = self.q_vals(state, env, applicable_actions)

        return np.argmax(x)

    def q_vals(self, state=None, env=None, applicable_actions=None):
        """return the approximation of the q-values

        Args:
            state (array, optional): values representing the state. Defaults to =None.
            env (Environment, optional): environment to extract the state from. Defaults to =None.
            blocked_actions (array, optional): ids if the actions that aren't applicable in the current state. Defaults to = None. (which assumes all actions are applicable)

        Returns:
            array: q-values
        """
        assert not (
            env is None and state is None
        ), "You must specify at least one way for the agent to interact with the environment"
        assert not (
            env is not None and state is not None
        ), "You must either specifiy a state or an environment"
        assert not (
            env is not None and applicable_actions is not None
        ), "You must either specify the environment or discrete representations, don't mix both ways."

        if state is None:
            # if you want to use another method to call the state, change the next line
            state = env.get_state()
            applicable_actions = env.applicable_actions()

        # check and cast state type
        if type(state) == np.ndarray:
            state = torch.from_numpy(state)
        else:
            if type(state) == torch.Tensor:
                pass
            else:
                state = torch.tensor(state)

        with torch.no_grad():
            x = self.network.forward(state)
            x = x.numpy()

            if applicable_actions is not None:
                for i in range(len(x)):
                    if i not in applicable_actions:
                        x[i] = -float("inf")

            return x

    def report(self, one=None, two=None, three=None, four=None, five=None):
        pass

    def finish(self):
        pass
