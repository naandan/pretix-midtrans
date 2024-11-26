from django.dispatch import receiver
from pretix.base.signals import register_payment_providers, register_global_settings
from collections import OrderedDict
from django import forms
from pretix.base.forms import SecretKeySettingsField
from django.utils.translation import gettext_lazy as _
from pretix_midtrans.payment import Midtrans


@receiver(register_payment_providers, dispatch_uid="midtrans_payment")
def register_payment_provider(sender, **kwargs):
    return Midtrans

@receiver(register_global_settings, dispatch_uid='midtrans_global_settings')
def register_global_settings(sender, **kwargs):
    return OrderedDict([
        ('payment_midtrans_client_key', forms.CharField(
            label=_('Midtrans Client Key'),
            required=False,
        )),
        ('payment_midtrans_secret_key', SecretKeySettingsField(
            label=_('Midtrans Secret Key'),
            required=False,
        )),
        ('payment_midtrans_sandbox', forms.BooleanField(
            label=_('Sandbox'),
            required=False,
            initial=True,
        )),
    ])
