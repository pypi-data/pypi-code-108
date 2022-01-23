import time
import fire
from . import tail, sender


def agal(*args, uri='', key=''):
    if uri:
        msg_sender = sender.Sender(uri, key=key)
        async def line_handler(line, **kwargs):
            await msg_sender.send({
                'payload': line,
                'meta': {
                    'timestamp': int(time.time())
                }
            })
    else:
        line_handler = None
    tail.start(args, handler=line_handler)


def main():
    fire.Fire(agal)


if __name__ == '__main__':
    main()
