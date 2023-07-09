from rest_framework.serializers import ModelSerializer
from ..models import Preference


class UserPreferenceSerializer(ModelSerializer):
    class Meta:
        model = Preference
        fields = ['country', 'state', 'preferred_app_language', 'preferred_podcast_languages', 'user']

    async def get_by_user_id(self, user_id):
        try:
            return await self.Meta.model.objects.aget(user_id=user_id)
        except self.Meta.model.DoesNotExist:
            return None

    def save(self, **kwargs):
        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
        else:
            self.instance = self.create(validated_data)
        return self.instance
