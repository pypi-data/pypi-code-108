from datetime import datetime, time, timedelta
import numpy as np
import regex as re
from xarray import open_dataset

from benedict.dicts import benedict as Benedict
from mosartwmpy.grid.grid import Grid
from mosartwmpy.state.state import State
from mosartwmpy.utilities.timing import timing


# @timing
def load_runoff(state: State, grid: Grid, config: Benedict, current_time: datetime) -> None:
    """Loads runoff from file into the state for each grid cell.

    Args:
        state (State): the current model state; will be mutated
        grid (Grid): the model grid
        config (Benedict): the model configuration
        current_time (datetime): the current time of the simulation
    """
    
    # note that the forcing is provided in mm/s
    # the flood section needs m3/s, but the routing needs m/s, so be aware of the conversions
    # method="pad" means the closest time in the past is selected from the file

    # runoff path can have placeholders for year and month and day, so check for those and replace if needed
    path = config.get('runoff.path')
    path = re.sub('\{y[^}]*}', current_time.strftime('%Y'), path)
    path = re.sub('\{m[^}]*}', current_time.strftime('%m'), path)
    path = re.sub('\{d[^}]*}', current_time.strftime('%d'), path)

    runoff = open_dataset(path)
    
    sel = {
        config.get('runoff.time'): current_time
    }

    current_runoff = runoff.sel(sel, method='pad').load()
    
    if config.get('runoff.variables.surface_runoff', None) is not None:
        state.hillslope_surface_runoff = 0.001 * grid.land_fraction * grid.area * current_runoff[
            config.get('runoff.variables.surface_runoff')].values.flatten()
    
    if config.get('runoff.variables.subsurface_runoff', None) is not None:
        state.hillslope_subsurface_runoff = 0.001 * grid.land_fraction * grid.area * current_runoff[
            config.get('runoff.variables.subsurface_runoff')].values.flatten()
    
    if config.get('runoff.variables.wetland_runoff', None) is not None:
        state.hillslope_wetland_runoff = 0.001 * grid.land_fraction * grid.area * current_runoff[
            config.get('runoff.variables.wetland_runoff')].values.flatten()
    
    runoff.close()
