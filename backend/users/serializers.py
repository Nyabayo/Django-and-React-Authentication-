# users/serializers.py

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

User = get_user_model()

class CreateUserSerializer(UserCreateSerializer):
    # ✅ Explicitly define the role field for validation
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.SEEKER)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # ✅ Extract and apply the role during user creation
        role = validated_data.pop('role', User.Role.SEEKER)
        user = super().create(validated_data)
        user.role = role
        user.save()
        return user


class CustomUserSerializer(UserSerializer):  # Used by Djoser GET /users/me/
    class Meta(UserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
