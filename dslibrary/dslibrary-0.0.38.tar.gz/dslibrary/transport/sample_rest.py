"""
A simple REST endpoint that just delegates to a local mmlibrary.  Demonstrates the server side of MMLibrary
endpoints.

(JUST GETTING STARTED WITH THIS)
"""
import json
import signal
import tornado.ioloop
import tornado.web
from .to_local import DSLibraryLocal


def detect_interrupt():
    request_close = []

    def signal_handler(signum, frame):
        request_close.append(1)

    def check_exit():
        if request_close:
            tornado.ioloop.IOLoop.instance().stop()

    signal.signal(signal.SIGINT, signal_handler)
    tornado.ioloop.PeriodicCallback(check_exit, 0.25*1000).start()


def create_app(target_folder: str):
    target = DSLibraryLocal(target_folder)

    class Context(tornado.web.RequestHandler):
        def get(self):
            ctx = {
                "uri": target.get_uri(),
                "parameters": target.get_parameters()
            }
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(ctx))

    class Resources(tornado.web.RequestHandler):
        def get(self):
            path = self.request.path.split("/resources/", maxsplit=1)[1]
            byte_range = json.loads(self.get_argument("byte_range"))
            with target.open_resource(path, mode='rb') as f_r:
                f_r.seek(byte_range[0])
                content = f_r.read(byte_range[1] - byte_range[0])
            self.set_header("Content-Type", "application/octet-stream")
            self.write(content)

        def put(self):
            path = self.request.path.split("/resources/", maxsplit=1)[1]
            append = self.get_argument("append") in ("true", 1, "True")
            hint = self.get_argument("hint")
            # TODO implement hints?  (for multi-part upload)
            with target.open_resource(path, mode='ab' if append else 'wb') as f_w:
                f_w.write(self.request.body)

    '''
    class AnotherOne(tornado.web.RequestHandler):
        async def get(self):
            try:
                value = json.loads(self.get_argument("request"))
            except ValueError:
                raise tornado.web.HTTPError(400, "Expected 'request' argument with JSON data")
            out = await ...
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({}))

        async def post(self):
            value = json.loads(self.request.body)
            out = await ba.request_one(self.request.path, value)
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({}))
    '''

    app = tornado.web.Application([
        (r"/context", Context),
        (r"/resources/.*", Resources),
    ])
    return app


def main():
    port = 6324
    app = create_app(".")
    app.listen(port)
    # tornado.ioloop.PeriodicCallback(ba.metrics.dump, settings.metrics_interval*1000).start()
    # tornado.ioloop.IOLoop.current().spawn_callback(ba.collect_batches)
    detect_interrupt()
    print(f"MMLibrary Endpoint running on port {port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
    exit(0)

