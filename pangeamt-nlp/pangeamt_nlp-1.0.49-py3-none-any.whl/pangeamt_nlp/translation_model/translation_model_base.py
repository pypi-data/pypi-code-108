class TranslationModelBase:
    def __init__(self):
        pass

    def train(self):
        cls = self.__class__
        raise ValueError(f'"{cls}" should implement a "train" method')

    def load(self):
        pass
        # cls = self.__class__
        # raise ValueError(f'"{cls}" should implement a "load" method')

    def process_train(self):
        pass
        # cls = self.__class__
        # raise ValueError(f'"{cls}" should implement a "process_train" method')

    def process_src_decoding(self):
        pass
        # cls = self.__class__
        # raise ValueError(
        #    f'"{cls}" should implement a "process_src_decoding" method'
        # )

    def process_tgt_decoding(self):
        pass
        # cls = self.__class__
        # raise ValueError(
        #    f'"{cls}" should implement a "process_tgt_decoding" method'
        # )
