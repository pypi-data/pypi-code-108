import gym
from gym import error, spaces, utils
from gym.utils import seeding
from collections import OrderedDict
import numpy as np

SIZE = 10
MOVE_REWARD = -1
HUNTER_REWARD = -300
TARGET_REWARD = 25

class OpenEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, width=SIZE, height=SIZE):

        self.width = width
        self.height = height


        self.target =  None
        self.player = None
        self.hunter = None

        self.reward = 0
        self.done = False
        self.info = {}
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Dict({
        'distanceTarget': spaces.Box(low=-SIZE + 1, high=SIZE - 1, shape=(2,), dtype=np.int32),
        'distanceEnemy':spaces.Box(low=-SIZE + 1, high=SIZE - 1, shape=(2,), dtype=np.int32)})
        self.isrendering = False
        self.deterministic = True


    def step(self, action):
      """Run one timestep of the environment's dynamics. When end of
      episode is reached, you are responsible for calling `reset()`
      to reset this environment's state.

      Accepts an action and returns a tuple (observation, reward, done, info).

      Args:
          action (object): an action provided by the agent

      Returns:
          observation (object): agent's observation of the current environment
          reward (float) : amount of reward returned after previous action
          done (bool): whether the episode has ended, in which case further step() calls will return undefined results
          info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
      """

      # Expected Actions:
      # 0: Up-Right movement
      # 1: Down-Left movement
      # 2: Up-Left movement
      # 3: Down-Right movement

      # Player movement

      self.player.action(action)

      pos = np.clip([self.player.x, self.player.y], 0, [self.width-1, self.height-1])
      self.player.newpos(pos[0], pos[1])

      obs = OrderedDict([('distanceEnemy', self.hunter - self.player),
      ('distanceTarget', self.target - self.player)])

      self.reward += MOVE_REWARD

      if obs['distanceEnemy'] == [0,0]:
          self.reward += HUNTER_REWARD
          self.done = True
      if obs['distanceTarget'] == [0,0]:
          self.reward += TARGET_REWARD
          self.done = True

      return obs, self.reward, self.done, self.info

    def reset(self):
        """Resets the environment to an initial state and returns an initial
        observation.

        Note that this function should not reset the environment's random
        number generator(s); random variables in the environment's state should
        be sampled independently between multiple calls to `reset()`. In other
        words, each call of `reset()` should yield an environment suitable for
        a new episode, independent of previous episodes.

        Returns:
          observation (object): the initial observation.
        """
        self.done = False
        self.reward = 0

        # REVIEW: Save the info?

        self.info = {}


        if not self.deterministic:
            self.target = self.AnimatedObject()
            self.player = self.AnimatedObject()
            self.hunter = self.AnimatedObject()
        else:
            self.target = self.AnimatedObject([9,9])
            self.player = self.AnimatedObject([0,0])
            self.hunter = self.AnimatedObject([4,4])

        return OrderedDict([('distanceEnemy', self.hunter - self.player),
        ('distanceTarget', self.target - self.player)])

    def render(self, mode='human'):
      """Renders the environment.

      The set of supported modes varies per environment. (And some
      environments do not support rendering at all.) By convention,
      if mode is:

      - human: render to the current display or terminal and
        return nothing. Usually for human consumption.
      - rgb_array: Return an numpy.ndarray with shape (x, y, 3),
        representing RGB values for an x-by-y pixel image, suitable
        for turning into a video.
      - ansi: Return a string (str) or StringIO.StringIO containing a
        terminal-style text representation. The text can include newlines
        and ANSI escape sequences (e.g. for colors).

      Note:
          Make sure that your class's metadata 'render.modes' key includes
            the list of supported modes. It's recommended to call super()
            in implementations to use the functionality of this method.

      Args:
          mode (str): the mode to render with

      Example:

      class MyEnv(Env):
          metadata = {'render.modes': ['human', 'rgb_array']}

          def render(self, mode='human'):
              if mode == 'rgb_array':
                  return np.array(...) # return RGB frame suitable for video
              elif mode == 'human':
                  ... # pop up a window and render
              else:
                  super(MyEnv, self).render(mode=mode) # just raise an exception
      """
      if not self.isrendering:
          self.isrendering = True
      pass


    def close(self):
      """Override close in your subclass to perform any necessary cleanup.

      Environments will automatically close() themselves when
      garbage collected or when the program exits.
      """
      pass

    def stochastic(self, stoc = False):
        self.deterministic = stoc


    class AnimatedObject():
        """Internal object to generate the interactive objects"""

        def __init__(self, pos = None):
            if not pos:
                self.x = np.random.randint(0, SIZE)
                self.y = np.random.randint(0, SIZE)
            else:
                self.x = pos[0]
                self.y = pos[1]

        def __str__(self):
            return f"{self.x}, {self.y}"
        def __sub__(self, other):
            return np.array([self.x-other.x, self.y-other.y], np.int32)
        def action(self, choice):
            '''
            Gives us 4 total movement options. (0,1,2,3)
            '''
            if choice == 0:
                self.move(x=1, y=1)
            elif choice == 1:
                self.move(x=-1, y=-1)
            elif choice == 2:
                self.move(x=-1, y=1)
            elif choice == 3:
                self.move(x=1, y=-1)

        def move(self, x, y):
            self.x += x
            self.y += y

        def newpos(self, x, y):
            self.x = x
            self.y = y
