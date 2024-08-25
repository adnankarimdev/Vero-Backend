from django.urls import path

from .views import create_charts 

urlpatterns = [
    path('create-charts/', create_charts, name='create_charts'),
]