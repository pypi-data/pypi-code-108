from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
import csv
import os


class QuickICS:

    reminder_text = '**Reminder** Single line in csv:\n\n02/06/2022,16:00:00,1:30,\
Anchor\n\n'

    def __init__(self):
        self.in_file = input(f'{QuickICS.reminder_text}Enter CSV file -> ')
        self.name = input('Enter Event Name -> ')
        self.ical = []
        self.events = []
        self.today = datetime.now()
        self.today = datetime.strftime(self.today, '%d_%b_%y')
        self.path = os.path.expanduser("~/Desktop")
        self.FNAME = f"Import_{self.today}"
        self.in_file = os.path.abspath(os.path.join(self.path, self.in_file))
        self.save_as = os.path.abspath(os.path.join(self.path, self.FNAME))
        self.base = os.path.dirname(__file__)
        self.save_as = os.path.abspath(os.path.join(self.base, self.FNAME))
        self.outfile = f"{self.save_as}.ics"
        self.loadCSV()
        self.calendarCreate()

    def parseDuration(self, time):
        self.time = time.split(":")
        self.h = self.time[0]
        self.m = self.time[1]
        self.duration = timedelta(hours=int(self.h), minutes=int(self.m))
        return self.duration

    def loadCSV(self):
        with open(self.in_file, newline='') as f:
            r = csv.reader(f)
            for i in r:
                if i != []:
                    self.date_time = f'{i[0]} {i[1]}'
                    self.dtstamp = datetime.strptime(self.date_time, '%m/%d/%Y %H:%M:%S')  # noqa: E501
                    self.duration = self.parseDuration(i[2])
                    self.location = vText(i[3])
                    self.ical.append((self.name, self.dtstamp, self.duration, self.location))  # noqa: E501

    def calendarCreate(self):
        for x, i in enumerate(self.ical):
            self.event = Event()
            self.event.add("summary", i[0])
            self.event.add("dtstamp", i[1])
            self.event.add("dtstart", i[1])
            self.event.add("dtend", i[1] + i[2])
            self.event.add("location", i[3])
            self.events.append(self.event)
        cal = Calendar()
        cal.add('prodid', '-//Michael H. Roberts//WMT TO ICS//')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        for evnt in self.events:
            cal.add_component(evnt)
        with open(self.outfile, 'wb') as f:
            f.write(cal.to_ical())


if __name__ == '__main__':
    QuickICS()
