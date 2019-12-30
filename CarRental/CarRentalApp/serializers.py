from rest_framework import serializers
from .models import User

class UserEntrySerializer(serializers.Serializer):

    email = serializers.CharField(max_length=200)
    id = serializers.CharField(max_length=200)
    mobile = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    namespace = serializers.CharField(max_length=200)
    confirmation_hash = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()
    href = serializers.CharField(max_length=200)
    target_id = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=200)
    updated = serializers.DateTimeField()

    # def update(self, instance, validated_data):
    #     instance.user_id = validated_data.get('id', instance.user_id)
    #     instance.name = validated_data.get("name", instance.name)
    #     instance.mobile = validated_data.get("mobile", instance.mobile)
    #     instance.namespace = validated_data.get("namespace", instance.namespace)
    #     instance.confirmation_hash = validated_data.get("confirmation_hash", instance.confirmation_hash)
    #     instance.target_id = validated_data.get("target_id", instance.target_id)
    #     instance.href = validated_data.get("href", instance.href)
    #     instance.type = validated_data.get("type", instance.type)
    #     instance.created_at = validated_data.get("created", instance.created_at)
    #     instance.updated_at = validated_data.get("updated", instance.updated_at)
    #     instance.save()
    #     return instance

    def create(self, validated_data):
        user = User.objects.create(
            email = validated_data.get("email"),
            user_id = validated_data.get("id"),
            name = validated_data.get("name"),
            mobile = validated_data.get("mobile"),
            namespace = validated_data.get("namespace"),
            confirmation_hash = validated_data.get("confirmation_hash"),
            target_id = validated_data.get("target_id"),
            href = validated_data.get("href"),
            type = validated_data.get("type"),
            created_at = validated_data.get("created"),
            updated_at = validated_data.get("updated"))
