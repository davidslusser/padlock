"""
Description:
    django views for serving ajax responses
"""

# import system modules
import json
import datetime

# import django modules
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q
from django.utils import timezone

# import models
from hostlock.models import (Host, Lock)


@require_POST
def release_host_lock(request):
    """
    Description:
        release a lock on a host.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'POST'):
        if 'client_response' in request.POST:
            lock_id = request.POST['client_response']
            lock = Lock.objects.get_object_or_none(id=lock_id)
            lock.release_lock(user=request.user, manual=True)
            return HttpResponse(json.dumps({"msg": 'lock released'}))
        else:
            return HttpResponse("Invalid request inputs", status=400)
    else:
        return HttpResponse("Invalid request", status=400)


def get_host_lock_history(request):
    """ """
    pass
