from rest_framework import serializers
from .models import (
    CustomUser,
    UserData,
    CustomerReviewInfo,
    ReviewsToPostLater,
    CustomerUser,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "password",
            "business_name",
            "account_type",
            "account_subscription",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],
            password=validated_data["password"],
            business_name=validated_data["business_name"],
            account_type=validated_data["account_type"],
            account_subscription=validated_data["account_subscription"],
        )
        return user


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ("id", "email", "password", "user_score", "user_reviews", "username")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomerUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            user_score=validated_data["user_score"],
            user_reviews=validated_data["user_reviews"],
            password=validated_data["password"],
        )
        return user


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = "__all__"


class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReviewInfo
        fields = "__all__"


class ReviewsToPostLaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewsToPostLater
        fields = [
            "email",
            "name",
            "google_review_url",
            "review_uuid",
            "review_body",
            "customer_url",
            "posted_to_google",
            "tone",
            "badges",
        ]
