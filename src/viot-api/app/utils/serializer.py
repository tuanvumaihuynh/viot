import msgspec
from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """

    def render(self, content: any) -> bytes:
        return msgspec.json.encode(content)
