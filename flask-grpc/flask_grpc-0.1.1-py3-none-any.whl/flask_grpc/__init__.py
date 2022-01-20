import grpc


class ChannelWrapper:
    def __init__(
        self, app=None, target=None, secure=None, credentials=None, prefix="GRPC"
    ):
        self.app = app
        self.target = target
        self.secure = secure
        self.prefix = prefix
        self.credentials = credentials
        self._channel = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not self.target:
            self.target = app.config[f"{self.prefix}_TARGET"]
        if self.secure is None:
            self.secure = app.config.get(f"{self.prefix}_SECURE", False)

        if self.secure:
            if not self.credentials:
                self.credentials = app.config.get("f{self.prefix}_CREDENTIALS")
            if not self.credentials:
                self.credentials = grpc.ssl_channel_credentials()

        # app.teardown_appcontext(self.teardown)

    # def teardown(self, exception):
    #     ctx = _app_ctx_stack.top
    #     if hasattr(ctx, "grpc_channel"):
    #         ctx.grpc_channel.close()

    def _new_channel(self):
        if self.secure:
            return grpc.secure_channel(self.target, credentials=self.credentials)
        return grpc.insecure_channel(self.target)

    @property
    def channel(self):
        if self._channel:
            return self._channel
        self._channel = self._new_channel()
        return self._channel


class StubWrapper:
    def __init__(self, stub_cls, channel_wrapper) -> None:
        self.stub_cls = stub_cls
        self.channel_wrapper = channel_wrapper

    def __getattr__(self, name):
        stub = self.stub_cls(self.channel_wrapper.channel)
        return getattr(stub, name)
