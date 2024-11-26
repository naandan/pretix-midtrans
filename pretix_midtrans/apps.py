from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from . import __version__


class PluginApp(AppConfig):
    default = True
    name = "pretix_midtrans"
    verbose_name = _("Midtrans Payment")

    class PretixPluginMeta:
        name = _("Midtrans Payment")
        author = _("Nandan Ramdani")
        description = _("Plugin for pretix payment with midtrans")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=4.17.0"

    def ready(self):
        from . import signals  # NOQA
