from typing import TypedDict

DefaultErrorContext = TypedDict(
    "DefaultErrorContext",
    {
        "status": int,
        "url": str,
        "req_body": dict | None,
        "res_body": dict
    }
)

class IDefaultException(Exception):
    def __init__(self, message: str, context: DefaultErrorContext):
        super()
        self.args = message,
        self.context = context
