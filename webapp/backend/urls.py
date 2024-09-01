from django.urls import path

from .views import create_charts, create_review, create_review_score, send_email

urlpatterns = [
    path('create-charts/', create_charts, name='create_charts'),
    path('create-review/', create_review, name='create_review'),
    path('create-review-score/', create_review_score, name='create_review_score'),
    path('send-email/', send_email, name='send_email'),
]