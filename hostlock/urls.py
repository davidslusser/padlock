from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

# import hostlock views and apis
from hostlock import views
from hostlock.apis import views as apis
from hostlock import ajax

app_name = "hostlock"

router = DefaultRouter()

# hostlock API Endpoints
router.register(r'host', apis.HostViewSet, "host")
router.register(r'lock', apis.LockViewSet, "lock")
router.register(r'check_lock', apis.CheckLockViewSet, "check_lock")
# router.register(r'release_lock', apis.ReleaseLockViewSet, "release_lock")
router.register(r'grant_lock', apis.GrantLockViewSet, "grant_lock")
# router.register(r'extend_lock', apis.ExtendLockViewSet, "extend_lock")


urlpatterns = [

    # API views
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),
    # path('api/v1/blah/<str:hostname>/', apis.Blah.as_view()),
    path('api/v1/blah/', apis.Blah.as_view()),
    path('api/v1/extend_lock/', apis.ExtendLockViewSet.as_view()),
    path('api/v1/release_lock/', apis.ReleaseLockViewSet.as_view()),


    # home page urls
    path('', views.HostLockIndex.as_view(), name='index'),
    path('home', views.HostLockIndex.as_view(), name='home'),
    path('default', views.HostLockIndex.as_view(), name='default'),

    # custom views
    path('hostlock_dashboard/', views.HostLockDashboard.as_view(), name='hostlock_dashboard'),
    path('hostlock_api_guide/', views.ApiUserGuide.as_view(), name='hostlock_api_guide'),

    # list views
    path('list_locks/', views.ListLocks.as_view(), name='list_locks'),
    path('list_hosts/', views.ListHosts.as_view(), name='list_hosts'),
    path('list_my_locks', views.ListMyLocks.as_view(), name='list_my_locks'),

    # action views
    path('release_host_lock', views.ReleaseHostLock.as_view(), name='release_host_lock'),

    # ajax views
    path('get_lock_auditlog', ajax.get_lock_auditlog, name='get_lock_auditlog'),
    path('get_host_auditlog', ajax.get_host_auditlog, name='get_host_auditlog'),
    # path('release_host_lock', ajax.release_host_lock, name='release_host_lock'),
]
