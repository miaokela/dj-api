from rest_framework.pagination import PageNumberPagination
from ..utils.response import APIResponse
from collections import OrderedDict


class RestPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return APIResponse(
            code=200,
            data=OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            ),
        )