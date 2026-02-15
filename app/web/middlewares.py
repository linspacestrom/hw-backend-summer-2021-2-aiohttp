import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPException, HTTPInternalServerError
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        code = getattr(e, "status", None) or getattr(e, "status_code", 500)
        try:
            payload = json.loads(e.text) if e.text else {}
        except Exception:
            payload = {}
        if code in HTTP_ERROR_CODES:
            return error_json_response(
                http_status=e.status,
                status=HTTP_ERROR_CODES[code],
                message=e.reason,
                data=payload,
            )

        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=e.reason,
            data={},
        )

    except Exception:
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=HTTPInternalServerError.reason,
            data={},
        )

    return response


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
