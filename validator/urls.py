from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('validate/', views.validate_yaml, name='validate_yaml'),
    path('correct/', views.correct_yaml, name='correct_yaml'),
]
