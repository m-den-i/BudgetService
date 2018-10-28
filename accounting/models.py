from django.db import models
from location_field.models.plain import PlainLocationField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from accounting.exceptions import UnbalancedTransactionException
from accounting.validators import BalancedTransaction, NonAbstractShouldHaveCommodity, RootIsAbstract
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

    class Meta:
        verbose_name_plural = 'Commodities'

    def __str__(self):
        return f"CMDT{self.id} {self.commodity_type} {self.mnemonic}"


class CommodityRate(InvariantMixin):
    """
    BasicCommodity is current commodity of split (commodity of transaction)
    RateCommodity is target (commodity of target account) commodity of split
    BasicCommodity * rate = RateCommodity
    """
    invariants = (CreateOnlyInvariant(),)

    basic_commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='rated')
    rate_commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='rating')
    rate = models.FloatField()

    def __str__(self):
        return f"RATE{self.id} CMDT{self.basic_commodity_id} CMDT_RT{self.rate_commodity_id}"


class Account(InvariantMixin, MPTTModel):
    invariants = (NonAbstractShouldHaveCommodity(), RootIsAbstract())

    name = models.CharField(blank=True, max_length=256)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)
    abstract = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ['id']

    def __str__(self):
        root = ' ROOT' if self.is_root_node() else ''
        return f"ACC{self.id}{root} {self.name}"


class Book(models.Model):
    root_account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='book')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"BOOK{self.id}"


class Location(models.Model):
    address = models.TextField()
    lat_lng = PlainLocationField(based_fields=['address'])

    def __str__(self):
        return self.address


class Transaction(InvariantMixin):
    # TODO: SameBookForTargetAccounts()
    invariants = (BalancedTransaction(),)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=True, blank=True)

    def balance_transaction(self, rest):
        root_account = self.splits.first().target_account.get_root()
        balance_acc_params = dict(name='Unbalanced-{}'.format(self.commodity.mnemonic), tree_id=root_account.tree_id)
        try:
            account = Account.objects.get(**balance_acc_params)
        except Account.DoesNotExist:
            account = Account(parent=root_account, commodity=self.commodity, **balance_acc_params)
            account.save()
        s = Split(amount=-rest, transaction=self, target_account=account)
        s.save()

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except UnbalancedTransactionException as ute:
            self.balance_transaction(ute.transaction_rest)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"TRX{self.id}"


class Split(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='splits')
    amount = models.IntegerField()
    target_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='splits')
    commodity_rate = models.ForeignKey(CommodityRate,
                                       on_delete=models.CASCADE,
                                       related_name='splits',
                                       blank=True,
                                       null=True)

    def __str__(self):
        return f"SPLT{self.id} TRX{self.transaction_id}"
