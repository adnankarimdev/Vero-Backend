from rest_framework import serializers
from .models import CustomUser, UserData, CustomerReviewInfo, ReviewsToPostLater

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'business_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password'],
            business_name=validated_data['business_name']
        )
        return user
    
class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReviewInfo
        fields = '__all__'

class ReviewsToPostLaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewsToPostLater
        fields = ['email', 'name', 'google_review_url', 'review_uuid', 'review_body', 'customer_url']