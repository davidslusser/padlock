from django.contrib import admin

# Register your models here.
from _common.models import (UserPreferences, UserRecent, UserFavorite)

# Register your models here.
admin.site.register(UserPreferences)
admin.site.register(UserRecent)
admin.site.register(UserFavorite)
