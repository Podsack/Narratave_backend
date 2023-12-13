from rest_framework import serializers
from userprofile.models import Preference
from asgiref.sync import async_to_sync
from ..utils.auth_utils import AuthUtils
from ..models import User
from ..utils.http_clients import IPClient


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ['country', 'state', 'preferred_app_language', 'preferred_podcast_languages', 'preferred_category_ids', 'user']

    async def get_by_user_id(self, user_id):
        try:
            return await self.Meta.model.objects.aget(user_id=user_id)
        except self.Meta.model.DoesNotExist:
            return None

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


class UserSerializer(serializers.ModelSerializer):
    preference = UserPreferenceSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'first_name', 'last_name', 'date_joined', 'email', 'dob', 'preference']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['first_name', 'last_name', 'date_joined', 'preference']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data, username=validated_data.get('email'))
        user.set_password(raw_password=password)
        user.save()
        current_ip = AuthUtils.get_client_ip_address(request=self.context.get('request'))
        ip_client = IPClient()

        location_data = async_to_sync(ip_client.get_location_data)(ip=current_ip)

        country = location_data.get('country') or "IN"
        state = location_data.get('region') or "West Bengal"

        preference = Preference.objects.create(user=user, country=country, state=state)
        return user

    def validate(self, data):
        email = data.get('email')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
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