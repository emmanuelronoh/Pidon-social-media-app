from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import MyTokenObtainPairSerializer, UserSerializer, SignupSerializer
from accounts.models import User
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SignupAPIView(CreateAPIView):
    model = User
    serializer_class = SignupSerializer
    permission_classes = []
    authentication_classes = []

    def perform_create(self, serializer):
        # I overode this method because its doesn't return the instance created by
        # the serializer by default, it only calls the save method of the serializer
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Need the instance to get the tokens
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = serializer.data
        response["tokens"] = get_tokens_for_user(instance)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailAPIView(RetrieveAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        obj = get_object_or_404(self.model, id=user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class FollowingListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("id")
        user = User.objects.get(id=user_id)
        return user.following.all()


class FollowerListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("id")
        user = User.objects.get(id=user_id)
        return User.objects.filter(following__icontains='following')


class FollowUnfollowUserAPIView(APIView):

    def post(self, request, pk):
        user = self.request.user
        other_user = get_object_or_404(User, pk=pk)
        followed = False
        if user == other_user:
            return Response({
                'message': "Cannot follow yourself"
            }, status=status.HTTP_403_FORBIDDEN)
        user_following = user.following
        if user_following.filter(id=other_user.id).exists():
            user_following.remove(other_user)
        else:
            followed = True
            user_following.add(other_user)
        data = SignupSerializer(user).data
        data['followed'] = followed
        data['followers'] = user_following.count()
        return Response(data)


class ProfileUpdateAPIView(UpdateAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(self.model, id=self.request.user.id)
