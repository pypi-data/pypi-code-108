import asyncio
import time

import related

from gosdk import construct_sdk


@related.mutable()
class State(object):
    debug = related.BooleanField(default=False)
    quiet = related.BooleanField(default=False)
    hard_failure = related.BooleanField(default=True)
    start_time = related.IntegerField(required=False)
    end_time = related.IntegerField(required=False)
    glob = related.SequenceField(str, required=False, repr=True)
    include_tar = related.BooleanField(default=False)

    batch_size = related.IntegerField(default=50)

    loop = related.ChildField(object, required=False, repr=False)
    run_id = related.StringField(required=False)
    pipeline = related.StringField(required=False)
    build = related.StringField(required=False)
    sdk_refs = related.SequenceField(object, default=[])
    failures = related.SequenceField(object, default=[])
    token = related.StringField(required=False)
    host = related.StringField(required=False)
    schemes = related.SequenceField(str, required=False)
    max_time = related.IntegerField(required=False)

    def set_start(self):
        self.start_time = time.time()

    def set_end(self):
        self.end_time = time.time()

    def create_sdk(self, async_enabled=False, loop=None, timeout=300):
        sdk = construct_sdk(
            async_enabled=async_enabled,
            loop=loop or self.loop,
            token=self.token,
            host=self.host,
            schemes=self.schemes,
            timeout=timeout,
            custom_header_option=self.custom_header_option,

        )
        if async_enabled:
            self.sdk_refs.append(sdk)
        return sdk

    def add_failure(self, failure):
        self.failures.append(failure)

    def finalize(self):
        pending = []

        for sdk_ref in self.sdk_refs:
            pending.append(sdk_ref.close())

        if pending:
            self.loop.run_until_complete(asyncio.wait(pending))
