from rest_framework import serializers
from ..utils import AuthUtils
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'first_name', 'last_name', 'role', 'date_joined', 'email', 'country', 'dob']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(raw_password=password)
        user.save()
        return user

    def validate(self, data):
        email = data.get('email')
        role = "CONSUMER" if data.get('role') is None else data.get('role')

        # Check if email already exists
        if User.objects.filter(email=email, role=role).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})

        return data


class GoogleSigninSerializer(serializers.Serializer):
    class Meta:
        google_id_token = serializers.CharField()
        email = serializers.EmailField()

    def create(self, validated_data):
        return User(email=validated_data.get('email'), google_id_token=validated_data.get('google_id_token'))

    def validate(self, data):
        is_token_valid = AuthUtils.validate_google_id_token(data.get('google_id_token'))

        if is_token_valid is False:
            serializers.ValidationError({'id_token': 'Invalid id token'})
