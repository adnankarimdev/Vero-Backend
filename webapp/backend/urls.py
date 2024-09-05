from django.urls import path

from .views import create_charts, create_review, create_review_score, send_email, sign_up_user, log_in_user, save_user_review_question_settings, get_review_settings, get_place_id_by_email, set_place_ids, get_review_questions, generate_review_template, generate_review_questions, generate_five_star_review, generate_categories, get_place_details

urlpatterns = [
    path('create-charts/', create_charts, name='create_charts'),
    path('create-review/', create_review, name='create_review'),
    path('create-review-score/', create_review_score, name='create_review_score'),
    path('send-email/', send_email, name='send_email'),
    path('sign-up/', sign_up_user, name='sign_up_user'),
    path('login/', log_in_user, name="log_in_user"),
    path('save-review-settings/', save_user_review_question_settings, name="save_user_review_question_settings"),
    path('get-review-settings/<str:place_ids>/', get_review_settings, name='get_review_settings'),
    path('get-place-id-by-email/<str:email>/', get_place_id_by_email, name='get_place_id_by_email'),
    path('set-place-ids/', set_place_ids, name='set_place_ids'),
    path('get-review-questions/<str:place_id>/', get_review_questions, name='get_review_questions'),
    path('generate-review-template/', generate_review_template, name='generate_review_template'),
    path('generate-review-questions/', generate_review_questions, name='generate_review_questions'),
    path('generate-five-star-review/', generate_five_star_review, name='generate_five_star_review'),
    path('generate-categories/', generate_categories, name='generate_categories'),
    path('get-place-details/<str:place_id>/', get_place_details, name='get_place_details'),
]