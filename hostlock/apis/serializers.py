from rest_framework import serializers
# import models
from hostlock.models import (Host,
                             Lock
                             )


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
                  "notes", "expiration", "status", ]
        depth = 0
