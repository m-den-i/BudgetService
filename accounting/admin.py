from django.contrib import admin
from django.db import transaction
from mptt.admin import DraggableMPTTAdmin

from .models import (
    Account,
    Book,
    Commodity,
    CommodityRate,
    Location,
    Transaction,
    Split,
)


class AccountAdmin(DraggableMPTTAdmin):
    list_display = ('name', 'description', 'commodity', 'abstract',
                    'tree_actions', 'indented_title')
    list_display_links = ('indented_title',)


class BookAdmin(admin.ModelAdmin):
    list_display = ('owner', 'root_account')


class CommodityAdmin(admin.ModelAdmin):
    list_display = ('commodity_type', 'mnemonic', 'fraction')


class CommodityRateAdmin(admin.ModelAdmin):
    list_display = ('basic_commodity', 'rate', 'rate_commodity')


class SplitInlineAdmin(admin.TabularInline):
    model = Split


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('commodity', 'description', 'author')
    inlines = (SplitInlineAdmin,)

    def save_related(self, request, form, formsets, change):
        transaction.on_commit(form.instance.save)
        return super().save_related(request, form, formsets, change)


admin.site.register(Account, AccountAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Commodity, CommodityAdmin)
admin.site.register(CommodityRate, CommodityRateAdmin)
admin.site.register(Location)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Split)
