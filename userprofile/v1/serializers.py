from rest_framework.serializers import ModelSerializer
from ..models import Preference


class UserPreferenceSerializer(ModelSerializer):
    class Meta:
        model = Preference
        fields = ['country', 'state', 'preferred_app_language', 'preferred_podcast_languages', 'user']
