"""
Description:
    django views for serving web pages
"""

from django.http import HttpResponse
from django.views.generic import (View, ListView, TemplateView, DeleteView)
from django.shortcuts import render, redirect
from django.contrib import messages
from djangohelpers.views import FilterByQueryParamsMixin
from rest_framework import response, schemas
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from braces.views import LoginRequiredMixin, GroupRequiredMixin


# import models
from userextensions.models import (UserRecent, UserFavorite)


class PadlockBaseListView(FilterByQueryParamsMixin, ListView):
    """ base view for shared PadLock listviews """
    title = None
    table = None
    request = None

    def get(self, request, *args, **kwargs):
        context = dict()
        template = "generic/generic_list.html"
        context['queryset'] = self.filter_by_query_params()
        context['title'] = self.title
        context['sub_title'] = self.page_description
        context['table'] = self.table
        return render(request, template, context=context)


@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='PadLock APIs')
    return response.Response(generator.get_schema(request=request))


class PadLockIndex(TemplateView):
    """ display PadLock default/home/index page """
    template_name = "padlock_index.html"


class ShowUserProfile(LoginRequiredMixin, View):
    """ show user profile """
    @staticmethod
    def get(request):
        context = dict()
        context['user'] = request.user
        context['token'] = str(Token.objects.get_or_create(user=request.user)[0])
        context['groups'] = sorted([i.name for i in request.user.groups.all()])
        context['pclouds'] = []
        return render(request, "detail/detail_current_user.html", context)


class ShowAdminPage(LoginRequiredMixin, View):
    """ show the admin page """
    @staticmethod
    def get(request):
        context = dict()
        return render(request, "custom/padlock_admin.html", context)


# class UpdateApiToken(LoginRequiredMixin, View):
#     """ delete current user token and create a new one """
#     def post(self, request):
#         redirect_url = self.request.META.get('HTTP_REFERER')
#         try:
#             token = Token.objects.get(user=request.user)
#             token.delete()
#             Token.objects.get_or_create(user=request.user)
#         except Exception as err:
#             messages.add_message(request, messages.ERROR, "Could not complete requested action",
#                                  extra_tags='alert-danger')
#         return redirect(redirect_url)


class CreateServiceAccount():
    pass


class ListRecents(LoginRequiredMixin, FilterByQueryParamsMixin, ListView):
    """  """
    def get(self, request, *args, **kwargs):
        context = dict()
        self.queryset = UserRecent.objects.filter(user=request.user).order_by('-updated_at')
        template = "generic/generic_list.html"
        context['queryset'] = self.filter_by_query_params()
        context['title'] = "Recents"
        context['sub_title'] = request.user.username
        context['table'] = "table/table_recents.htm"
        return render(request, template, context=context)


class ListFavorites(LoginRequiredMixin, PadlockBaseListView):
    def get(self, request, *args, **kwargs):
        context = dict()
        self.queryset = UserFavorite.objects.filter(user=request.user).order_by('-updated_at')
        template = "generic/generic_list.html"
        context['queryset'] = self.filter_by_query_params()
        context['title'] = "Favorites"
        context['sub_title'] = request.user.username
        context['table'] = "table/table_favorites.htm"
        return render(request, template, context=context)
