class Invariant(object):
    def is_active(self, model_object):
        raise NotImplementedError()


class CreateOnlyInvariant(Invariant):
    def is_active(self, model_object):
        if model_object.id:
            raise CannotChangeObjectException()
