class DefaultException(Exception):
    context: dict

    def __init__(self, message: str, context: dict):
        super()
        self.args = message,
        self.context = context
