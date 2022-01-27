class ComplexFrameElementError(ValueError):
    def __init__(
            self,
            jumped_rows: int,
    ):
        self.jumped_rows: int = jumped_rows
        super().__init__()
