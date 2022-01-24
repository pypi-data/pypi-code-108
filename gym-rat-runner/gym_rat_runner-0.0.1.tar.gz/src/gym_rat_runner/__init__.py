from gym.envs.registration import register

register(
    id='open-v0',
    entry_point='gym_rat_runner.envs:OpenEnv',
    max_episode_steps=200,
    nondeterministic = True,
)
# register(
#     id='maze-v0',
#     entry_point='gym_rat_runner.envs:MazeEnv',
# )
