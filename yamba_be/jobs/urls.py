from rest_framework import routers
from .views import JobViewSet,CategoryViewSet, SkillViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register('jobs', JobViewSet)
router.register('categories', CategoryViewSet)
router.register('skills', SkillViewSet)

urlpatterns = [
    path('', include(router.urls)),
]