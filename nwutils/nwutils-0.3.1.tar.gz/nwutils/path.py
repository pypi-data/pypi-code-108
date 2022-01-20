import os
import numpy as np
from typing import List, Optional, Union
from pathlib import Path
from natsort import natsorted
from .logger import logger

def changeDirectory(Dir:Union[str, Path], expectExist:Optional[bool]=None):
	if isinstance(Dir, str):
		Dir = Path(Dir)
	assert isinstance(Dir, Path), f"Got: {Dir}"
	assert expectExist in (True, False, None)
	if expectExist in (True, False):
		assert Dir.exists() == expectExist, f"Exists: {Dir}"
	Dir.mkdir(exist_ok=True, parents=True)
	logger.info(f"Changing to working directory: {Dir}")
	os.chdir(Dir)

def getFilesFromDir(x:Path, pattern:str="*", N:int=None) -> List[Path]:
	y = Path(x)
	assert y.exists()
	y = y.glob(pattern)
	y = [str(x) for x in y]
	y = natsorted(y)
	y = [Path(x).absolute() for x in y]
	y = np.array(y)
	y = y[0:N] if N is not None else y
	return y
