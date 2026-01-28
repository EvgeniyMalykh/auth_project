from rest_framework import status, views
from rest_framework.response import Response

from .permissions import IsAuthenticatedCustom, RbacPermission


class ProductsMockView(views.APIView):
    permission_classes = [IsAuthenticatedCustom, RbacPermission]
    element_code = "products"

    def get(self, request):
        data = [
            {"id": 1, "name": "Laptop", "price": 1000},
            {"id": 2, "name": "Phone", "price": 500},
        ]
        return Response(data)


class OrdersMockView(views.APIView):
    permission_classes = [IsAuthenticatedCustom, RbacPermission]
    element_code = "orders"

    def get(self, request):
        data = [
            {"id": 1, "user_id": str(request.user.id), "amount": 100},
            {"id": 2, "user_id": "00000000-0000-0000-0000-000000000000", "amount": 200},
        ]
        return Response(data)

    def post(self, request):
        new_order = {
            "id": 999,
            "user_id": str(request.user.id),
            "amount": request.data.get("amount", 0),
        }
        return Response(new_order, status=status.HTTP_201_CREATED)
