import pandas as pd
import numpy as np
from pyfbook.core.marketing.extract.api import get


def _clean(all_ids, table_name, facebook):
    query = "DELETE FROM %s WHERE id in ('%s')" % (table_name, "','".join(all_ids))
    try:
        facebook.dbstream.execute_query(query=query)
    except Exception:
        pass


def process_ad_accounts(ad_accounts, table_name, facebook, list_account_ids=None):
    if not ad_accounts:
        return 0
    dict_ad_accounts = pd.json_normalize(ad_accounts, sep='__').replace({np.nan: None}).to_dict(
        orient='records')
    columns = []
    all_ids = []
    unique_ad_accounts = []
    for r in dict_ad_accounts:
        if r["id"] in all_ids:
            continue
        elif list_account_ids and r["id"] not in list_account_ids:
            continue
        all_ids.append(r["id"])
        r["active"] = True
        unique_ad_accounts.append(r)
        for k in r.keys():
            if k not in columns:
                columns.append(k)
    data = {
        "table_name": table_name,
        "columns_name": columns,
        "rows": [[i.get(c) for c in columns] for i in unique_ad_accounts]
    }

    _clean(all_ids, table_name, facebook=facebook)
    facebook.dbstream.send_data(data=data, replace=False)


def get_ad_accounts(system_user):
    params = {
        "fields": "name,account_id,currency,partner"
    }
    result = get(system_user, "me/adaccounts", params)
    for r in result:
        r["app_system_user_id"] = system_user.id
    return result
