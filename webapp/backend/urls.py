from django.urls import path

from .views import create_charts, create_review

urlpatterns = [
    path('create-charts/', create_charts, name='create_charts'),
    path('create-review/', create_review, name='create_review'),
]