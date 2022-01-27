class MergedContext:
    def __init__(self, global_context, local_context):
        self.global_context = global_context
        self.local_context = local_context

    def get(self, key):
        if self.local_context is not None and self.local_context.get(key) is not None:
            return self.local_context.get(key)

        if self.global_context is not None:
            return self.global_context.get(key)

        return None

    def __getitem__(self, key):
        return self.get(key)
