class UnbalancedTransactionException(Exception):
    transaction_rest = 0

    def __init__(self, transaction_rest):
        self.transaction_rest = 0
