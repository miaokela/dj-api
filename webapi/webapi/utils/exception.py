from django.http import Http404
from rest_framework import exceptions, views
from rest_framework.response import Response
from rest_framework import status


class APIServerError(exceptions.APIException):
    default_detail = "服务器错误"


class APIValidationError(exceptions.ValidationError):
    default_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class APIParseError(exceptions.ParseError):
    default_detail = "解析错误"


class APIAuthenticationFailed(exceptions.AuthenticationFailed):
    default_detail = "用户认证失败"


class APINotAuthenticated(exceptions.NotAuthenticated):
    default_detail = "用户未认证"


class APIPermissionDenied(exceptions.PermissionDenied):
    default_detail = "没有操作权限"


class APINotFound(exceptions.NotFound):
    default_detail = "数据不存在"


class APIMethodNotAllowed(exceptions.MethodNotAllowed):
    default_detail = "方法不存在"


class APINotAcceptable(exceptions.NotAcceptable):
    default_detail = "不允许访问"


class APIUnsupportedMediaType(exceptions.UnsupportedMediaType):
    default_detail = "不支持的媒体数据类型"


class APIThrottled(exceptions.Throttled):
    default_detail = "请求被服务端强制撤销"


def exception_handler(exc, context):
    """
    自定义 exception_handler 错误信息返回
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, exceptions.APIException):
        if isinstance(exc.detail, (list, dict)):
            if isinstance(exc.detail, list):
                errors = exc.detail
            else:
                errors = {k: v[0] for k, v in exc.detail.items()}
        else:
            errors = exc.detail

        views.set_rollback()
        return Response(
            {"code": exc.status_code, "msg": "failed", "errors": errors, "data": {}},
            status=status.HTTP_200_OK,
        )

    return None