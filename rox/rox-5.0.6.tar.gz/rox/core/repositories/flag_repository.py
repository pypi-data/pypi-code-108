from collections import OrderedDict


class FlagRepository:
    def __init__(self):
        self.variants = OrderedDict()
        self.flag_added_handlers = []

    def add_flag(self, variant, name):
        if not variant.name:
            variant.set_name(name)
        self.variants[name] = variant
        self.raise_flag_added_event(variant)

    def get_flag(self, name):
        return self.variants.get(name, None)

    def get_all_flags(self):
        return self.variants

    def register_flag_added_handler(self, handler):
        self.flag_added_handlers.append(handler)

    def raise_flag_added_event(self, variant):
        for handler in self.flag_added_handlers:
            handler(variant)
