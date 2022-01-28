def prepare_report_request(facebook, report):
    result = dict()
    result["level"] = report["level"]
    fields = report["fields"].copy()
    if report.get("filtering"):
        result["filtering"] = report.get("filtering")
    if report.get("action_attribution_windows"):
        result["action_attribution_windows"] = report.get("action_attribution_windows")
    if report.get("action_report_time"):
        result["action_report_time"] = report.get("action_report_time")
    if 'account_id' not in fields:
        fields.append('account_id')
    if "purchase" in fields:
        fields[fields.index("purchase")] = "actions"
    elif "total_actions" in fields:
        fields[fields.index("total_actions")] = "actions"
    if "video_view_10_sec" in fields:
        fields[fields.index("video_view_10_sec")] = "video_10_sec_watched_actions"
    if "updated_time" not in fields:
        fields.append("updated_time")
    fields = ", ".join(fields)
    result["fields"] = fields
    if report.get("breakdowns"):
        breakdowns = [b for b in report["breakdowns"]]
        breakdowns = ", ".join(breakdowns)
    else:
        breakdowns = None
    result["breakdowns"] = breakdowns
    if report.get('ad_accounts'):
        accounts = report.get('ad_accounts')
        query = "SELECT DISTINCT id, app_system_user_id, account_id FROM %s.ad_accounts WHERE id in ('%s')"
        query = query % (facebook.schema_name if facebook.schema_name else facebook.config["schema_name"], "','".join(accounts))
    else:
        query = "SELECT DISTINCT id, app_system_user_id, account_id FROM %s.ad_accounts WHERE active = True"
        query = query % facebook.schema_name if facebook.schema_name else facebook.config["schema_name"]
    accounts = facebook.dbstream.execute_query(query=query)
    result["accounts"] = accounts
    return result
