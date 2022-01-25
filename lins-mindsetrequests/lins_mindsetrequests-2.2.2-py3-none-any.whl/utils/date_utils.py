from pytz import timezone


def make_aware(date):
    return date.replace(tzinfo=timezone('America/Sao_Paulo'))
