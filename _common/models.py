"""

"""

from django.db import models
from django.contrib.auth.models import User, Group
from djangohelpers.managers import HandyHelperModelManager


THEME_CHOICES = (('normal', 'normal'), ('dark', 'dark'), ('light', 'light'))


class UserExtensionBaseModel(models.Model):
    """ base model for UserExtension tables """
    objects = HandyHelperModelManager()
    created_at = models.DateTimeField(auto_now_add=True, help_text="date/time when this row was first created")
    updated_at = models.DateTimeField(auto_now=True, help_text="date/time this row was last updated")

    class Meta:
        abstract = True


class UserPreferences(UserExtensionBaseModel):
    """ table to track user preferences """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=16, blank=True, null=True, choices=THEME_CHOICES,
                             help_text="name of theme to user for this user")
    recents_count = models.IntegerField(default=10, help_text="number of recents to keep a record of")

    def __str__(self):
        return self.user.username


class UserRecent(UserExtensionBaseModel):
    """ table to track user's recently visited urls """
    url = models.URLField(help_text="url endpoint")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('url', 'user'), )

    def __str__(self):
        return self.url


class UserFavorite(UserExtensionBaseModel):
    """ table to track user's favorite urls """
    name = models.CharField(max_length=32, blank=True, null=True, help_text="name/label/reference for this favorite")
    url = models.URLField(help_text="url endpoint")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('url', 'user'), )

    def __str__(self):
        return self.url

# class ServiceAccount(User):
#     """ table to track service accounts and their related group """
#     # group = models.OneToOneField(Group, on_delete=models.CASCADE)
#     # user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # name = models.CharField(max_length=64, unique=True, help_text="name of this service account")
#     # enabled = models.BooleanField(default=True, help_text="select if this service account is enabled")
#
#     # todo: add vailidation to only allow ONE service account per group
