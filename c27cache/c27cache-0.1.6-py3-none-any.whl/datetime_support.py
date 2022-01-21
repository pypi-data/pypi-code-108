import pytz
from bisect import bisect
from datetime import datetime, timedelta, timezone as tz
from pytz import timezone
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

asia_kolkata = timezone('Asia/Kolkata')
utc          = timezone('UTC')

def time_diff(dt1:datetime, dt2:datetime) -> relativedelta:
    return relativedelta(dt1, dt2)

def to_IST(event_timestamp:datetime, tz:pytz.timezone=asia_kolkata):    
    """
    >>> to_IST('2020-07-13T05:30:00.000+00:00')
    datetime.datetime(2020, 7, 13, 11, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    if isinstance(event_timestamp, datetime):   dt = event_timestamp
    else:                                       dt = dateutil_parser.parse(event_timestamp)
    
    return dt.astimezone(tz)

def to_UTC(event_timestamp:datetime, tz:pytz.timezone=utc):    
    """
    >>> to_IST('2020-07-13T05:30:00.000+00:00')
    datetime.datetime(2020, 7, 13, 11, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    if isinstance(event_timestamp, datetime):   dt = event_timestamp
    else:                                       dt = dateutil_parser.parse(event_timestamp)
    
    return dt.astimezone(tz)  

def to_UTC_without_tz(event_timestamp:str, format:str="%Y-%m-%d %H:%M:%S.%f"):
    dt = datetime.strptime(event_timestamp, format)
    return dt.astimezone(tz.utc).strftime(format)

def beginning_of_day(dt:datetime):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> beginning_of_day(dt)
    datetime.datetime(2020, 7, 13, 0, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    dt = dt.replace(minute=0, hour=0, second=0, microsecond=0)
    return dt

def end_of_day(dt:datetime):
    """    
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0)
    >>> end_of_day(dt.astimezone(asia_kolkata))
    datetime.datetime(2020, 7, 13, 23, 59, 59, 999999, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    dt = dt.replace(minute=59, hour=23, second=59, microsecond=999999)
    return dt

def minutes_ago(dt:datetime, days:int=0, hours:int=0, minutes:int=1, seconds:int=0):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> hours_ago(dt, minutes=1)
    datetime.datetime(2020, 7, 12, 21, 2, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    past = dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)    
    return past  

def minutes_after(dt:datetime, days:int=0, hours:int=0, minutes:int=1, seconds:int=0):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> hours_ago(dt, minutes=1)
    datetime.datetime(2020, 7, 13, 21, 4, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    past = dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)    
    return past     

def hours_ago(dt:datetime, days:int=0, hours:int=1, minutes:int=0, seconds:int=0):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> hours_ago(dt, hours=1)
    datetime.datetime(2020, 7, 12, 20, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    past = dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)    
    return past 

def days_ago(dt:datetime, days:int=1, hours:int=0, minutes:int=0, seconds:int=0):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> days_ago(dt)
    datetime.datetime(2020, 7, 12, 21, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    past = dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds) 
    if dt.tzinfo:
        past=past.replace(tzinfo=dt.tzinfo)
    return past 

def months_ago(dt:datetime, months:int=1):
    """    
    >>> dt = datetime.now().replace(year=2020, month=7, day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> months_ago(dt, months=5)
    datetime.datetime(2020, 2, 13, 21, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)    
    """
    past = (dt - relativedelta(months=months))
    return past

def months_after(dt:datetime, months:int=1):
    """    
    >>> dt = datetime.now().replace(year=2020, month=7, day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> months_ago(dt, months=5)
    datetime.datetime(2020, 2, 13, 21, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)    
    """
    past = (dt + relativedelta(months=months))
    return past

def years_ago(dt:datetime, years:int=1):
    past = (dt - relativedelta(years=years))
    if dt.tzinfo:
        past=past.replace(tzinfo=past.tzinfo)
    return past

def days_after(dt:datetime, days:int=1, hours:int=0, minutes:int=0, seconds:int=0):
    """
    >>> dt = datetime.now().replace(day=13, hour=21, minute=3, second=3, microsecond=0).astimezone(asia_kolkata)
    >>> days_after(dt)
    datetime.datetime(2020, 7, 14, 21, 3, 3, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    future = dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if dt.tzinfo:
        future=future.replace(tzinfo=dt.tzinfo)
    return future

def is_today(dt:datetime):    
    return dt.astimezone(asia_kolkata).day == datetime.now().astimezone(asia_kolkata).day

def is_yesterday(dt:datetime):
    return dt.astimezone(asia_kolkata).day == days_ago(datetime.now().astimezone(asia_kolkata)).day

def is_tomorrow(dt:datetime):
    return dt.astimezone(asia_kolkata).day == days_after(datetime.now().astimezone(asia_kolkata)).day

def IST_time(): 
    return datetime.now().astimezone(asia_kolkata)
    
def tz_now(tz:pytz=utc):
    dt = datetime.utcnow()
    return dt.replace(tzinfo=tz)

def tz_from_iso(dt:str, to_tz:pytz=utc, format='%Y-%m-%dT%H:%M:%S.%f%z') -> datetime:
    date_time = datetime.strptime(dt,format)
    return date_time.astimezone(to_tz)

def start_of_week(dt:str, to_tz:pytz=utc) -> datetime:
    day_of_the_week = dt.weekday()
    return days_ago(dt=dt, days=day_of_the_week)

def end_of_week(dt:str, to_tz:pytz=utc) -> datetime:    
    _start_of_week = start_of_week(dt=dt, to_tz=to_tz)
    return days_after(dt=_start_of_week, days=6)

def end_of_last_week(dt:str, to_tz:pytz=utc):
    _end_of_current_week = end_of_week(dt=dt, to_tz=to_tz)
    return days_ago(dt=_end_of_current_week, days=7)


    


