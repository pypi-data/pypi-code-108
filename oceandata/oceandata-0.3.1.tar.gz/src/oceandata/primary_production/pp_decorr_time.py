
import functools

import numpy as np
import pandas as pd
import xarray as xr

import primary_production
from input_fields import match, oc_cci_day, ostia, modis, seawifs, read_pp
from algorithms import primary_production as pp_algos

def match_months():
    kw = dict(days_ahead=30, days_behind=30)

    df = pd.read_hdf("h5files/mattei_pp_global_sat.h5")
    obs_id = np.arange(len(df))[df.index>"1998-01-01"]
    df = df[df.index>"1998-01-01"]
 
    mt = match.Match(oc_cci_day.open_dataset)
    chlarr   = mt.multiday(df.lon, df.lat, df.index, data_var="chlor_a", **kw)
    kd490arr = mt.multiday(df.lon, df.lat, df.index, data_var="kd_490",  **kw)

    mt = match.Match(ostia.open_dataset)
    sstarr = mt.multiday(df.lon, df.lat, df.index, data_var="analysed_sst",**kw)

    modis.open_dataset = functools.partial(modis.open_dataset, timetype="day")
    mask = df.index>"2003-01-01"
    marr = np.full(chlarr.shape, np.nan)
    mt = match.Match(modis.open_dataset)
    marr[mask,:] = mt.multiday(df.lon[mask], df.lat[mask], df.index[mask], 
                               data_var="par", **kw)
    seawifs.open_dataset = functools.partial(seawifs.open_dataset, timetype="day")
    mask = df.index<"2005-12-31"
    sarr = np.full(chlarr.shape, np.nan)
    mt = match.Match(seawifs.open_dataset)
    sarr[mask,:] = mt.multiday(df.lon[mask], df.lat[mask], df.index[mask], 
        data_var="par", **kw)
    pararr = np.nanmean((marr,sarr),axis=0)

    ds = xr.Dataset({"chl"  :(("obs_id","delta_day"), chlarr), 
                     "SST"  :(("obs_id","delta_day"), sstarr), 
                     "kd490":(("obs_id","delta_day"), kd490arr), 
                     "PAR"  :(("obs_id","delta_day"), pararr)},
                     coords={"obs_id":obs_id, "delta_day":np.arange(-30,31)})
    return ds
    #ds.to_netcdf("ncfiles/PP_mattei_sat_delta_day.nc")


def ifado_months():
    kw = dict(days_ahead=30, days_behind=30)
    df = pd.read_hdf("h5files/mattei_pp_global_sat.h5")
    obs_id = np.arange(len(df))[df.index>"1998-01-01"]
    df = df[df.index>"1998-01-01"]
    mt = match.Match(read_pp.ifado) if mt is None else mt
    pparr = mt.multiday(df.lon, df.lat, df.index, data_var="PP", **kw)
    ds = xr.Dataset({"PP"   :(("obs_id","delta_day"), pparr)},
        coords={"obs_id":obs_id, "delta_day":np.arange(-30,31)})
    return ds



def rf_predict_dday():
    model = primary_production.rf_mattei()
    ds = xr.open_dataset("ncfiles/PP_mattei_sat_delta_day.nc")
    df = pd.read_hdf("h5files/mattei_pp_global_sat.h5")
    df = df[df.index>"1998-01-01"]

    def replace_day(dday):
        df["kd_490"] = ds["kd490"][:,30+dday].values
        df["sat_Zeu"] = 4.6/ds["kd490"][:,30+dday].values
        df["sst"] = ds["SST"][:,30+dday].values
        df["sat_par"] = ds["PAR"][:,30+dday].values
        X = df[["lat", "lon", "sat_chl", "sst", "sat_par", "depth", "kd_490", 
                "sat_Zeu", "longhurst", "month","PP"]]
        X.dropna(inplace=True)
        y = np.log(X["PP"])
        del X["PP"]
        return X,y

    r2list = []
    for dday in np.arange(-30,31):
        X,y = replace_day(dday)
        r2list.append(model.score(X, y))
    return r2list

def ifado_predict_dday():
    ds = xr.open_dataset("ncfiles/PP_ifado_delta_day.nc")
    df = pd.read_hdf("h5files/mattei_pp_global_sat.h5")
    df = df[df.index>"1998-01-01"]
    df["PP"] = np.log(df["PP"])
    r2list = []
    for dday in np.arange(-30,31):
        r2list.append(primary_production.calc_r2(df.PP, 
                      np.log(ds["PP"][:,30+dday].values*1000)))
    return r2list

def vgpm_predict_dday():

    ds = xr.open_dataset("ncfiles/PP_mattei_sat_delta_day.nc")
    pb_opt = pp_algos.pb_opt(ds.SST.values)
    df = pd.read_hdf("h5files/mattei_pp_global_sat.h5")
    df = df[df.index>"1998-01-01"]
    daylen = pp_algos.daylength(df.index, df.lat).values[:,None] + (pb_opt*0)
    vgpm_pp = pp_algos.VGPM_1997(ds.chl, ds.PAR, 4.6/ds.kd490, pb_opt, daylen)
    r2list = []
    for dday in np.arange(-30,31):
        r2list.append(primary_production.calc_r2(np.log(df.PP), 
                      np.log(vgpm_pp[:,30+dday].values)))
    return r2list