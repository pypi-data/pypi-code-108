from rest_framework import serializers
from .models import MyUser

class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ['url', 'username', 'email', 'is_staff']