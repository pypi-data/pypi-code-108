import json


def add_active_filter_to_report(r):
    result = r.copy()
    result["filtering"] = r["filtering"] if r.get("filtering") else []

    if result["level"] == "ad":
        new_filter = {'field': 'ad.effective_status', 'operator': 'IN', 'value': ['ACTIVE']}
    elif result["level"] == "adset":
        new_filter = {'field': 'adset.effective_status', 'operator': 'IN', 'value': ['ACTIVE']}
    elif result["level"] == "campaign":
        new_filter = {'field': 'campaign.effective_status', 'operator': 'IN', 'value': ['ACTIVE']}
    elif result["level"] == "account":
        new_filter = ""
    else:
        new_filter = ""
    result["filtering"].append(new_filter)
    result["filtering"] = json.dumps(result["filtering"])
    return result


def add_updated_time_filter_to_report(r, updated_time_filter):
    result = r.copy()
    result["filtering"] = r["filtering"] if r.get("filtering") else []
    if result["level"] == "ad":
        new_filter = {'field': 'ad.updated_time', 'operator': 'AFTER', 'value': updated_time_filter}
    elif result["level"] == "adset":
        new_filter = {'field': 'adset.updated_time', 'operator': 'AFTER', 'value': updated_time_filter}
    elif result["level"] == "campaign":
        new_filter = {'field': 'campaign.updated_time', 'operator': 'AFTER', 'value': updated_time_filter}
    elif result["level"] == "account":
        new_filter = ""
    else:
        new_filter = ""
    result["filtering"].append(new_filter)
    result["filtering"] = json.dumps(result["filtering"])
    return result
