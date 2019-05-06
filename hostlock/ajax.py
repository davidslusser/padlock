"""
Views used specifically for handling AJAX Requests
"""
# import system modules
import json

# import django modules
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.http import require_GET, require_POST

# import models
from auditlog.models import LogEntry
from hostlock.models import Lock


@require_GET
def get_host_auditlog(request):
    """
    Description:
        get AuditLog for a given Host.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            hostname = request.GET['client_response']
            queryset = LogEntry.objects.filter(content_type__model="host",
                                               object_repr__icontains=hostname)
            template = loader.get_template('ajax/show_audit_log.htm')
            return HttpResponse(json.dumps({"server_response": template.render({'queryset': queryset})}),
                                content_type='application/javascript')
        else:
            return HttpResponse("Invalid request inputs", status=400)
    else:
        return HttpResponse("Invalid request", status=400)


@require_GET
def get_lock_auditlog(request):
    """
    Description:
        get AuditLog for a given Lock.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            lock = request.GET['client_response']
            queryset = LogEntry.objects.filter(content_type__model="lock",
                                               object_repr__icontains=lock)
            template = loader.get_template('ajax/show_audit_log.htm')
            return HttpResponse(json.dumps({"server_response": template.render({'queryset': queryset})}),
                                content_type='application/javascript')
        else:
            return HttpResponse("Invalid request inputs", status=400)
    else:
        return HttpResponse("Invalid request", status=400)


@require_POST
def release_host_lock(request):
    """
    Manually release a lock on a host
    :param request:
        ajax request object
    :return:
        JSON formatted response
    """
    if (request.is_ajax()) and (request.method == 'POST'):
        if 'client_response' in request.POST:
            lock = request.GET['client_response']
    lock_id = request.POST['client_response']
    lock = Lock.objects.get(id=lock_id)
    if lock.release_lock(user=request.user, manual=True):
        return HttpResponse(json.dumps({'msg': 'Failed to release lock on {}'.format(lock.host.hostname)}), status=400)
    else:
        return HttpResponse(json.dumps({'msg': 'Lock on {} successfully released'.format(lock.host.hostname)}))
