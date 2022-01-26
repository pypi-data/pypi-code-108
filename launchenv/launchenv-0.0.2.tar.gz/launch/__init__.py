import os
from .utils.utils import PATH

if not os.path.exists(PATH):
    os.makedirs(PATH)
else:
    pass