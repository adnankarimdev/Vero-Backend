from django.urls import path

from .views import (
    create_charts,
    create_review,
    create_review_score,
    send_email,
    sign_up_user,
    sign_up_customer,
    log_in_user,
    log_in_customer,
    save_user_review_question_settings,
    get_review_settings,
    get_place_id_by_email,
    set_place_ids,
    get_review_questions,
    generate_review_template,
    generate_review_questions,
    generate_five_star_review,
    generate_categories,
    get_place_details,
    save_customer_review,
    get_reviews_by_client_ids,
    send_email_to_post_later,
    get_review_by_uuid,
    update_review_data,
    get_client_catgories,
    chat_with_badges,
    get_user_data,
    translate_language,
    translate_badge,
    generate_google_review_response,
    product_page,
    stripe_webhook,
    get_review_data_customer,
    get_customer_reviewed_places,
    get_personal_reviews,
    already_posted_to_google,
    get_customer_score,
    get_place_information,
    customer_journey_analysis,
    save_user_avatar,
    get_customer_svgs,
    get_customer_information,
    website_creator,
    get_website_details,
    get_website_message,
    get_linear_task_by_place_id,
    update_task,
)

urlpatterns = [
    path("create-charts/", create_charts, name="create_charts"),
    path("create-review/", create_review, name="create_review"),
    path("save-user-avatar/", save_user_avatar, name="save_user_avatar"),
    path("create-review-score/", create_review_score, name="create_review_score"),
    path("send-email/", send_email, name="send_email"),
    path("sign-up/", sign_up_user, name="sign_up_user"),
    path("sign-up-customer/", sign_up_customer, name="sign_up_customer"),
    path("login/", log_in_user, name="log_in_user"),
    path("login-customer/", log_in_customer, name="log_in_customer"),
    path(
        "save-review-settings/",
        save_user_review_question_settings,
        name="save_user_review_question_settings",
    ),
    path(
        "get-review-settings/<str:place_ids>/",
        get_review_settings,
        name="get_review_settings",
    ),
    path(
        "get-client-categories/<str:place_id>/",
        get_client_catgories,
        name="get_client_catgories",
    ),
    path(
        "get-place-id-by-email/<str:email>/",
        get_place_id_by_email,
        name="get_place_id_by_email",
    ),
    path("set-place-ids/", set_place_ids, name="set_place_ids"),
    path(
        "get-review-questions/<str:place_id>/",
        get_review_questions,
        name="get_review_questions",
    ),
    path(
        "generate-review-template/",
        generate_review_template,
        name="generate_review_template",
    ),
    path(
        "generate-review-questions/",
        generate_review_questions,
        name="generate_review_questions",
    ),
    path(
        "generate-five-star-review/",
        generate_five_star_review,
        name="generate_five_star_review",
    ),
    path("generate-categories/", generate_categories, name="generate_categories"),
    path(
        "get-place-details/<str:place_id>/", get_place_details, name="get_place_details"
    ),
    path("save-customer-review/", save_customer_review, name="save_customer_review"),
    path(
        "get-reviews-by-client-ids/",
        get_reviews_by_client_ids,
        name="get_reviews_by_client_ids",
    ),
    path(
        "get-customer-svgs/",
        get_customer_svgs,
        name="get_customer_svgs",
    ),
    path(
        "send-email-to-post-later/",
        send_email_to_post_later,
        name="send_email_to_post_later",
    ),
    path(
        "get-review-by-uuid/<str:review_uuid>/",
        get_review_by_uuid,
        name="get_review_by_uuid",
    ),
    path("update-review-data/", update_review_data, name="update_review_data"),
    path("chat-with-badges/", chat_with_badges, name="chat_with_badges"),
    path(
        "get-user-data/<str:email>/",
        get_user_data,
        name="get_user_data",
    ),
    path("translate-language/", translate_language, name="translate_language"),
    path("translate-badge/", translate_badge, name="translate_badge"),
    path(
        "generate-google-review-response/",
        generate_google_review_response,
        name="generate_google_review_response",
    ),
    path("product-page/", product_page, name="product_page"),
    # cant have appending slash for stripe (?)
    path("stripe_webhook", stripe_webhook, name="stripe_webhook"),
    path(
        "get-review-data-customer/",
        get_review_data_customer,
        name="get_review_data_customer",
    ),
    path(
        "get-place-information/",
        get_place_information,
        name="get_place_information",
    ),
    path(
        "get-customer-score/<str:email>/",
        get_customer_score,
        name="get_customer_score",
    ),
    path(
        "get-customer-information/<str:email>/",
        get_customer_information,
        name="get_customer_information",
    ),
    path(
        "get-website-message/<str:email>/",
        get_website_message,
        name="get_website_message",
    ),
    path(
        "get-website-details/<str:slug>/",
        get_website_details,
        name="get_website_details",
    ),
    path(
        "get-customer-reviewed-places/<str:email>/",
        get_customer_reviewed_places,
        name="get_customer_reviewed_places",
    ),
    path(
        "get-personal-reviews/<str:email>/",
        get_personal_reviews,
        name="get_personal_reviews",
    ),
    path(
        "already-posted-to-google/",
        already_posted_to_google,
        name="already_posted_to_google",
    ),
    path(
        "customer-journey-analysis/",
        customer_journey_analysis,
        name="customer_journey_analysis",
    ),
    path(
        "website-creator/",
        website_creator,
        name="website_creator",
    ),
    path(
        "get-linear-task-by-place-id/<str:place_id>/",
        get_linear_task_by_place_id,
        name="get_linear_task_by_place_id",
    ),
    path('update-task/<str:place_id>/', update_task, name='update_task'),
]
