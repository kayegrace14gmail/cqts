from rest_framework import serializers
from base.models import Batch, User

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('groups', 'user_permissions', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login', 'last_name', 'first_name')
