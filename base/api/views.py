from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
import jwt
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .serializers import BatchSerializer
from base.models import Batch

# imports for the model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
import cv2

# secret key
secret_key = settings.SECRET_KEY

# start of model logic

model = tf.keras.models.load_model('base/api/best_model.h5')

class ClassificationResult(BaseModel):
    predicted_class: str
    predicted_probability: float

@csrf_exempt
def classify_image(request):
    if request.method == 'POST':
        # Read and preprocess the image

        image_file = request.FILES['image']
        img_array = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        IMG_SIZE = 50
        new_array = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        Xt = new_array
        Xt = np.array(Xt).reshape( IMG_SIZE, IMG_SIZE, 3)

        # Convert image to numpy array and normalize pixel values
        
        Xt = Xt/255

        # Perform inference
        prediction = model.predict(np.expand_dims(Xt, axis=0))

        # Get the predicted class
        predicted_class = np.argmax(prediction)
        predicted_probability = np.max(prediction)

        # Define a dictionary to map the class index to a human-readable label
        class_labels = {
            0: "Dark",
            1: "Green",
            2: "Light",
            3: "Medium",
            # Add more class labels as needed
        }

        # Create the ClassificationResult object for the response
        result = ClassificationResult(
            predicted_class=class_labels[predicted_class],
            predicted_probability=float(predicted_probability)
        )

        # Return the result as a JSON response
        return JsonResponse(result.dict())
    return JsonResponse({'error': 'Invalid request method.'})
#end of model logic


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
def logout_user(request):
    logout(request)
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

