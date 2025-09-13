from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatViewSet, MissionViewSet

router = DefaultRouter()
router.register(r'cats', CatViewSet, basename='cat')
router.register(r'missions', MissionViewSet, basename='mission')

urlpatterns = [
    path('', include(router.urls)),
]
