from rest_framework.views import APIView

from webapi.utils.pagination import RestPagination
from webapi.utils.response import APIResponse
from webapi.utils.rewrite import ListAPIView
from webapi.utils.helper import DBHelper

from .models import Product
from .serializers import ProductSerializer


class TestListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = RestPagination


class TestDetailView(APIView):

    def get(self, request, pk):
        products = DBHelper.select_one(
            'sales.index.query_products',
            params={
                'product_id': pk
            },
            return_obj=False
        )

        return APIResponse(data=products)
