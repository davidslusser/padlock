from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

# import hostlock views and apis
import hostlock.views.views_gui as gui
import hostlock.views.views_api as api
import hostlock.views.views_ajax as ajax

app_name = "hostlock"

router = DefaultRouter()

# hostlock API Endpoints
router.register(r'host', api.HostViewSet, "host")
router.register(r'lock', api.LockViewSet, "lock")
router.register(r'grant_lock', api.GrantLockViewSet, "grant_lock")


urlpatterns = [

    # API views
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),
    path('api/v1/extend_lock/', api.ExtendLockViewSet.as_view()),
    path('api/v1/release_lock/', api.ReleaseLockViewSet.as_view()),
    path('api/v1/check_lock/', api.CheckLockViewSet.as_view()),


    # home page urls
    path('', gui.HostLockIndex.as_view(), name='index'),
    path('home', gui.HostLockIndex.as_view(), name='home'),
    path('default', gui.HostLockIndex.as_view(), name='default'),

    # custom views
    path('hostlock_dashboard/', gui.HostLockDashboard.as_view(), name='hostlock_dashboard'),
    path('hostlock_api_guide/', gui.ApiUserGuide.as_view(), name='hostlock_api_guide'),

    # list views
    path('list_locks/', gui.ListLocks.as_view(), name='list_locks'),
    path('list_hosts/', gui.ListHosts.as_view(), name='list_hosts'),
    path('list_my_locks', gui.ListMyLocks.as_view(), name='list_my_locks'),

    # action views
    path('release_host_lock', gui.ReleaseHostLock.as_view(), name='release_host_lock'),

    # ajax views
    path('get_lock_auditlog', ajax.get_lock_auditlog, name='get_lock_auditlog'),
    path('get_host_auditlog', ajax.get_host_auditlog, name='get_host_auditlog'),

]
