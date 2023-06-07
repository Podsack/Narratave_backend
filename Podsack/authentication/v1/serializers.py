from rest_framework.serializers import ModelSerializer, ValidationError
from ..models import User


class UserSerializer(ModelSerializer):
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
            raise ValidationError({'email': 'Email already exists.'})

        return data



