import datetime
import os

from pyfbook.SystemUser import SystemUser
from pyfbook.core.marketing.extract.api import post
from pyfbook.core.marketing.extract.params import prepare_report_request
from pyfbook.core.marketing.extract.start_update_date import define_start_date, define_updated_time_filter
from pyfbook.core.marketing.extract.filters import add_active_filter_to_report, add_updated_time_filter_to_report
from pyfbook.core.marketing.extract.date import since_until_to_time_ranges, since_until_to_time_range


def _launch_insights(facebook, account, params, since, until, time_increment):
    endpoint = str(account['id']) + "/insights"
    if time_increment in ["week", "month", "quarter", "year"]:
        time_ranges = str(since_until_to_time_ranges(since, until, time_increment))
        params["time_ranges"] = time_ranges
    elif time_increment == "lifetime" or time_increment == 'maximum':
        params["date_preset"] = "maximum"
    else:
        time_range = since_until_to_time_range(since, until)
        params["time_range"] = time_range
        params["time_increment"] = time_increment
    try:
        data = post(system_user=SystemUser.get(facebook=facebook, _id=account["app_system_user_id"]), endpoint=endpoint,
                    params=params)
    except ValueError:
        return None
    return {
        "report_run_id": data,
        "app_system_user_id": account["app_system_user_id"],
        "account_id": account["id"],
        "start_report": since,
        "end_report": until
    }


def launch(facebook, report, time_increment, start, end):
    r = prepare_report_request(facebook, report)
    accounts = r["accounts"]
    del r["accounts"]
    data = []
    for account in accounts:
        if start is None:
            start_account = define_start_date(facebook, report, time_increment, account)
            if start_account is None:
                if os.environ.get('DEFAULT_START_DATE'):
                    start_account = str(datetime.datetime.strptime(os.environ.get('DEFAULT_START_DATE'), '%Y-%m-%d'))[
                                    :10]
                else:
                    start_account = str(
                        datetime.datetime.strptime(str(datetime.datetime.now())[:10], '%Y-%m-%d') - datetime.timedelta(
                            days=365))[:10]
        else:
            start_account = start
        if end is None:
            end_account = str(datetime.datetime.now())[:10]
        else:
            end_account = end

        if time_increment == 'lifetime':
            updated_time_filter = define_updated_time_filter(facebook, report, time_increment, account)
            if updated_time_filter:
                # Define params to check active assets
                params_active_assets = add_active_filter_to_report(r)

                # Define params to check updated assets
                updated_time_filter = int(datetime.datetime.timestamp(updated_time_filter))
                params_updated_assets = add_updated_time_filter_to_report(r, updated_time_filter)

                for p in [params_active_assets, params_updated_assets]:
                    data.append(_launch_insights(
                        facebook=facebook,
                        account=account,
                        params=p,
                        since=start_account,
                        until=end_account,
                        time_increment=time_increment
                    ))
            else:
                data.append(_launch_insights(
                    facebook=facebook,
                    account=account,
                    params=r,
                    since=start_account,
                    until=end_account,
                    time_increment=time_increment
                ))
        else:
            data.append(_launch_insights(facebook, account, r, start_account, end_account, time_increment))
    return data
