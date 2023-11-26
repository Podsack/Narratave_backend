import serpy


class FollowRelationSerializer(serpy.Serializer):
    follower_id = serpy.IntField()
    followee_id = serpy.IntField()
    is_following = serpy.BoolField(attr="is_active")


class UserSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.MethodField()

    def get_name(self, obj):
        return obj.first_name + "_" + obj.last_name


class SubscriptionsUserSerializer():
    followee = UserSerializer()
