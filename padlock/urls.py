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
from django.conf import settings
from django.urls import path, include
from django.contrib.auth.views import login, logout_then_login
from userextensions.urls import *
from _common import views as common
from hostlock import views as hostlock

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login, {'template_name': 'registration/login.html'}, name="login"),
    path('logout/', logout_then_login, name="logout"),
    path('detail_user/', common.ShowUserProfile.as_view(), name='detail_user'),
    path('', include('userextensions.urls'), ),

    # app urls
    path('userextensions/', include('userextensions.urls'), ),
    path('hostlock/', include('hostlock.urls'), ),
    path('common/', include('_common.urls'), ),

    # home/default/index urls
    path('', common.PadLockIndex.as_view(), name='index'),
    path(r'default', common.PadLockIndex.as_view(), name='default'),
    path(r'home', common.PadLockIndex.as_view(), name='home'),
    path(r'index', common.PadLockIndex.as_view(), name='index'),

    # swagger API docs
    path('swagger', common.schema_view, name="swagger"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
