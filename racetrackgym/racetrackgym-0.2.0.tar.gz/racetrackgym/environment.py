from . import parser
import copy
import numpy as np
from . import graphic as g
import logging
import os
from pathlib import Path

from argparse import Namespace


logging.basicConfig(
    format="[%(levelname)s: %(filename)s - line %(lineno)d] %(message)s",
    level=logging.INFO,
)


def _round(x):
    return int(np.floor(x + 0.5))


def _discretize_position(pos):
    """used for cont. rt. rounds the continuous position to the neareast discrete one. (Each coordinate is round for itself.)

    Args:
        pos ((float, float)): current cont. position.

    Returns:
        ((int,int)): discrete position
    """
    discrete_x = _round(pos[0])
    discrete_y = _round(pos[1])

    return (discrete_x, discrete_y)


class Map:
    """Class representing a racetrack map."""

    def random_line(self, width):
        """method to randomly create a line of the given width within the empty tiles.

        Args:
            width ([int]): width of the line to create

        Returns:
            array [(int, int)]: returns the positions of the line
        """
        while True:
            x = self.rng.integers(0, self.height)
            y = self.rng.integers(0, self.width)

            if self.wall(x, y):
                continue

            vertical = bool(self.rng.integers(2))
            signum = self.rng.choice([-1, 1])

            if vertical:
                ys = [y + i * signum for i in range(width)]
                positions = [(x, new_y) for new_y in ys]

            else:
                xs = [x + i * signum for i in range(width)]
                positions = [(new_x, y) for new_x in xs]

            valid = True
            for pos in positions:
                if self.terminal(pos[0], pos[1]):
                    valid = False

            if not valid:
                continue
            else:
                return positions

    def spawn_lines(self, width_goal_line):
        """randomly sets a new goal line of the given width. Reinitializes the distances.

        Args:
            width_goal_line ([type]): width of the goal line to spawn.
        """
        self.height, self.width, self.map = parser.parse_file(
            self.map_path,
            replace_goals=True,
            surround_with_walls=self.surround_with_walls,
        )

        #         self.starters = []
        self.goals = []

        #         first = self.random_line()
        second = self.random_line(width_goal_line)

        #         self.starters = first
        #         for x,y in self.starters:
        #             self.map[x] = self.map[x][:y] + 's' + self.map[x][y+1:]

        self.goals = second
        for x, y in self.goals:
            self.map[x] = self.map[x][:y] + "g" + self.map[x][y + 1 :]

        self.init_distances()

    def init_distances(self):
        """computes and stores the distances from every position to the current goal line and all the wall tiles."""
        distances = np.zeros((self.height, self.width)).tolist()

        for x in range(self.height):
            for y in range(self.width):
                if self.terminal(x, y):
                    all_d = np.zeros(11).tolist()
                else:
                    d = self.calculate_wall_distances(x, y)
                    dg = self.calculate_goal_distances(x, y)
                    all_d = d + dg
                distances[x][y] = all_d
        self.distances = distances

    def __init__(self, map_name, surround_with_walls, rng):
        """creates a map instance. Parses the map file with the provided name. If surround_with_walls is set, addionall wall tiles around the map are created.

        Args:
            map_name ([string]): name of the map file
            surround_with_walls (bool): flag to surround the map with addional wall tiles.

        """
        self.rng = rng
        self.surround_with_walls = surround_with_walls
        self.map_name = map_name

        if not self.map_name.endswith(".track"):
            self.map_name += ".track"

        found_map_file = False
        possible_paths = [
            Path("./maps/"),
            Path(__file__).parent.joinpath("maps"),
        ]
        extended_possible_paths = []
        for path in possible_paths:
            try:
                for name in os.listdir(path):
                    current_extended_path = path.joinpath(name)
                    if os.path.isdir(current_extended_path):
                        extended_possible_paths.append(current_extended_path)
            except FileNotFoundError:
                # only one of the two above locations exists, so ignore is some possible dirs don't exist
                pass

        for path in possible_paths + extended_possible_paths:
            self.map_path = path.joinpath((self.map_name))
            if os.path.exists(self.map_path):
                found_map_file = True
                break

        if not found_map_file:
            logging.error(
                "Specified map file does not exist or at least couldn't be found: %s"
                % self.map_name
            )

        self.height, self.width, self.map = parser.parse_file(
            self.map_path, surround_with_walls=self.surround_with_walls
        )

        self.starters = []
        self.goals = []
        self.spawnable_positions = []
        for i, row in enumerate(self.map):
            for j, sign in enumerate(row):
                if sign == "s":
                    self.starters.append((i, j))
                    self.spawnable_positions.append((i, j))
                if sign == "g":
                    self.goals.append((i, j))
                if sign == ".":
                    self.spawnable_positions.append((i, j))

        self.dict = {
            0: (-1, -1),
            1: (0, -1),
            2: (1, -1),
            3: (-1, 0),
            4: (0, 0),
            5: (1, 0),
            6: (-1, 1),
            7: (0, 1),
            8: (1, 1),
        }

        self.init_distances()
        #         create distance and goal-distance features

    def calculate_goal_distances(self, x, y):
        """Compute the goal distances for the given position.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            [(int, int, int)]: triple of dx, dy and sum of absolute values of the two former.
        """
        pos = np.array((x, y))

        dx = self.height + 1
        dy = self.width + 1
        d_m = dx + dy
        for goal in self.goals:
            g = np.array(goal)
            d = g - pos
            m = np.abs(d[0]) + np.abs(d[1])
            if m < d_m:
                dx = d[0]
                dy = d[1]
                d_m = m
        return [dx, dy, d_m]

    def calculate_wall_distances(self, x, y):
        """calculates the wall distances for the given position.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            array [int]: returns the eight wall-distance values
        """

        pos = np.array((x, y))
        res = np.zeros(8)

        x_directions = [-1, 0, 1, -1, 1, -1, 0, 1]
        y_directions = [-1, -1, -1, 0, 0, 1, 1, 1]

        for i, (dx, dy) in enumerate(zip(x_directions, y_directions)):
            direction = np.array((dx, dy))
            distance = 1
            while True:
                checking_coordinate = pos + distance * direction
                if self.wall(checking_coordinate[0], checking_coordinate[1]):
                    res[i] = distance
                    break
                distance += 1

        return res.tolist()

    def terminal(self, x, y):
        """whether the given position is a terminal one, i.e., wall, goal, or outside of the map.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            (bool): true if terminal, false else.
        """
        if (
            x < 0
            or y < 0
            or x >= self.height
            or y >= self.width
            or ((x, y) in self.goals)
        ):  # this is not the hole trueth!
            return True
        return self.map[x][y] == "x"

    def wall(self, x, y):
        """whether the given position is a wall one.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            (bool): true if wall, false else.
        """
        if x < 0 or y < 0 or x >= self.height or y >= self.width:
            return True
        return self.map[x][y] == "x"

    def __eq__(self, other):
        if other is None:
            return False

        return other.map_name == self.map_name


class Environment:
    """class representing the racetrack game."""

    def __init__(self, rt_args: Namespace, clone_call: bool = False):
        """initializes an object of the class with the given arguments.

        Args:
            rt_args (Namespace): contains all the rt arguments to use. see argument_parser.py
            clone_call (bool, optional): if set to true, most steps of the init will be skipped because the env will be cloned anyway. Defaults to False.
        """
        self.rt_args = rt_args

        self.noisy = rt_args.noise
        self.random_start = rt_args.random_start
        self.random_velocity = rt_args.random_velocity
        self.landmarking = rt_args.landmarking
        self.gamma = rt_args.gamma

        # initialise environment rng
        self.rng = np.random.default_rng(rt_args.seed)

        if not clone_call:
            self.surround_with_walls = rt_args.surround_with_walls
            self.map = Map(rt_args.map_name, self.surround_with_walls, self.rng)

            if self.random_start:
                x = self.rng.integers(low=0, high=self.map.height)
                y = self.rng.integers(low=0, high=self.map.width)
                while self.map.terminal(x, y):
                    x = self.rng.integers(low=0, high=self.map.height)
                    y = self.rng.integers(low=0, high=self.map.width)
                self.position = np.array([x, y])
            else:
                self.position = np.array(self.rng.choice(self.map.starters))

            if self.random_velocity:
                vx = self.rng.integers(0, rt_args.maximal_random_velocity)
                vy = self.rng.integers(0, rt_args.maximal_random_velocity)
            else:
                vx = 0
                vy = 0
            self.velocity = np.array((vx, vy))

            self.done = False

            self.path = [self.position]

            if self.landmarking:
                self.potentials = self.read_potential_map()

    def spawn_lines(self):
        """spawns a new, randomly placed goal line."""
        self.map.spawn_lines(self.rt_args.width_goal_line)

    def read_potential_map(self):
        """reads the potentials from a potential file that corresponds to the given map file. Useful for reward shaping.


        Returns:
            array (int): two-dimensional array containing the potentials.
        """
        other_name = self.map.map_path[:-5] + "potentials"
        f = open(other_name, "r+")
        potential_array = np.zeros((self.map.height, self.map.width))

        for j, line in enumerate(f):
            for i, sign in enumerate(line.split()):
                if not self.map.wall(j, i):
                    # todo: 2x is an experiment, remove this
                    potential_array[j][i] = 2 * int(sign)

        return potential_array

    def __eq__(self, other):
        """checks equality of this and the other instance of the rt game

        Args:
            other (Racetrack): other instance of rt game.

        Returns:
            bool: True, if position and velocity are equal. False otherwise.
        """
        if other is None:
            return False
        return (
            (self.position == other.position).all()
            and (self.velocity == other.velocity).all()
            and self.map == other.map
        )

    def clone(self, deep=False):
        """creates a clone of the current instance.

        Args:
            deep (bool, optional): Whether to make a deep clone (also cloning the map and the rng) or just using the references. Defaults to False.

        Returns:
            [type]: [description]
        """
        oe = Environment(
            rt_args=self.rt_args,
            clone_call=True,
        )
        if deep:
            oe.map = copy.deepcopy(self.map)
            oe.rng = copy.copy(self.rng)
        else:
            oe.map = self.map
            oe.rng = self.rng

        oe.position = copy.copy(self.position)
        oe.velocity = copy.copy(self.velocity)
        oe.path = copy.copy(self.path)
        oe.done = copy.copy(self.done)

        if self.landmarking:
            oe.potentials = copy.copy(self.potentials)

        return oe

    def calculate_intermediates(self, x, y, dx, dy):
        """provides all intermediates when steering with velocity dx dy starting in x y

        Args:
            x (int): x-value of position
            y (int): y-value of position
            dx (int): x-value of velocity
            dy (int): y-value of velocity

        Returns:
            [type]: [description]
        """
        # trivial case:
        if dx == 0 and dy == 0:
            return [(x, y)]
        res = []
        # case 1, dx == 0
        if dx == 0:
            # each possible y value
            m = np.sign(dy)  # evaluates to 1 or -1, dependend of dy>0 or dy<0
            for i in range(np.abs(dy) + 1):
                res.append((x, y + i * m))
            return res
        # case 2, dy == 0
        if dy == 0:
            m = np.sign(dx)  # evaluates to 1 or -1, dependend of dx>0 or dx<0
            for i in range(np.abs(dx) + 1):
                res.append((x + i * m, y))
            return res
        # case 3, dx and dy != 0, |dx| > |dy|
        if np.abs(dx) >= np.abs(dy):
            m_y = dy / np.abs(dx)
            m_x = np.sign(dx)
            for i in range(np.abs(dx) + 1):
                act_x = int(x + i * m_x)
                act_y = int(_round(y + i * m_y))
                res.append((act_x, act_y))
            return res
        # case 4
        if np.abs(dx) < np.abs(dy):
            m_x = dx / np.abs(dy)
            m_y = np.sign(dy)
            for i in range(np.abs(dy) + 1):
                act_y = int(y + i * m_y)
                act_x = int(_round(x + i * m_x))
                res.append((act_x, act_y))
            return res

    def show(
        self,
        hide_positions=False,
        graphical=False,
        show_landmarks=False,
        additional_return=False,
        hide_start_line=False,
    ):
        """method to show the current state of the rt game.

        Args:
            hide_positions (bool, optional): hide positions, show map only. Defaults to False.
            graphical (bool, optional): use graphical representation intead of string one. Defaults to False.
            show_landmarks (bool, optional): visualize the landmarks. Defaults to False.
            additional_return (bool, optional): additionally to showing the picture, return it. May be used to save the graphical representation. Defaults to False.
            hide_start_line (bool, optional): hide start line. Defaults to False.

        Returns:
            img: potentially the image
        """
        if graphical:
            pic = g.create_map(
                self,
                show_path=(not hide_positions),
                show_landmarks=show_landmarks,
                hide_start_line=hide_start_line,
            )
            if additional_return:
                return pic
        else:
            show = []
            for line in self.map.map:
                show.append(list(line))

            if not hide_positions:
                for i, position in enumerate(self.path):
                    logging.debug(
                        "env.show, iteration %i with position %s", i, str(position)
                    )
                    x, y = _discretize_position(position)
                    if not (
                        x < 0 or y < 0 or x >= self.map.height or y >= self.map.width
                    ):
                        show[x][y] = str((i % 10))

            for line in show:
                print("".join(line))

            if additional_return:
                return show

    def reward(self, old_position):
        """reward function. Depends on the arguments set by rt_args in the init step.

        Args:
            old_position ((int, int))): old position

        Returns:
            [int]: computed reward function.
        """
        res = self.rt_args.step_reward

        if self.rt_args.continuous:
            old_position = _discretize_position(old_position)
            position_discret = _discretize_position(self.position)
            velocity = np.array(position_discret) - np.array(old_position)
        else:
            velocity = copy.copy(self.velocity)

        intermediates = self.calculate_intermediates(
            old_position[0], old_position[1], velocity[0], velocity[1]
        )

        for intermediate in intermediates:
            if intermediate in self.map.goals:
                logging.debug("Reached goal, position: %s", str(intermediate))
                self.done = True
                res = self.rt_args.positive_reward
                break
            if self.map.wall(intermediate[0], intermediate[1]):
                logging.debug("Crashed, position: %s", str(intermediate))
                self.done = True
                res = self.rt_args.negative_reward
                break

        # For all terminal states (win and lose!) the potential must be zero to preserve the optimal policy
        if self.landmarking:
            if res != self.rt_args.step_reward:
                potential_to = 0
            else:
                new_pos = intermediates[-1]
                potential_to = self.potentials[new_pos[0]][new_pos[1]]
            potential_from = self.potentials[old_position[0]][old_position[1]]

            F = self.gamma * potential_to - potential_from

            res += F

        return res

    def light_step(self, action):
        """perform a light step, i.e., clone the environment, perform the action, return the clone.

        Args:
            action (int or float): action to apply in the clone
            clone_rng (bool, optional): see Environment.clone

        Returns:
            (Environment): other instance of this class
        """
        other_env = self.clone()
        res = other_env.step(action)
        return other_env, res

    def step(self, action):
        """Center piece of this class. Performs the given action in the racetrack game. Action is either int or float, depending on the game variant.

        Args:
            action (int or float): action to apply

        Returns:
            (int, array [int], bool): reward, state reached, termination flag.
        """
        if self.done:
            print("Already done, step has no further effect")
            return self.rt_args.step_reward, (self.position, self.velocity), self.done

        if self.rt_args.continuous:
            x_action = action[0]
            y_action = action[1]
            assert (
                -1 <= x_action <= 1 and -1 <= y_action <= 1
            ), "both ct actions must be in [-1,1]"
        else:
            action = np.array(self.map.dict[action])

        # NOISE!
        if self.noisy:
            if self.rng.random() < self.rt_args.noise_probability:
                # 4 is the number of action doing nothing
                action = 4
                action = np.array(self.map.dict[action])

        self.velocity = self.velocity + action
        old_position = self.position
        self.position = self.position + self.velocity

        self.path.append(self.position)

        # call reward function
        reward = self.reward(old_position=old_position)

        # actually, the state is defined through pos and velocity and the distances are only features
        # for reasons of simpler implementation, the features here are returned together with the state
        state = self.get_state()
        return reward, state, self.done

    def reset(self):
        """reset the rt game. Must be used before starting a new training episode.

        Returns:
            array [int]: initial state.
        """
        if self.random_start:
            x = self.rng.integers(0, self.map.height)
            y = self.rng.integers(0, self.map.width)
            while self.map.terminal(x, y):
                x = self.rng.integers(0, self.map.height)
                y = self.rng.integers(0, self.map.width)
            self.position = np.array([x, y])
        else:
            self.position = np.array(self.rng.choice(self.map.starters))

        if self.random_velocity:
            vx = self.rng.integers(0, self.rt_args.maximal_random_velocity)
            vy = self.rng.integers(0, self.rt_args.maximal_random_velocity)
        else:
            vx = 0
            vy = 0
        self.velocity = np.array((vx, vy))

        self.done = False

        self.path = [self.position]

        return self.get_state()

    def reset_to_state(self, pos, velo=None):
        """resets the game and sets the position (and possibly velocity) to the given values. If no velocity is given, it is chosen acording to the current game mode.

        Args:
            pos ((int,int)): position to reset the rt game to.
            velo ((int,int), optional): velocity to reset the rt game to. Defaults to None.
        """
        self.reset()

        self.position = np.array(pos)

        if velo is not None:
            self.velocity = np.array(velo)

        self.path = [self.position]

    def calculate_children(self):
        """calculate all possible sucessor states

        Returns:
            array [int, array[int]]: array containing the applied action and the resulting successor.
        """
        res = []
        for action in range(9):
            acc = self.map.dict[action]
            vel = self.velocity + acc
            pos = self.position - vel
            res.append(
                (action, list(pos) + list(vel) + self.map.distances[pos[0]][pos[1]])
            )

        return res

    def get_graphical_state(self):
        """get state represented by an greyscale image

        Returns:
            two dimensional array [int]: array containing the greyscale values
        """
        res = np.zeros((self.map.height, self.map.width))

        for i, row in enumerate(self.map.map):
            for j, sign in enumerate(row):
                if self.position[0] == i and self.position[1] == j:
                    # v = 0.5
                    v = 1 / 3
                    res[i][j] = v
                else:
                    if sign == "g":
                        v = 1
                        res[i][j] = v
                        continue
                    # there is absolutely no difference between a starting state and a normal state
                    # during a race -> thus we handle it equally
                    if sign == "." or sign == "s":
                        v = 0
                        res[i][j] = v
                        continue
                    if sign == "x":
                        # v = 0.5
                        v = 2 / 3
                        res[i][j] = v
                        continue
                    print("could not identify ", sign)

        return [res, self.velocity]

    def get_state(self):
        """value-based representation of the current state.

        Returns:
            array[int or float]: current state.
        """
        if self.rt_args.continuous:
            x, y = _discretize_position(self.position)
        else:
            x, y = self.position
        if not self.done:
            return list(self.position) + list(self.velocity) + self.map.distances[x][y]
        else:
            return list(self.position) + list(self.velocity) + np.zeros(11).tolist()

    def applicable_actions(self):
        """returns list of applicable actions. Actually, this is a kind of lazy method, as for the rt game, this is (nearly) always the same. Still, is is neede by some algorithms.

        Returns:
            array [int]: list of applicable actions.
        """
        if not self.done:
            return [i for i in range(9)]
        else:
            return []

    def get_state_rep(self, pos, velo=None):
        """
        Given a position (x,y) and a velocity (optional (x,y))

        Returns:
            array[int or float]: state representation with given position and velocity (or (0,0)
                                 if not specified)
        """
        if velo is None:
            velo = (0, 0)

        if self.rt_args.continuous:
            x, y = _discretize_position(pos)
        else:
            x, y = pos

        return list(pos) + list(velo) + self.map.distances[x][y]
