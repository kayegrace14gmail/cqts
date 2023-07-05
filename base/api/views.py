
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
import jwt
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .serializers import BatchSerializer
from base.models import Batch, User

# imports for the model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
import cv2

# UUID import
import uuid

# secret key
secret_key = settings.SECRET_KEY

# start of model logic
model_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_model.h5')
model = tf.keras.models.load_model(model_file)

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
        Xt = np.array(Xt).reshape(IMG_SIZE, IMG_SIZE, 3)

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
# end of model logic


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
            group = user.group.name
            if(group == 'Cooperative' or group == 'Exporter' or group == 'Buyer'):
                login(request, user)
                return Response({'message': 'Login successful.', 'group': group}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Not allowed here'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def logout_user(request):
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def register_batch(request):
    serializer = BatchSerializer(data=request.data)
    if serializer.is_valid():
        cooperative = User.objects.get(id=request.data.get('cooperative'))
        serializer.validated_data['cooperative'] = cooperative
        image_file = request.FILES['image']
        img_array = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        IMG_SIZE = 50
        new_array = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

        Xt = new_array
        Xt = np.array(Xt).reshape(IMG_SIZE, IMG_SIZE, 3)

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
        predicted_class = class_labels[predicted_class]
        predicted_probability = float(predicted_probability)

        if predicted_class != 'dark':
            serializer.validated_data['is_approved'] = True
            serializer.validated_data['batch_string'] = str(uuid.uuid4())

        serializer.validated_data['color'] = predicted_class
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
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
