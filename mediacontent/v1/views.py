from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async

from authentication.customauth import CustomAuthBackend
from .serializers import CategorySerializer, SectionSerializer
from ..models import Category, Section


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def retrieve_content_categories(request):
    content_categories = Category.objects.all()
    serializer = CategorySerializer(content_categories, many=True)
    return Response(data={'content_categories': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_dashboard_sections(request):
    sections = Section.objects.filter(active=True).order_by('priority')
    serializer = SectionSerializer(sections, many=True)
    return Response(data={'sections': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_customer_history(request):
    sections = Section.objects.filter(active=True)
    serializer = SectionSerializer(sections)
    return Response(data={'content_categories': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def save_playback_history(request):
    pass