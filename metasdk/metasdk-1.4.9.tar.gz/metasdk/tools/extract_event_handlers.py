import json
import runpy
import os
import argparse
from metasdk.__state import get_current_app


def main():
    """
    Запускает указанный МЕТА скрипт и извлекает из него конструкции @META.event_bus.listener,
    которые используются для объявления функции как обработчика конкретных типов событий
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_name', help='Full absolute filepath', type=str, required=True)
    args = parser.parse_args()

    build_event_list(args.path_name)


def build_event_list(path_name):
    os.environ['GARPUN_CLOUD_GENERATE'] = 'y'
    runpy.run_path(path_name=path_name)

    META = get_current_app()  # type: META: MetaApp

    res = []
    for listener in META.event_bus.get_listeners():
        res.append(listener.listen.__dict__)

    print('%START_GARPUN_CLOUD_GENERATE%\n' + json.dumps(res) + '\n%END_GARPUN_CLOUD_GENERATE%')


if __name__ == '__main__':
    main()
