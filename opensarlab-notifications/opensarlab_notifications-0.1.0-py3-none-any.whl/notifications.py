import os
from datetime import datetime
import re

import yaml
from ics import Calendar
import requests
import html2text

def notes(profile_arg, ical_arg):

    try:
        cal = Calendar(requests.get(ical_arg).text)
        active_events = []
        
        for event in list(cal.events):
            begin_time = event.begin.to('utc').datetime.replace(tzinfo=None)
            now_time = datetime.utcnow().replace(tzinfo=None)
            end_time = event.end.to('utc').datetime.replace(tzinfo=None)

            if begin_time <= now_time <= end_time:
                compiled = re.compile("<meta>(.*)<message>(.*)$", re.DOTALL)
                descr_to_html = html2text.html2text(event.description)

                groups = compiled.search(descr_to_html)
                
                try:
                    meta = yaml.safe_load(groups.group(1))
                    message = groups.group(2)

                    profile = [ prof.strip() for prof in meta['profile'].split(',') ]

                    if 'mute' not in meta:
                        if type(profile) is not list:
                            profile = [profile]

                        if profile_arg in profile:
                            active_events.append(
                                {
                                    "title": event.name,
                                    "message": message.strip(),
                                    "type": meta['type'].strip()
                                }
                            )
                except Exception as e:
                    print(e)
                    message = """
There must be a description of format:
<meta>
    profile: SAR 1,Other_profile_names
    type: info
<message>
    Your message in HTML.""" 
                    raise Exception(message)

        print(f"Active events to popup: {active_events}")
        return active_events

    except Exception as e:
        print(e)
        raise Exception(f"{e}")

def main(profile: str='default', ical: str=None):
    if ical is None:
        ical = os.environ.get('ICAL_URL', None)
    if ical is None:
        raise Exception("iCal URL not found.")

    return notes(profile, ical)