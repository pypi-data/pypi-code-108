# File: ArangoDB Metadata and ORM support functions
# Author: alexsanchezvega
# Company: d20
# Version: 1.0

import json
from datetime import datetime, timedelta

def search_obj_cache(otype, okey):
    try:
        with open('obj_cache.json', 'r') as infile:
            cache = json.load(infile)
            if otype in cache:
                if okey in cache[otype]:
                    lifetime = timedelta(seconds=60)
                    expiration = datetime.strptime(cache[otype][okey]['ts_created'], '%c') + lifetime
                    if datetime.utcnow() >= expiration:
                        cache[otype].pop(okey)
                    else:
                        return [cache[otype][okey]['obj_dict'], cache[otype][okey]['obj_sch'], cache[otype][okey]['obj_schb']]
    except:
        clear_obj_cache()
    return None

def add_obj_cache(otype, okey, odict, osch, oschb):
    try:
        with open('obj_cache.json', 'r') as infile:
            cache = json.load(infile)
            if not otype in cache:
                cache[otype] = {}
            cache[otype][okey] = {'obj_dict':odict, 'obj_sch':osch, 'obj_schb':oschb, 'ts_created': datetime.utcnow().strftime('%c')}
        with open('obj_cache.json', 'w') as outfile:
            json.dump(cache, outfile)
    except:
        pass

def clear_obj_cache():
    cache = {}
    with open('obj_cache.json', 'w') as outfile:
        json.dump(cache, outfile)
