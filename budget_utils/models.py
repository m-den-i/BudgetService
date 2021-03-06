from django.db import models


class InvariantMixin(models.Model):
    invariants = ()

    def save(self, *args, **kwargs):
        for invariant in self.invariants:
            invariant.is_active(model_object=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
