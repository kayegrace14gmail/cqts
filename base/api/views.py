from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
import jwt
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# from rest_framework.authtoken.models import Token
from django.conf import settings
from .serializers import BatchSerializer
from base.models import Batch

secret_key = settings.SECRET_KEY


@api_view(['GET', 'PUT', 'POST'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/cooperatives',
        'GET /api/exporters',
        'GET /api/buyers'
    ]

    return Response(routes)

@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, email=email, password=password)
    
    if user is not None:
        login(request, user)
        # Generate and return authentication token (e.g., JWT)
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time
        }, secret_key, algorithm='HS256')
        return Response({'token': token})
    else:
        return Response({'error': 'Invalid credentials'}, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    django_request = request._request
    logout(django_request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_batch(request):
    serializer = BatchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_batch(request, batch_id):
    try:
        batch = Batch.objects.get(id=batch_id)
    except Batch.DoesNotExist:
        return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BatchSerializer(batch, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

