from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import CustomUserSerializer, LoginSerializer


class AuthViewSet(viewsets.ModelViewSet):  # Added ModelViewSet
    queryset = CustomUser.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        return CustomUserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']  # Use the user from serializer validation
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })

    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user exists (this is already handled in serializer, but keeping for safety)
        if CustomUser.objects.filter(email=serializer.validated_data['email']).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'patch'])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        
        return Response({
            'user_id': updated_user.id,
            'username': updated_user.username,
            'email': updated_user.email
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
            return Response({'message': 'Logged out successfully'})
        return Response({'error': 'No active session found'}, status=status.HTTP_400_BAD_REQUEST)