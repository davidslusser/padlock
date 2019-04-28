from django.shortcuts import render

from braces.views import LoginRequiredMixin, GroupRequiredMixin

from django.http import HttpResponse
from django.views.generic import (View, TemplateView)
from django.shortcuts import render
from rest_framework import response, schemas
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer


# Create your views here.
@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='Atmosphere APIs')
    return response.Response(generator.get_schema(request=request))


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
