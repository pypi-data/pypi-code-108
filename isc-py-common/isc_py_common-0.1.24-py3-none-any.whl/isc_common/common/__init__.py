import os
from typing import Text
from uuid import UUID


def getOrElse(default, value):
    if value:
        return value
    else:
        return default


black = "black"
blue = "blue"
closed = "closed"
create = "create"
deleted = "deleted"
developers = "developers"
doing = "doing"
execution = "execution"
FILES_STORE_UNKNOWN_TYPE = "FILES_STORE неизвестного типа"
formirovanie = "formirovanie"
gray = "#808080"
green = "green"
handmade = "handmade"
in_production = "in_production"
launched = "launched"
light_green = "#99CC00"
made = "made"
new = "new"
new_man = "new_man"
not_relevant = "not_relevant"
notDefined = "Не определен"
orange = "orange"
otkryt = "otkryt"
otmenen = "otmenen"
red = "red"
tournaments_offset = 10000000
DELETE_ONE_STAGE = 'DELETE_ONE_STAGE'
delete_image_refs = 'delete_image_refs'
restarted = "restarted"
route_made = "route_made"
route_made_error = "route_made_error"
SFTP = "SFTP"
shirts = "shirts"
sht = "шт"
started = "started"
started_another = "started_another"
stoped = "stoped"
transferred = "transferred"
undefined = "undefined"
unknown = "unknown"
unknown_name = 'Не задан'
update = "update"
value_odd = "value_odd"
zakryt = "zakryt"
ONE_STAGE_ADDING = 'ONE_STAGE_ADDING'

name_closed = "Закрыт"
name_doing = "Выполнен"
name_formirovanie = "Формирование"
name_handmade = "Системный (ручное формирование)"
name_new = "Новый"
name_new_h = "Новый (р)"
name_new_s = "Новый (с)"
name_restarted = "Запущен (повторно)"
name_started = "Запущен"
name_started_another = "Запущен (раннее)"
name_stoped = "Остановлен"
name_transferred = "Назначенный"
name_unknown = "Неопределеный"


def blinkString(text, blink=True, color="black", bold=False) -> Text:
    if blink:
        res = f'<div class="blink"><font color="{color}"</font>{text}</div>'
    else:
        res = f'<div><font color="{color}"</font>{text}</div>'

    if bold is True:
        return f'<b>{res}</b>'
    else:
        return res


def blinkString1(text, blink=True, color="black", bold=True) -> Text:
    if blink:
        res = f'<blink class="blink"><font color="{color}"</font>{text}</blink>'
    else:
        res = f'<blink><font color="{color}"</font>{text}</blink>'

    if bold is True:
        return f'<b>{res}</b>'
    else:
        return res


def to_H(text, level=4):
    return f'<h{level}>{text}</h{level}>'


def uuid5():
    return UUID(bytes=os.urandom(16), version=4)


def uuid4():
    return str(UUID(bytes=os.urandom(16), version=4)).upper().replace('-', '_')
