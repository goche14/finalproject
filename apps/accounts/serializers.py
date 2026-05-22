from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "password", "password_confirm",
            "role", "bio", "avatar"
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "პაროლები არ ემთხვევა."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)   
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """GET /api/auth/me/ — read + partial update"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "bio", "avatar"]
        read_only_fields = ["id", "role"]  