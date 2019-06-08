from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

# import models
from _common.models import UserPreferences, UserRecent


class UserRecentsMiddleware(MiddlewareMixin):
    """ add url to user recents on page request """

    def process_request(self, request):
        """ """
        # define the number of recent urls to track
        max_history = 10

        # do not track url if user is not authenticated
        if not request.user.is_authenticated:
            return
        user = getattr(request, 'user')
        if not user:
            return
        path = getattr(request, 'get_full_path')()
        if not path:
            return

        print("PATH: ", path)

        # if path.startswith('/admin/'):
        #     print("SKIPPING admin urls")
        #     return
        # do not track urls in the skip_url_prefix_list
        skip_url_prefix_list = ['/admin/', '/__debug__/']
        for prefix in skip_url_prefix_list:
            if path.startswith(prefix):
                print("SKIPPING: ", path)
                return

        # do not track urls in the skip_fixed_url_list
        skip_fixed_url_list = ['/', '/admin/', '/login/', '/logout/', '/__debug__/']
        for url in skip_fixed_url_list:
            if path == url:
                print("SKIPPING: ", path)
                return

        # print(type(user))

        # p = UserPreferences.objects.get_or_create(user__username=user.username)[0]
        # recent, is_new = UserRecent.objects.get_or_create(url=request.get_full_path())
        # recent.save()
        # if is_new:
        #     p.recents.add(recent.id)
        #     p.save()

        # todo: validate that url is valid; exit out if not
        from urllib.parse import urlparse
        print("yo!")
        print(path)
        print(urlparse(path).path)


        recent, is_new = UserRecent.objects.get_or_create(url=request.get_full_path(),
                                                          user=request.user,
                                                          defaults=dict(url=request.get_full_path(),
                                                                        user=request.user,
                                                                        updated_at=timezone.now())
                                                          )
        if is_new:
            print('ADDING: ', path)

"""
    to trip recents to only the latest:
    recent_id_list = UserRecent.objects.filter(userpreferences__user__username="david").order_by('-created_at')[:4].values_list("id", flat=True)
    UserRecent.objects.exclude(pk__in=list(recent_id_list)).delete()
"""
