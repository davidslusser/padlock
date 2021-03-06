# import system modules
from datetime import timedelta
import logging

# import django modules
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
from djangohelpers.managers import HandyHelperModelManager

# import third party modules
from auditlog.registry import auditlog

# import PadLock modules
from _common.exceptions import (UserNotAuthorized, HostLocked, LockExpireMissing, MaxLockExtensionReached)


lock_status_choices = (
    ('granted', 'granted'),
    ('released', 'released'),
    ('manually released', 'manually released'),
    ('expired', 'expired'),
)


lock_state_choices = (
    ("locked", "locked"),
    ("unlocked", "unlocked"),
)


class PadlockBaseModel(models.Model):
    """ base model for PadLock tables """
    objects = HandyHelperModelManager()
    created_at = models.DateTimeField(auto_now_add=True, help_text="date/time when this row was first created")
    updated_at = models.DateTimeField(auto_now=True, help_text="date/time this row was last updated")

    class Meta:
        abstract = True

    def get_meta(self):
        return self._meta

    def to_dict(self):
        from django.forms.models import model_to_dict
        return model_to_dict(self)


class Host(PadlockBaseModel):
    """ table to track hosts """
    hostname = models.CharField(max_length=64, unique=True, help_text="unique fqdn of a host")
    owner = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE,
                              help_text="group that owns this host")
    is_locked = models.BooleanField(default=False, help_text="select if this host is currently locked")

    class Meta:
        db_table = 'hostlock_hosts'

    def get_lock(self):
        """ return the current lock, if lock, otherwise return None """
        if self.is_locked:
            return self.lock_set.latest('id')

    def __str__(self):
        return self.hostname


class Lock(PadlockBaseModel):
    """ track the details and results of a lock action request """
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    requester = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                                  help_text="user requesting this lock")
    source = models.CharField(max_length=128, blank=True, null=True, help_text="location this lock was requested from")
    request_details = models.CharField(max_length=255, blank=True, null=True, help_text="details of the request")
    purpose = models.CharField(max_length=254, blank=True, null=True, help_text="details regarding this lock request")
    notes = models.CharField(max_length=255, blank=True, null=True, help_text="additional notes regarding this lock")
    expires_at = models.DateTimeField(blank=True, null=True, default=timezone.now() + timedelta(minutes=15),
                                      help_text="date/time when this lock expires")
    status = models.CharField(max_length=32, choices=lock_status_choices, default="unknown",
                              help_text="current status of this lock")
    no_expire = models.BooleanField(default=False, help_text="set to True if this lock does not expire")
    extend_count = models.IntegerField(default=0, help_text="number of times this lock has been extended")

    class Meta:
        db_table = 'hostlock_locks'

    def clean(self):
        # set the expiration default (for a new lock) if None
        if not self.expires_at and not self.no_expire:
            self.expires_at = timezone.now() + timedelta(minutes=15)

        # check for existing lock on a host
        existing_lock = Lock.objects.get_object_or_none(host=self.host, status='granted')

        if not self.pk and existing_lock:
            # check if lock is expired; set as expired and create new if expired, else reject grant
            if not self.expires_at:
                raise ValidationError({'host': 'this host is currently locked'})
            elif timezone.now() > existing_lock.expires_at:
                Lock.objects.filter(pk=existing_lock.pk).update(status="expired")
            else:
                raise ValidationError({'host': 'this host is currently locked'})

    def get_manageability(self, user):
        """ determine if user can manage (extend/release/etc.) a lock. All admins can manage all locks.
        User can manage lock if they are the original requester -or- a member of the group the original requester
        is in. """
        user_can_manage_lock = False
        if user is self.requester:
            user_can_manage_lock = True
        elif user.is_superuser:
            user_can_manage_lock = True
        elif user.groups.filter(name=getattr(self.host.owner, 'name', None)):
            user_can_manage_lock = True
        return user_can_manage_lock

    def release_lock(self, user, manual=False):
        """ release the current lock """
        if not self.get_manageability(user):
            return 1
        if manual:
            self.status = "manually released"
        else:
            self.status = "released"
        self.save()
        return 0

    def extend_lock(self, user, minutes):
        """
        extend lock by <minutes> minutes
        :param user: user object
        :param minutes: minutes to extend lock by <int>
        :return: <int>
            0 if successful
            1 if error encountered
        """
        if not self.get_manageability(user):
            return UserNotAuthorized

        # do not allow extend if no expires_at is set
        if not self.expires_at or self.no_expire:
            raise LockExpireMissing('the lock on {} does not have an expiration and thus can not be extended'
                                    .format(self.host))

        # do not allow extend if maximum extends have been reached
        max_extend = 3
        if self.extend_count >= max_extend:
            raise MaxLockExtensionReached('the lock on {} has been extended {} times and can not be extended further'
                                          .format(self.host, self.extend_count))

        minutes = int(minutes)
        self.expires_at += timedelta(minutes=minutes)
        self.extend_count = self.extend_count + 1
        self.save()
        return 0

    def save(self, *args, **kwargs):
        self.full_clean()
        # when adding/updating a lock, also set the host is_locked flag to True or False accordingly
        if self.status == 'granted':
            Host.objects.filter(pk=self.host.pk).update(is_locked=True)
        else:
            Host.objects.filter(pk=self.host.pk).update(is_locked=False)
        super().save(*args, **kwargs)


# Models to register with AuditLog
auditlog.register(Host)
auditlog.register(Lock)
