from django.db import models

class MidtransTransaction(models.Model):
    reference = models.CharField(max_length=190, db_index=True, unique=True)
    order = models.ForeignKey('pretixbase.Order', on_delete=models.CASCADE, related_name='midtrans_transaction')
    payment = models.ForeignKey('pretixbase.OrderPayment', null=True, blank=True, on_delete=models.CASCADE)
    transaction_url = models.CharField(max_length=190)