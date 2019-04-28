from django.shortcuts import render
from django.views.generic import (View, ListView, DetailView, TemplateView)


# Create your views here.
class ShowIndex(TemplateView):
    """ super simple view for displaying a page with no queried data """
    template_name = "index.html"
