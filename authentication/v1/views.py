from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
import rest_framework.status as status
from ..customauth import CustomAuthBackend
from ..utils import AuthUtils

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()
        except Exception as exc:
            return Response({'success': False, 'message': exc}, status=status.HTTP_400_BAD_REQUEST)

        token = AuthUtils.generate_token(request=request, user=user)
        return Response({'success': True, 'message': 'Sign-up successful', 'user': serializer.data, 'token': token},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    email = request.data.get('email')
    if email is None:
        return Response(data={'success': False, 'message': 'Invalid credentials'})

    user = User.objects.filter(email=email).first()

    if user.check_password(raw_password=request.data.get('password')) and user.is_active:
        serializer = UserSerializer(user)
        tokens_map = AuthUtils.generate_token(request=request, user=user)
        return Response({'success': True, 'user': serializer.data, 'tokens': tokens_map})

    return Response(data={'success': False, 'message': 'Invalid login credentials'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_user(request):
    user = UserSerializer(request.user)
    return Response({'user': user.data})
