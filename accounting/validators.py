from django.db.models import Sum

from accounting.exceptions import UnbalancedTransactionException
from budget_utils.validators import Invariant


class BalancedTransaction(Invariant):
    def is_active(self, model_object):
        transaction_rest = model_object.splits.all().aggregate(transaction_sum=Sum('amount'))['transaction_sum']
        if transaction_rest:
            raise UnbalancedTransactionException(transaction_rest)
