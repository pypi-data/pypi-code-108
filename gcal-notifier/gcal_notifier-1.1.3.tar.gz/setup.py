# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gcal_notifier']

package_data = \
{'': ['*'], 'gcal_notifier': ['resources/*']}

install_requires = \
['gcsa>=1.2.0,<2.0.0', 'simpleaudio>=1.0.4,<2.0.0']

entry_points = \
{'console_scripts': ['gcal_notifier = gcal_notifier.main:gcal_notifier']}

setup_kwargs = {
    'name': 'gcal-notifier',
    'version': '1.1.3',
    'description': 'A simple and lightweight GoogleCalendar notifier for Linux',
    'long_description': "# SimpleGCalendarNotifier\n\n### A simple and lightweight GoogleCalendar notifier for Linux\n\nThis app is focused on giving versatility and simplicity, and present a\nvery lightweight command-line application that reminds you of your events\nin Google Calendar.\n\nThe project was inspired by [gcalcli](https://github.com/insanum/gcalcli),\nand looking for more bare-bones features and that could handle multiple\nGoogle accounts and calendars.\n\nInstallation\n------------\n\nFor now, this package is only available through [PyPi](https://pypi.org/)\n\n### Install from PyPi\n```sh\npip install gcal_notifier\n```\n\nFeatures\n--------\n\n- Fetch Google events from all accounts\n- Notify events\n- Uses Cron jobs to keep everything as minimal as possible\n\nUsage\n-----\n\n```sh\ngcal_notifier --help\nusage: gcal_notifier [-h] {get,notify,print} ...\n\nA simple and lightweight GoogleCalendar notifier for Linux.\n\npositional arguments:\n  {get,notify,print}  Invoking a subcommand with --help prints subcommand usage.\n    get               fetch events from Google Calendar and save them in cache.\n    notify            run reminders with cached events.\n    print             print events to the console.\n\noptions:\n  -h, --help          show this help message and exit\n```\n\n### Credentials\n\nFor all of this to work, you have to create your credentials for each account\nyou want to use.\nNote: this section was copied and pasted from the [gcsa](https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html) README.\n\n1. Create a new [Google Cloud Platform (GCP) project](https://developers.google.com/workspace/guides/create-project)\n\n2. Configure the [OAuth consent screen](https://developers.google.com/workspace/guides/create-credentials#configure_the_oauth_consent_screen)\n\n3. [Create a OAuth client ID credential](https://developers.google.com/workspace/guides/create-credentials#create_a_oauth_client_id_credential)\nand download the `credentials.json` file\n\n4. Put downloaded `credentials.json` file into `~/.config/gcal_notifier/default`\n\nSee more options in [Authentication](https://google-calendar-simple-api.readthedocs.io/en/latest/authentication.html#authentication).\n\nNote:\n\nOn the first run, your application will prompt you to the default browser to get permissions from you to use your calendar.\nThis will create token.pickle file in the same folder.\n\nSetting Up\n----------\n\nAfter having your `credentials.json` file(s), you can run `gcal_notifier get`\nto see if everything works properly.\n\nIf it does, it's time to set up your cron jobs.\n\n1. Run `crontab -e` to edit your cron jobs.\n\n2. Choose the intervals that you want to run `get` and `remind`. This means\nthat you can fetch events in a different interval that you check for reminders.\nMy personal preference, for example, is:\n```sh\n*/10 * * * *  gcal_notifier get\n* * * * *  gcal_notifier remind\n```\nSo it runs every 10 minutes to fetch events, but looks for reminders every minute.\n\nThat's it! You're all set up!\n\nConfiguration\n-------------\n\nYou can configure some things for now (and hopefully more later), and all the\nconfigurations are done in a file that sits in `~/.config/gcal_notifier/config.ini`\n\nA sample of every configuration supported is:\n```ini\n[GENERAL]\n# Returns only one event for recurrent events. Default is true\nsingle_events = true\n# How to order the events. Default (and recommended) is startTime\norder_by = startTime\n# Custom notification sound, if you would like to choose (it has to be a wav file).\nnotification_sound = ~/Music/my_notification.wav\n\n[CALENDAR1]\n# Name given to the calendar. Default is 'Calendar'\nname = NAME1\n# Name or ID of the calendar. Required.\ncalendar = example@gmail.com\n# Reminders to your events, up to 5 integers separated by commas. Default is None\ndefault_reminders = 10,0\n# Path to the credentials file. Default is ~/.config/gcal_notifier/credentials.json\n# credentials = ~/.config/gcal_notifier/credentials_file.json\n\n[CALENDAR2]\nname = NAME2\ncalendar = xxxxxxxxxxxxxxxxxxxxxxxx@group.calendar.google.com\ndefault_reminders = 10,0\ncredentials = ~/.config/gcal_notifier/credentials_other_account.json\n\n[CALENDAR3]\nname = NAME3\ncalendar = other@gmail.com\n.\n.\n.\n```\n\n## Help wanted!\n\nIf you find this project useful, please feel free to contribute or report an issue.\nYou can always email me as thalesaknunes22@gmail.com\n\n### Happy Coding!\n",
    'author': 'Thales Nunes',
    'author_email': 'thalesaknunes22@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thalesnunes/gcal_notifier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
