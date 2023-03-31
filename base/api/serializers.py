from rest_framework.serializers import ModelSerializer
from base.models import Room
from django.contrib.auth.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class RoomSerializer(ModelSerializer):
    host = UserSerializer(many=False, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Room
        fields = '__all__'

