from django.db import models
from location_field.models.plain import PlainLocationField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from accounting.exceptions import UnbalancedTransactionException
from accounting.validators import BalancedTransaction
from budget_auth.models import User
from budget_utils.models import InvariantMixin
from budget_utils.validators import CreateOnlyInvariant


class Commodity(models.Model):
    CURRENCY = 0

    commodity_types = (
        (CURRENCY, 'Currency'),
    )

    commodity_type = models.IntegerField(choices=commodity_types)
    mnemonic = models.CharField(max_length=32)
    fraction = models.PositiveIntegerField(default=1)


class CommodityRate(InvariantMixin):
    """
    BasicCommodity * rate = RateCommodity
    """
    invariants = (CreateOnlyInvariant,)

    basic_commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='rated')
    rate_commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='rating')
    rate = models.FloatField()


class Account(MPTTModel):
    name = models.CharField(blank=True, max_length=256)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='accounts')

    class MPTTMeta:
        order_insertion_by = ['id']


class Book(models.Model):
    root_account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='book')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Location(models.Model):
    address = models.TextField()
    lat_lng = PlainLocationField(based_fields=['address'])


class Transaction(InvariantMixin):
    invariants = (BalancedTransaction,)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transactions')
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    def balance_transaction(self, rest):
        account = Account.objects.get_or_create(name='Unbalanced', author=self.author)
        Split.objects.create(amount=-rest, transaction=self, account=account)

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except UnbalancedTransactionException as ute:
            self.balance_transaction(ute.transaction_rest)
            super().save(*args, **kwargs)


class Split(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='splits')
    amount = models.PositiveIntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='splits')
    commodity_rate = models.ForeignKey(CommodityRate, on_delete=models.CASCADE, related_name='splits')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.transaction.save()
