from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from hostlock import apis

app_name = "hostlock"

router = routers.DefaultRouter()

# hostlock API Endpoints
router.register(r'host', apis.HostViewSet, "host")
router.register(r'lock', apis.LockViewSet, "lock")


urlpatterns = [

    # API views
    path('hostlock/', include(router.urls),

]
