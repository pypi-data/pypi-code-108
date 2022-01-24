import datetime

def get_utc_now():
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    return now

def convert_date_to_timestamp(vNgayThang):
    try:
        if vNgayThang is not None:
            return round(vNgayThang.replace(tzinfo=datetime.timezone.utc).timestamp())
        else:
            return None
    except:
        return None

def convert_timestamp_to_date_utc(timestamp):
    try:
        if timestamp is not None:
            return datetime.datetime.utcfromtimestamp(timestamp).replace(
                tzinfo=datetime.timezone.utc
            )
        else:
            return None
    except:
        return None

def get_timestamp_utc_now():
    return round(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp())
