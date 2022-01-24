#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from gym.envs.registration import register

register(
    id='update-v0',
    entry_point='gym_update.envs:UpdateEnv',
)

