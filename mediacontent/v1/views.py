from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authentication.customauth import CustomAuthBackend
from .serializers import CategorySerializer
from ..models import Category


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def retrieve_content_categories(request):
    content_categories = Category.objects.all()
    serializer = CategorySerializer(content_categories, many=True)
    return Response(data={'content_categories': serializer.data}, status=status.HTTP_200_OK)

