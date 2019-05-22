from rest_framework import serializers

# import models
from hostlock.models import (Host, Lock)


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ["id", "created_at", "updated_at", "hostname", "is_locked", ]
        depth = 0


class LockSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()
    requester = serializers.StringRelatedField()

    class Meta:
        model = Lock
        fields = ["id", "created_at", "updated_at", "host", "requester", "source", "request_details", "purpose",
                  "notes", "expires_at", "status", ]
        depth = 0


class ExtendLockSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    # name = serializers.CharField(max_length=256)
    # owner = serializers.CharField(max_length=256)
    message = serializers.CharField(max_length=256)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance
