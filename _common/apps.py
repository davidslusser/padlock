from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = '_common'

    def ready(self):
        import _common.signals
