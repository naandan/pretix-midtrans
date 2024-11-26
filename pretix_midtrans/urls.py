from pretix_midtrans.views import webhook
from django.urls import re_path

urlpatterns = [
    re_path(r'^_midtrans/webhook/$', webhook, name='webhook'),
]
