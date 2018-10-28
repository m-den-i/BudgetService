from accounting.exceptions import UnbalancedTransactionException, UnknownCommodityRateException, \
    TargetCommodityRateException, SourceCommodityRateException, MissingCommodityException
from budget_utils.validators import Invariant


class BalancedTransaction(Invariant):
    def is_active(self, model_object):
        transaction_rest = 0
        for split in model_object.splits.select_related('target_account', 'commodity_rate').all():
            # Split is allowed to be free of commodity rates if target account have the same commodity
            # as split's transaction. In that way we consider split with 1:1 rate.
            if model_object.commodity_id != split.target_account.commodity_id:
                # If target account has another commodity, check that split has rate and ends of rate are right.
                if split.commodity_rate is None:
                    raise UnknownCommodityRateException()
                elif split.commodity_rate.rate_commodity_id != split.target_account.commodity_id:
                    raise TargetCommodityRateException()
                elif split.commodity_rate.basic_commodity_id != model_object.commodity_id:
                    raise SourceCommodityRateException()
            print(split.amount)
            transaction_rest += split.amount
        print('=============')
        if transaction_rest:
            raise UnbalancedTransactionException(transaction_rest)


class NonAbstractShouldHaveCommodity(Invariant):
    def is_active(self, model_object):
        if not model_object.abstract and not model_object.commodity_id:
            print(model_object.__dict__)
            raise MissingCommodityException()


class RootIsAbstract(Invariant):
    def is_active(self, model_object):
        if model_object.is_root_node() and not model_object.abstract:
            model_object.abstract = True
