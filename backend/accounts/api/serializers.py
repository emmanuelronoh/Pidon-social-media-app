from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from post.api.serializers import CreatorSerializer, PostSerializer
from accounts.models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_name'] = user.username
        try:
            token["profile_pic"] = user.profile_pic.url
        except:
            token["profile_pic"] = ""

        return token


class UserSerializer(serializers.ModelSerializer):
    followers = CreatorSerializer(many=True)
    posts = PostSerializer(many=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'date_joined',
            'email',
            'profile_pic',
            'followers',
            'posts',
        ]
