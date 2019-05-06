from django.shortcuts import render
from django.utils import timezone
from django.views.generic import (View, ListView, DetailView, TemplateView)
from djangohelpers.views import FilterByQueryParamsMixin
from itertools import chain
from braces.views import LoginRequiredMixin

# import models
from hostlock.models import (Host, Lock)


# Create your views here.
class HostLockIndex(TemplateView):
    """ super simple view for displaying a page with no queried data """
    template_name = "index.html"


class HostlockBaseListView(FilterByQueryParamsMixin, ListView):
    """ base view for shared hostlock listviews """
    title = None
    table = None

    def get(self, request, *args, **kwargs):
        context = dict()
        template = "generic/generic_list.html"
        context['queryset'] = self.filter_by_query_params()
        context['title'] = self.title
        context['sub_title'] = self.page_description
        context['table'] = self.table
        return render(request, template, context=context)


class ListLocks(HostlockBaseListView):
    """ list available all hostlock lock entries  """
    queryset = Lock.objects.all().select_related('host', 'host__owner', 'requester').order_by('-created_at')
    title = "Locks"
    page_description = ""
    table = "table/table_locks.htm"


class ListHosts(HostlockBaseListView):
    """ list available all hostlock host entries  """
    queryset = Host.objects.all().select_related('owner').prefetch_related('lock_set')
    title = "Available Hosts"
    page_description = ""
    table = "table/table_hosts.htm"


class ListMyLocks(LoginRequiredMixin, View):
    """ list current locks that have been granted to user, or a group user is a member of """
    @staticmethod
    def get(request):
        template = 'custom/show_my_locks.html'
        context = dict()
        context['title'] = "Locks for"
        context['sub_title'] = request.user.username
        context['table'] = "table/table_locks.htm"
        context['user_locks'] = Lock.objects.filter(requester=request.user, status='granted')\
            .select_related('requester', 'host', 'host__owner')
        group_locks = Lock.objects.none()
        for group_name in request.user.groups.all():
            group_locks = group_locks | Lock.objects.filter(requester__groups__name=group_name, status='granted')\
                .select_related('requester', 'host', 'host__owner')
        context['group_locks'] = group_locks.exclude(requester=request.user)
        context['historical_locks'] = Lock.objects.filter(requester=request.user).exclude(status='granted')\
            .select_related('requester', 'host', 'host__owner')
        context['stale_locks'] = group_locks.exclude()

        return render(request, template, context=context)


class SelfServicePanel(View):
    """ 'control panel' like self-service page to perform actions such as:
        - update a token
        - create a service account
        - list assets by ownership
        - disable locking for a host or service
        - view action history
        - view/manage locks or owned assets
    """
    pass


class AdminPanel(View):
    """ 'control panel' like view for admins to perform actions such as:
    - revoke a user token
    - disable locking for a host or service
    - list/release/manager current locks
    - delete a host or service
    - view/manage stale locks
    """
    pass


class ApiUserGuide(TemplateView):
    """ show information/examples on using each available API """
    template_name = "help/api_guide.html"
