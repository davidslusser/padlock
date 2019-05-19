from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import (View, ListView, DetailView, TemplateView)
from djangohelpers.views import FilterByQueryParamsMixin
from itertools import chain
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count, Sum
import datetime
import collections

# import models
from hostlock.models import (Host, Lock)


# Create your views here.
class HostLockIndex(TemplateView):
    """ super simple view for displaying a page with no queried data """
    template_name = "index2.html"


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
    title = "Hosts"
    page_description = "with lock activity"
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


class ReleaseHostLock(View):
    """ manually release lock on a given host """
    def post(self, request, *args, **kwargs):
        """ process POST request """
        redirect_url = self.request.META.get('HTTP_REFERER')
        lock_id = self.request.GET.dict().get('id', None)
        lock = Lock.objects.get_object_or_none(id=lock_id)
        if lock:
            if lock.release_lock(user=request.user, manual=True):
                messages.add_message(request, messages.ERROR, "failed to release lock",
                                     extra_tags='alert-danger', )
            else:
                messages.add_message(request, messages.ERROR, "Lock released!",
                                     extra_tags='alert-success', )
        return redirect(redirect_url)


class ExtendLock(View):
    """ increase the expire date for a given lock """
    def post(self, request, *args, **kwargs):
        """ process POST request """
        redirect_url = self.request.META.get('HTTP_REFERER')
        lock_id = self.request.GET.dict().get('id', None)
        minutes = self.request.GET.dict().get('minutes', None)
        if not minutes:
            messages.add_message(request, messages.ERROR, "can not extend lock by 0 minutes",
                                 extra_tags='alert-warning', )
            return redirect(redirect_url)
        lock = Lock.objects.get_object_or_none(id=lock_id)
        if lock:
            if lock.extend_lock(user=request.user, minutes=minutes):
                messages.add_message(request, messages.ERROR, "failed to extend lock",
                                     extra_tags='alert-danger', )
            else:
                messages.add_message(request, messages.ERROR, "Lock extended by {}".format(minutes),
                                     extra_tags='alert-success', )
        return redirect(redirect_url)


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


# class ApiUserGuide(TemplateView):
#     """ show information/examples on using each available API """
#     template_name = "help/api_guide.html"


class ApiUserGuide(LoginRequiredMixin, View):
    """ show information/examples on using each available API """
    @staticmethod
    def get(request):
        template = "help/api_guide.html"
        context = dict()
        return render(request, template, context=context)


class HostLockDashboard(LoginRequiredMixin, View):
    """ show a consolidated view containing summarized information regarding host locks """
    # @staticmethod
    def get_24hr_trend_data(self, queryset, timestamp="created_at"):
        """ """
        print("TEST: getting 24hr data...")
        last_day_data = queryset.filter(created_at__gte=(timezone.now() - datetime.timedelta(days=1)))
        print("TEST: ", last_day_data)
        data = {}
        now = timezone.now()
        # for hour in range(0, 24):
        for hour in [(now - datetime.timedelta(hours=i)).hour for i in range(0, 24)]:
            date_diff = now - datetime.timedelta(hours=hour)
            if timestamp == "updated_at":
                data[date_diff.hour] = last_day_data.filter(updated_at__hour=hour).count()
            else:
                data[date_diff.hour] = last_day_data.filter(created_at__hour=hour).count()
        print(data)
        return data

    # @staticmethod
    def get(self, request):
        template = 'custom/show_hostlock_dashboard.html'
        context = dict()
        now = timezone.now()
        all_locks = Lock.objects.filter().select_related('requester', 'host', 'host__owner')
        all_granted_locks = all_locks.filter(status='granted').select_related('requester', 'host', 'host__owner')
        all_released_locks = all_locks.filter(status__in=['released', 'manually released'])
        all_expired_locks = all_granted_locks.filter(no_expire=False, expires_at__lt=now)
        group_locks = Lock.objects.none()
        if request.user and request.user != 'AnonymousUser':
            for group_name in request.user.groups.all():
                group_locks = group_locks | all_granted_locks.filter(requester__groups__name=group_name)
            context['manageable_locks'] = group_locks.distinct() | all_granted_locks.filter(requester=request.user).distinct()
        trend_data = {
            'granted': self.get_24hr_trend_data(all_locks),
            'released': self.get_24hr_trend_data(all_released_locks, timestamp="updated_at"),
            'expired': self.get_24hr_trend_data(all_expired_locks, timestamp="updated_at"),
        }
        context['granted_locks'] = all_granted_locks
        context['current_locks'] = all_granted_locks.filter(Q(expires_at__gte=now) | Q(expires_at=None)).order_by('-created_at')
        context['expired_locks'] = all_granted_locks.filter(expires_at__lt=now).order_by('-created_at')
        context['trend_data'] = trend_data
        return render(request, template, context=context)
