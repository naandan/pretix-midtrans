import midtransclient
from pretix.base.payment import BasePaymentProvider
from django.utils.translation import gettext_lazy as _
from pretix.base.models import Event
from pretix.base.settings import SettingsSandbox
from django import forms
from collections import OrderedDict
from django.template.loader import get_template
from pretix.base.i18n import LazyI18nString
from django.http import HttpRequest
from pretix.base.models import Order, OrderPayment
from pretix_midtrans.models import MidtransTransaction

class Midtrans(BasePaymentProvider):
    identifier = 'midtrans'
    verbose_name = _('Midtrans')

    def __init__(self, event: Event):
        super().__init__(event)
        self.settings = SettingsSandbox('payment', 'midtrans', event)
        self.payment = MidtransPayment(self.settings.get('client_key'), self.settings.get('server_key'), True if self.settings.get('sandbox') else False)

    @property
    def settings_form_fields(self):
        main_fields = [
            ('client_key',
             forms.CharField(
                 label=_('Client Key'),
                 help_text=_('Client key from Midtrans Dashboard'),
                 required=True,
             )),
            ('server_key',
             forms.CharField(
                 label=_('Server Key'),
                 help_text=_('Server key from Midtrans Dashboard'),
                 required=True,
             )),
            ('sandbox',
             forms.BooleanField(
                 label=_('Sandbox'),
                 help_text=_('Use sandbox environment'),
                 required=False,
                 initial=True,
             )),
        ]

        extra_fields = [
            ('prefix',
             forms.CharField(
                 label=_('Reference prefix'),
                 help_text=_('Any value entered here will be added in front of the regular booking reference '
                             'containing the order number.'),
                 required=False,
             )),
            ('postfix',
             forms.CharField(
                 label=_('Reference postfix'),
                 help_text=_('Any value entered here will be added behind the regular booking reference '
                             'containing the order number.'),
                 required=False,
             )),
        ]

        d = OrderedDict(
            main_fields + extra_fields + list(super().settings_form_fields.items())
        )
        d.move_to_end('_enabled', False)
        return d
    
    @property
    def public_name(self):
        return str(self.settings.get('public_name', as_type=LazyI18nString) or self.verbose_name)
    
    def settings_content_render(self, request):
        return "Hello, This is Midtrans function settings content render"
        
    def payment_form_render(self, request, total=None, order=None) -> str:
        return "Hello, This is Midtrans function payment form render"

    
    def checkout_prepare(self, request, cart):
        return True

    def payment_prepare(self, request: HttpRequest, payment: OrderPayment):
        print("payment_prepare")
        return True
    
    def payment_is_valid_session(self, request):
        print("payment_is_valid_session")
        return True

    def checkout_confirm_render(self, request, order=None):
        return "Hello, This is Midtrans function checkout confirm render"

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        self.payment.create_transaction(payment.order, request)
    
    def payment_pending_render(self, request: HttpRequest, payment: OrderPayment):
        template = get_template('pretixplugins/midtrans/pay.html')
        transaction = self.payment.get_transaction(payment.order)
        return template.render({'transaction_url': transaction.transaction_url})

class MidtransPayment:
    def __init__(self, client_key: str, server_key: str, sandbox: bool):
        self.client = midtransclient.Snap(
            is_production=not sandbox,
            server_key=server_key,
            client_key=client_key,
        )
    
    def create_transaction(self, order: Order, request: HttpRequest):
        self.client.api_config.custom_headers = {
            'x-override-notification': request.build_absolute_uri('/_midtrans/webhook/'),
        }
        return_url = f"{request.build_absolute_uri('/')}{order.organizer.slug}/{order.event.slug}/order/{order.code}/{order.secret}/?paid=yes"
        params = {
            "transaction_details": {
                "order_id": order.code,
                "gross_amount": str(order.total).split('.')[0],
            },
            "callbacks": {
                "finish": return_url,
            },
            "expiry": {
                "unit": "minute",
                "duration": 5
            }
        }
        try:
            transaction = self.client.create_transaction(params)
            MidtransTransaction.objects.create(
                reference=transaction['token'],
                order=order,
                transaction_url=transaction['redirect_url'],
            )
            return True
        except Exception as e:
            print(e)
            return False
        
    def get_transaction(self, order: Order):
        return MidtransTransaction.objects.filter(order=order).first()
        
    def verify_transaction(self, transaction: dict):
        try:
            transaction = self.client.transactions.status(transaction['order_id'])
            if transaction['transaction_status'] == 'settlement':
                return True
            return False
        except Exception as e:
            print(e)
            return False
