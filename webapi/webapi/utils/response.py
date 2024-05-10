from rest_framework.response import Response


class APIResponse(Response):
    def __init__(
        self,
        code=200,
        msg="success",
        data=None,
        status=None,
        headers=None,
        errors=None,
        **kwargs
    ):
        errors = {k: v[0] for k, v in errors.items()} if errors else {}

        dic = {"code": code, "msg": msg, "errors": errors, "data": {}}
        if data:
            dic = {
                "code": code,
                "msg": msg,
                "data": data,
            }
        dic.update(kwargs)
        super().__init__(data=dic, status=status, headers=headers)
