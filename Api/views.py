#  from django.shortcuts import render

from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response

from . import serializer
from . import models
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.


# create: new user
# list/retrieve: user profile
# update: user profile (include set password)
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all().order_by('user_id')
    serializer_class = serializer.UserProfileSerializer
    filterset_fields = ('user_tel', 'user_id')

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            # get
            return serializer.UserProfileSerializer
        else:
            # post/patch
            return serializer.UserUpdateSerializer

    # create a new user(register)
    def create(self, request, *args, **kwargs):
        user = self.queryset.filter(user_tel=request.data["user_tel"])
        print(user)
        if user.exists():
            return Response({'This telephone has been registered'}, status=status.HTTP_302_FOUND)
        else:
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list: all job type detail
class JobtypeDetailViewSet(viewsets.ModelViewSet):
    queryset = models.JobtypeDetail.objects.all().order_by('jobtype_upper')
    serializer_class = serializer.JobtypeDetailSerializer


