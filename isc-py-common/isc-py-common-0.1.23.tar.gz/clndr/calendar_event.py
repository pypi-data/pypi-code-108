import datetime
import json
import logging
import os
import uuid

from django.db.models.query import QuerySet

from isc_common import setAttr
from isc_common.common import uuid4
from list.listCalendarEvent import LinkedList

logger = logging.getLogger(__name__)


class CalendarEvent:
    backgroundColor = None
    borderColor = 'black'
    canDrag = False
    canEdit = False
    canEditLane = False
    canEditSublane = False
    canResize = False
    description = None
    duration = None
    durationUnit = "hour"
    endDate = None
    headerBackgroundColor = None
    headerBorderColor = None
    headerTextColor = None
    id = None
    isholiday = None
    isworkday = None
    isredlabelday = None
    length = None
    lane = None
    name = None
    startDate = None
    styleName = None
    sublane = None
    textColor = None

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, bool):
                setattr(self, k, 1 if v is True else 0)
            elif isinstance(v, datetime.datetime):
                if isinstance(v, datetime.datetime):
                    r = v.isoformat()
                    if v.microsecond:
                        r = r[:23] + r[26:]
                    if r.endswith('+00:00'):
                        r = r[:-6] + 'Z'
                setattr(self, k, r)
            else:
                setattr(self, k, v() if callable(v) else v)

    def __str__(self):
        setAttr(self.__dict__, "startDate", str(self.__dict__.get('startDate')))
        setAttr(self.__dict__, "endDate", str(self.__dict__.get('endDate')))
        return f'{str(self.__dict__)}'

    def print(self, comment=''):
        print('\n')
        print(f'{comment}({self.__hash__()}) {str(self)}')

    def copy(self, *args, **kwargs):
        res = CalendarEvent(**self.__dict__)
        for k, v in kwargs.items():
            setattr(res, k, v() if callable(v) else v)
        return res

    def to_json(self):
        return self.__dict__


class CalendarEventLinkedList(LinkedList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get('query'):
            query = kwargs.get('query')
            if isinstance(kwargs.get('query'), QuerySet):
                for item in query:
                    self.add(item)

    def fusion(self, fusion_list):
        if not isinstance(fusion_list, CalendarEventLinkedList):
            raise Exception(f'ce is not CalendarEventLinkedList instance')

        relax = fusion_list.first
        while relax:
            shift = self.first
            y = 0
            while shift:
                # shift.item.print('shift')
                # relax.item.print('relax')
                if shift.item.isworkday and shift.item.startDate < relax.item.startDate:
                    if shift.item.endDate > relax.item.startDate:
                        if shift.item.endDate > relax.item.endDate:
                            # self.print('self:')
                            self.replace(y, shift.item.copy(id=uuid4(), endDate=relax.item.startDate))
                            # self.print('self:')
                            self.insert(y + 1, relax.item.copy(id=uuid4(), ))
                            # self.print('self:')
                            self.insert(y + 2, shift.item.copy(id=uuid4(), startDate=relax.item.endDate))
                            # self.print('self:')
                            break
                        else:
                            raise Exception(f'Unknown case.')
                    else:
                        pass
                else:
                    pass
                shift = shift.next
                y += 1
            relax = relax.next

    def to_json(self):
        res = []

        if self.first is not None:
            current = self.first
            res.append(current.item.to_json())

            while current.next is not None:
                current = current.next
                res.append(current.item.to_json())

        return res

    def write_2_file(self, filename):
        dir, _ = os.path.split(filename)
        dir = f'{os.path.curdir}{os.sep}{dir}'
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

        outF = open(filename, "w")

        def pritnt(str):
            # logger.debug(str)
            outF.write(str)

        if self.first is not None:

            current = self.first
            pritnt('simpleSyS.tag=')
            pritnt('[')

            pritnt(f'{json.dumps(current.item.to_json())},')
            pritnt("\n")

            while current.next is not None:
                current = current.next
                pritnt(f'{json.dumps(current.item.to_json())},')
                pritnt("\n")
            pritnt(']')

        outF.close()
        print('Запись выполнена.')
