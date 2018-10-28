class UnbalancedTransactionException(Exception):
    transaction_rest = 0

    def __init__(self, transaction_rest):
        self.transaction_rest = transaction_rest


class UnknownCommodityRateException(Exception):
    pass


class TargetCommodityRateException(Exception):
    pass


class SourceCommodityRateException(Exception):
    pass


class MissingCommodityException(Exception):
    pass
