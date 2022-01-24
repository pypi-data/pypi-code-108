import folium
from mobilipy.constants import *
from mobilipy.preparation import prepare
import pandas as pd

def get_map_bounds(df):
    bounds = [
      [df.latitude.min(), df.longitude.min()],
      [df.latitude.max(), df.longitude.max()]
    ]
    padding = abs((sum(bounds[0])-sum(bounds[1]))/20)

    bounds[0][0] = bounds[0][0] - padding
    bounds[0][1] = bounds[0][1] - padding
    bounds[1][0] = bounds[1][0] + padding
    bounds[1][1] = bounds[1][1] + padding

    return bounds

def plot_gps(df, loc_map=None, type_=TRANSPORT, line=True):
    """[summary]

    Args:
        df ([type]): [description]
        loc_map ([type], optional): [description]. Defaults to None.
        type_ ([type], optional): [description]. Defaults to TRANSPORT.
        line (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    #First, we set the bounds for the created map
    bounds = get_map_bounds(df)
    
    if loc_map is None:
        loc_map = folium.Map()
        loc_map.fit_bounds(bounds)
     
    #Then, we plot the points in lines
    points = df[['latitude', 'longitude', 'tracked_at']]
    
    if line:
        points = points[['latitude', 'longitude']].values.tolist()
        if(len(points) > 0):
            folium.PolyLine(points, color=color_type[type_]).add_to(loc_map)
            folium.RegularPolygonMarker(location=points[0], color=color_type[BEGINNING], number_of_sides=3, radius=10).add_to(loc_map)
            folium.RegularPolygonMarker(location=points[-1], color=color_type[END], number_of_sides=3, radius=10).add_to(loc_map)
    else:
        [folium.CircleMarker(point[:-1], color=color_type[type_], radius=5,
                             popup=folium.Popup(str(point[-1]), max_width=len(str(point[-1]))*20),opacity=0.5).add_to(loc_map) for point in points.values.tolist()]
    return loc_map

def plot_waypoints(waypoints, clean_df=True, map_=None):
        if clean_df:
            return plot_gps(prepare(waypoints), loc_map=map_, type_=CLEAN, line=False)
        else:
            return plot_gps(waypoints, loc_map=map_, type_=DIRTY, line=False)

def plot_solos(solos, map_=None):
    """Plots the solos DataFrame points
    Args:
        map_ ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    return plot_gps(solos, loc_map=map_, type_=SOLO, line=False)


def get_leg_points(legs_from_waypoints, clean_waypoints, index, info=False):
    """[summary]

    Args:
        index ([type]): [description]
        info (bool, optional): [description]. Defaults to False.
        gt (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    legs = legs_from_waypoints
    start = legs.iloc[index, legs.columns.get_loc('started_at')]
    end = legs.iloc[index, legs.columns.get_loc('finished_at')]
    leg = clean_waypoints[(clean_waypoints['tracked_at']>=start) & (clean_waypoints['tracked_at']<=end)]

    if info:
        day, start_time = start.split("T")
        end_time = end.split("T")[1]
        stats = leg[1:]
        inf = {
            'Leg number': index,
            'Day': day,
            'Start time': start_time,
            'End time': end_time,
            'Type': legs.iloc[index, legs.columns.get_loc('type')],
            'Num points': len(leg),
            'Mean speed': stats.calculated_speed.mean(), 'Max speed': stats.calculated_speed.max(), 'Min speed': stats.calculated_speed.min(),
        }
        return leg, inf
    else:
        return leg

def plot_leg(legs_from_waypoints, clean_waypoints, index, map_=None, info=False, gt=False):
    """[summary]

    Args:
        index ([type]): [description]
        map_ ([type], optional): [description]. Defaults to None.
        info (bool, optional): [description]. Defaults to False.
        gt (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    legs = legs_from_waypoints
    leg_ty = legs.iloc[index, legs.columns.get_loc('type')]
    if info:
        leg, info = get_leg_points(legs_from_waypoints, clean_waypoints, index, info=True)
        return leg, info, plot_gps(leg, loc_map=map_, type_=leg_ty)
    else:
        leg = get_leg_points(legs_from_waypoints, clean_waypoints, index)
        return leg, plot_gps(leg, loc_map=map_, type_=leg_ty)


def plot_legs(legs_from_waypoints, clean_waypoints, map_=None):
    df = pd.DataFrame()
    m = map_
    for i in range(len(legs_from_waypoints)):
        points_df, m = plot_leg(legs_from_waypoints, clean_waypoints, i, map_=m)
        df = df.append(points_df, ignore_index=True)
    
    if(df.shape[0]>0):
        bounds = get_map_bounds(df)
        m.fit_bounds(bounds)
    
    return m

def plot_daily_legs(legs_from_waypoints, waypoints, day_num, first_=0, last_=-1, map_=None, legs=True, dirty_waypoints=False, plot_waypoints=False, solos=False, gt=False):
    """[summary]

    Args:
        day_num ([type]): [description]
        first_ (int, optional): [description]. Defaults to 0.
        last_ (int, optional): [description]. Defaults to -1.
        map_ ([type], optional): [description]. Defaults to None.
        legs (bool, optional): [description]. Defaults to True.
        dirty_waypoints (bool, optional): [description]. Defaults to False.
        waypoints (bool, optional): [description]. Defaults to False.
        solos (bool, optional): [description]. Defaults to False.
        gt (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    
    legs = legs_from_waypoints.reset_index(drop=True)
    legs['start_day'] = legs.started_at.map(lambda date: date.split('T')[0])
    
    leg_days = sorted(legs.start_day.unique())
    
    day_legs =  legs_from_waypoints.groupby('start_day').get_group(leg_days[day_num])
    first, last = day_legs.index[first_], day_legs.index[last_]
    m = map_
    infos = []
    if dirty_waypoints:
        start, end = day_legs.iloc[first_].started_at, day_legs.iloc[last_].finished_at
        dirty_points = waypoints[(waypoints.tracked_at >= start) & (waypoints.tracked_at <= end)]
        m = plot_gps(dirty_points, loc_map=m, type_=DIRTY, line=False)

    for i in range(first, last + 1):
        if legs:
            _, m = plot_leg(i, map_=m, gt=gt)
        points_df, info = get_leg_points(legs_from_waypoints, i, info=True, gt=gt)
        infos.append(info)
        if plot_waypoints:
            m = plot_gps(points_df, loc_map=m, type_=CLEAN, line=False) 

    if solos:
        solos = pd.DataFrame([])
        start, end = day_legs.iloc[first_].started_at, day_legs.iloc[last_].finished_at
        solo_points = solos[(solos.tracked_at >= start) & (solos.tracked_at <= end)]
        m = plot_gps(solo_points, loc_map=m, type_=SOLO, line=False)
    return m, infos

def plot_all(legs_from_waypoints, waypoints):
    map_ = plot_waypoints(waypoints, clean_df=False)
    map_ = plot_waypoints(waypoints, map_=map_)
    map_ = plot_legs(legs_from_waypoints, waypoints, map_=map_)
    return map_