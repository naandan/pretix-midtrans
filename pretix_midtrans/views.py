import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django_scopes import scopes_disabled
from pretix.base.models.orders import Order
from pretix_midtrans.payment import MidtransPayment
from pretix.base.settings import GlobalSettingsObject

@csrf_exempt
@require_POST
@scopes_disabled()
def webhook(request, *args, **kwargs):
    event_body = request.body.decode('utf-8').strip()
    event_json = json.loads(event_body)
    gs = GlobalSettingsObject()
    midtrans_payment = MidtransPayment(gs.settings.payment_midtrans_client_key, gs.settings.payment_midtrans_secret_key,  True if gs.settings.payment_midtrans_sandbox else False)
    if event_json['transaction_status'] == 'settlement' and midtrans_payment.verify_transaction(event_json):
        order = Order.objects.get(code=event_json['order_id'])
        payment = order.payments.filter(provider='midtrans').first()
        payment.confirm()

    return HttpResponse(status=200)