#!/usr/bin/env python

# import system modules
import sys
import os
import random
import django
from django.core.exceptions import ValidationError

# setup django
sys.path.append(os.environ['HOME'] + '/code/padlock')
# this_file_dir = os.path.dirname(os.path.abspath(__file__))
# settings_dir = os.path.dirname(this_file_dir)
# sys.path.append(settings_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "padlock.settings")
django.setup()
from rest_framework.authtoken.models import Token

# import models
from django.contrib.auth.models import (Group, User)
from hostlock.models import (Host, Lock)


def get_random_row(queryset):
    """ return a single, random entry from a queryset """
    random_index = random.randint(0, queryset.count() - 1)
    return queryset[random_index]


def generate_user_data(count=1):
    """
    generate a list of dictionaries containing data necessary to create a User object
    :param count:
    :return:
    """
    return [{'username': 'user_{:03}'.format(i)} for i in range(1, count + 1)]


def generate_group_data(count=1):
    """
    generate a list of dictionaries containing data necessary to create a Group object
    :param count:
    :return:
    """
    return [{'name': 'group_{:03}'.format(i)} for i in range(1, count + 1)]


def generate_host_data(count=1):
    """
    generate a list of dictionaries containing data necessary to create a Host object
    :param count:
    :return:
    """
    return [{'hostname': 'host_{:03}'.format(i),
             'owner': get_random_row(Group.objects.all())
             } for i in range(1, count + 1)]


def generate_lock_data(count=1):
    """
    generate a list of dictionaries containing data necessary to create a Lock object
    :param count:
    :return:
    """
    return [{'host': get_random_row(Host.objects.filter(is_locked=False)),
             'requester': get_random_row(User.objects.all()),
             'status': 'granted'} for i in range(count)]


def create_users(data=None, clean=False, count=1):
    """ """
    if clean:
        User.objects.all().delete()
    if not data:
        data = generate_user_data(count=count)
    for obj in data:
        user, is_new = User.objects.get_or_create(**obj)
        if is_new:
            Token.objects.get_or_create(user=user)


def create_groups(data=None, clean=False, count=1):
    """ """
    if clean:
        Group.objects.all().delete()
    if not data:
        data = generate_group_data(count=count)
    for obj in data:
        group = Group.objects.get_or_create(**obj)[0]

        # add some users to group
        for i in range(0, random.randint(0, 5)):
            group.user_set.add(get_random_row(User.objects.all()))


def create_hosts(data=None, clean=False, count=1):
    """ """
    if clean:
        Host.objects.all().delete()
    if not data:
        data = generate_host_data(count=count)
    for obj in data:
        Host.objects.get_or_create(hostname=obj['hostname'], defaults=obj)


def create_locks(data=None, clean=False, count=1):
    """ """
    if clean:
        Lock.objects.all().delete()
    if not data:
        data = generate_lock_data(count=count)
    for obj in data:
        try:
            Lock.objects.get_or_create(**obj)
        except ValidationError:
            pass


def create_all():
    """ Create all the things! """
    create_users(count=12)
    create_groups(count=4)
    create_hosts(count=12)
    create_locks(count=6)


def main():
    """ script entry point """
    print('Starting local dev data creation')
    create_all()
    print('Done!')


if __name__ == "__main__":
    sys.exit(main())
