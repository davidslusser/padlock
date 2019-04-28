"""padlock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from _common import views as common
from hostlock import views as hostlock

urlpatterns = [
    path('admin/', admin.site.urls),

    # app urls
    path('hostlock/', include('hostlock.urls'), ),
    # path(r'default', hostlock.ShowHostlockHome.as_view(), name='default'),
    # path(r'home', hostlock.ShowHostlockHome.as_view(), name='home'),
    # path(r'index', hostlock.ShowHostlockHome.as_view(), name='index'),

    # swagger API docs
    path('swagger', common.schema_view, name="swagger"),
]
