"""
PadLock exception and warning classes.
"""
from django.core.exceptions import ValidationError


class LockExpireMissing(Exception):
    """The requested lock can not be extended as it has no expire datetime"""
    pass


class MaxLockExtensionReached(ValidationError):
    """The requested lock can not be extended as it has reached the maximum number of extensions"""
    pass


class UserNotAuthorized(Exception):
    """User is not authorized to manage this lock"""
    pass


class HostLocked(Exception):
    """This host is currently locked"""
    pass

