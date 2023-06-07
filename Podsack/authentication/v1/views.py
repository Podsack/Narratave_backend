from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer
from rest_framework.response import Response
import rest_framework.status as status
from django.contrib.auth import authenticate
from ..utils import AuthUtils


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()
        except Exception as exc:
            return Response({'success': False, 'message': exc}, status=status.HTTP_400_BAD_REQUEST)

        token = AuthUtils.generate_token(request=request, user=user)
        return Response({'success': True, 'message': 'Sign-up successful', 'user': serializer.data, 'token': token}, status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = request.user

    if user and user.is_active:
        serializer = UserSerializer(user)
        tokens_map = AuthUtils.generate_token(request=request, user=user)
        return Response({'success': True, 'user': serializer.data, 'tokens': tokens_map})

    return Response(data={'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response({'user': {}})