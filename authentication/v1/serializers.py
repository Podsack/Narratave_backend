from rest_framework import serializers
from userprofile.models import Preference
from asgiref.sync import sync_to_async
from ..utils.auth_utils import AuthUtils
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'first_name', 'last_name', 'role', 'date_joined', 'email', 'dob']
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


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ['country', 'state', 'preferred_app_language', 'preferred_podcast_languages', 'user']

    async def get_by_user_id(self, user_id):
        try:
            return await self.Meta.model.objects.aget(user_id=user_id)
        except self.Meta.model.DoesNotExist:
            return None

    @sync_to_async
    def save(self, **kwargs):
        if self.is_valid(raise_exception=True):
            validated_data = dict(
                list(self.validated_data.items()) +
                list(kwargs.items())
            )

            if self.instance is not None:
                self.instance = self.update(self.instance, validated_data)
            else:
                self.instance = self.create(validated_data)
        return self.instance
