from django.urls import path

# import hostlock views and apis
from _common import views

app_name = "_common"


urlpatterns = [

    # action views
    path('update_token/', views.UpdateApiToken.as_view(), name='update_token'),
    path('show_admin/', views.ShowAdminPage.as_view(), name='show_admin'),

]
