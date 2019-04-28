from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

# import hostlock views and apis
from hostlock import views
from hostlock.apis import views as apis

app_name = "hostlock"

router = DefaultRouter()

# hostlock API Endpoints
router.register(r'host', apis.HostViewSet, "host")
router.register(r'lock', apis.LockViewSet, "lock")
router.register(r'check_lock', apis.CheckLockViewSet, "check_lock")
router.register(r'release_lock', apis.ReleaseLockViewSet, "release_lock")
router.register(r'grant_lock', apis.GrantLockViewSet, "grant_lock")


urlpatterns = [

    # API views
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),

    # home page urls
    path('', views.ShowIndex.as_view(), name='index'),
    path('home', views.ShowIndex.as_view(), name='home'),
    path('default', views.ShowIndex.as_view(), name='default'),

]
