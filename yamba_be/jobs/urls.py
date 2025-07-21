from rest_framework import routers
from .views import JobViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register('jobs', JobViewSet)