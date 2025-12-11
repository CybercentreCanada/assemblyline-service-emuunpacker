class UnpackError(Exception):
    """An unpacking error occured."""

    def __init__(self, description: str):
        super().__init__(self, description)
