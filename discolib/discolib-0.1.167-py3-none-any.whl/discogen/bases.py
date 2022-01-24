from discolib.discogen.config import Config

class LangGenerator:

    def __init__(self, cfg: Config):
        self.config = cfg
        self.attributes = cfg.attrs

    def write_attributes(self):
        ...