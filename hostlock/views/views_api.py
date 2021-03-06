import json
from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from rest_framework.views import APIView

from _common.helper_functions import get_requester_ip

# import models
from hostlock.models import (Host, Lock)

# import serializers
from hostlock.serializers import (HostSerializer, LockSerializer)


class HostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Hosts to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend, )
    model = Host
    queryset = model.objects.all().select_related()
    serializer_class = HostSerializer
    filter_fields = ["id", "created_at", "updated_at", "hostname", "is_locked", ]
    search_fields = filter_fields


class LockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Locks to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend, )
    model = Lock
    queryset = model.objects.all().select_related()
    serializer_class = LockSerializer
    filter_fields = ["id", "created_at", "updated_at", "host", "requester", "source", "request_details", "purpose",
                     "notes", "expires_at", "status", ]
    search_fields = filter_fields


class GrantLockViewSet(viewsets.ViewSet):
    """
    Description:
        request a lock for a given host

    Workflow:
        - if host does not exist, add to host table
        - if there is a current lock on this host, reject request and provide lock details
        - if there is an expired lock on this host, release lock and grant request

    To use:
        curl -X POST http://127.0.0.1:8787/hostlock/api/v1/grant_lock/ -H 'Authorization: Token 98d8b8302d93b82edbfb329697c84a25445db3a5' -H rlencoded -d '{"hostname":"host4", "purpose":"test"}'
    """
    @staticmethod
    def create(request):
        """ API entry point; viewset expects a pk value; we use this as the hostname (str) """
        data = json.loads(request.body)
        hostname = data.get('hostname')
        purpose = data.get('purpose')
        notes = data.get('notes')
        expiration = data.get('expiration')
        source = get_requester_ip(request)

        if not hostname:
            return Response({'message': 'hostname is required to grant lock'.format(hostname)},
                            status.HTTP_400_BAD_REQUEST)

        # check if host exists; create if new
        host = Host.objects.get_or_create(hostname=hostname, defaults={'hostname': hostname, 'is_locked': False})[0]

        try:
            # create a lock for host
            if expiration in ['0']:
                expires_at = None
                no_expire = True
            elif expiration:
                expires_at = timezone.now() + timedelta(minutes=int(expiration))
                no_expire = False
            else:
                expires_at = None
                no_expire = False
            new_lock = Lock.objects.create(host=host, requester=request.user, purpose=purpose, notes=notes,
                                           expires_at=expires_at, status="granted", no_expire=no_expire,
                                           source=source)
            lock_serializer = LockSerializer(new_lock)
            return Response(lock_serializer.data)
        except ValidationError as err:
            return Response(err.message_dict, status.HTTP_303_SEE_OTHER)


class ReleaseLockViewSet(APIView):
    """
    Description:
        release a lock on a given host

    Workflow:
        - if there is not a lock on this host, return appropriate message with 200 status
        - if user is the original requester of the lock, or an owner of the host, or an admin, release the lock,
          else, reject the release request

    To use:
        curl -X PUT http://127.0.0.1:8787/hostlock/api/v1/release_lock/ -H 'Authorization: Token 98d8b8302d93b82edbfb329697c84a25445db3a5' -d '{"hostname":"host4"}
    """
    def put(self, request):
        """ API entry point; viewset expects a pk value; we use this as the hostname (str) """
        data = json.loads(request.body)
        hostname = data.get('hostname')

        # check if a host exists; return appropriate message if not
        host = Host.objects.get_object_or_none(hostname=hostname)
        if not host:
            return Response({'message': 'host {} was not found'.format(hostname)}, status.HTTP_400_BAD_REQUEST)

        # get current lock (or none) for host
        lock = Lock.objects.get_object_or_none(host__hostname=hostname, status='granted')

        # check if host is currently locked; return appropriate message if not locked
        if not lock:
            return Response({'message': '{} is not currently locked'.format(hostname)}, status.HTTP_200_OK)

        # attempt to release the lock; return appropriate response
        try:
            lock.release_lock(request.user)
            return Response({'message': 'lock on {} successfully released'.format(hostname)}, status.HTTP_200_OK)
        except Exception as err:
            return Response({'messages': err}, status.HTTP_400_BAD_REQUEST)


class CheckLockViewSet(APIView):
    """
    Description:
        Check if a given host is currently locked; return lock details if locked, or appropriate message if not

    Workflow:
        - check if there is an existing lock on the given host, return lock details (via serializer) if found

    To use:
        curl -X GET http://127.0.0.1:8787/hostlock/api/v1/check_lock/host1/ -H 'Authorization: Token 98d8b8302d93b82edbfb329697c84a25445db3a5' -H 'Content-Type: application/x-www-form-urlencoded'
    """
    @staticmethod
    def get(request):
        """ API entry point; viewset expects a pk value; we use this as the hostname (str) """
        try:
            data = json.loads(request.body)
            hostname = data.get('hostname')

            # check if a host exists; return appropriate message if not
            host = Host.objects.get_object_or_none(hostname=hostname)
            if not host:
                return Response({'message': 'host {} was not found'.format(hostname)}, status.HTTP_303_SEE_OTHER)

            # get current lock (or none) for host
            lock = Lock.objects.get_object_or_none(host__hostname=hostname, status='granted')
            if not lock:
                return Response({'message': '{} is not currently locked'.format(hostname)}, status.HTTP_200_OK)
            else:
                lock_serializer = LockSerializer(Lock.objects.get(id-lock.id))
                return Response(lock_serializer.data)
        except Exception as err:
            return Response({'error': str(err)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExtendLockViewSet(APIView):
    """
    Description:
        extend an existing lock on a given host

    Workflow:
        - if there is not a lock on this host, return appropriate message with 303 status
        - if user is the original requester of the lock, or an owner of the host, or an admin, extend the lock,
          else, reject the request

    To use:
        curl -X PUT http://127.0.0.1:8787/hostlock/api/v1/extend_lock/ -H 'Authorization: Token 98d8b8302d93b82edbfb329697c84a25445db3a5' -H 'Content-Type: application/x-www-form-urlencoded' -d '{"hostname":"host5", "minutes":"4"}'

    """
    @staticmethod
    def put(request):
        """ API entry point; viewset expects a pk value; we use this as the hostname (str) """
        data = json.loads(request.body)
        hostname = data.get('hostname')
        minutes = data.get('minutes')

        # check if a host exists; return appropriate message if not
        host = Host.objects.get_object_or_none(hostname=hostname)
        if not host:
            return Response({'message': 'host {} was not found'.format(hostname)}, status.HTTP_400_BAD_REQUEST)

        # get current lock (or none) for host
        lock = Lock.objects.get_object_or_none(host__hostname=hostname, status='granted')

        # check if host is currently locked; return appropriate message if not locked
        if not lock:
            return Response({'message': '{} is not currently locked'.format(hostname)}, status.HTTP_200_OK)

        # attempt to extend the lock; return appropriate response
        try:
            lock.extend_lock(request.user, minutes)
            lock_serializer = LockSerializer(lock)
            return Response(lock_serializer.data)
        except Exception as err:
            return Response({'messages': err}, status.HTTP_400_BAD_REQUEST)
