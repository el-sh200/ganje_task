from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from utils.permissions import IsAnonymous
from .serializers import UserRegistrationSerializer, CustomTokenObtainSerializer


@extend_schema(tags=['account'])
class CustomTokenObtainPair(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer


@extend_schema(tags=['account'])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['account'])
class UserRegistration(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (IsAnonymous,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({
                'message': 'User created successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                },
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
