from starlette.responses import JSONResponse

from api.utils.utils import now


def error_response(message, status_code) -> JSONResponse:
    """
    The function will create https error response
    :param message:
    :param status_code:
    :return: JSONResponse
    """
    data = {
        'status': 'ERROR',
        'code': status_code,
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S.%f%Z"),
        'error_message': message
    }
    return JSONResponse(data, status_code=status_code)


def ok_response(message: str, status_code: int = 200, cookies: dict = None, **additional_data) -> JSONResponse:
    """
    The function will create https ok response
    :param message:
    :param status_code:
    :param cookies:
    :param additional_data:
    :return: JSONResponse
    """
    if not cookies:
        cookies = {}
    data = {
        'status': 'OK',
        'code': status_code,
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S.%f%Z"),
        'message': message,
    }
    for k, v in additional_data.items():
        data['{0}'.format(k)] = v
    res = JSONResponse(data, status_code=status_code)
    for k, v in cookies.items():
        res.set_cookie(key=k, value=v)
    return res
