from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CustomAppConfig(AppConfig):
    name = 'metric'
    verbose_name = _("Statistics")

    def ready(self):
        from . import checks
