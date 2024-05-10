import logging

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from webapi.utils.pagination import RestPagination
from webapi.utils.response import APIResponse
from webapi.utils.rewrite import CreateAPIView, ListAPIView
from webapi.utils.helper import DBHelper
from .models import Product
from .serializers import ProductSerializer, UserRegistrationSerializer


logger = logging.getLogger('core')

class TestListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = RestPagination
    permission_classes = [IsAuthenticated]


class TestDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        products = DBHelper.select_one(
            'sales.index.query_products',
            params={
                'product_id': pk
            },
            return_obj=False
        )
        # raise Exception('error')
        # logger.error("raise error")

        return APIResponse(data=products)


class RegisterView(CreateAPIView):
    """
    用户注册
    """

    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return APIResponse(data={
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
