from django.contrib import admin

# Register your models here.
from django.db.models import QuerySet

from .models import Contract, Counterparty, PaymentStages, SignActStages, Payment, Coasts, ExpenseItem
from datetime import date


class FilterSumWithNds(admin.SimpleListFilter):
    title = 'Фильтр по сумме (с НДС)'
    parameter_name = 'sum_with_tax'

    def lookups(self, request, model_contract):
        return [
            ('<1м', '< 1 млн.'),
            ('>от1до10м', '1-10 млн.'),
            ('больше10м', '> 10 млн.'),
            ('не заполнено', 'не заполнено')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<1м':
            return queryset.filter(sum_with_nds__lt=1000000)
        if self.value() == '>от1до10м':
            return queryset.filter(sum_with_nds__gte=1000000).filter(sum_with_nds__lt=10000000)
        if self.value() == 'больше10м':
            return queryset.filter(sum_with_nds__gte=10000000)
        if self.value() == 'не заполнено':
            return queryset.filter(sum_with_nds__isnull=True)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'counterparty', 'sum_with_nds', 'is_closed', 'date', 'days_from_beginning']
    list_editable = ['sum_with_nds', 'is_closed', 'date']
    ordering = ['sum_with_nds', 'title']
    list_per_page = 12
    search_fields = ['title']
    list_filter = ['is_closed', FilterSumWithNds]
    actions = ['set_is_closed_true']

    @admin.display(description='от тек.даты')
    def days_from_beginning(self, contract: Contract):
        if contract.date:
            return (date.today() - contract.date).days
        else:
            return None

    @admin.action(description='Закрыть выбранные Договоры')
    def set_is_closed_true(self, request, qs: QuerySet):
        qs.update(is_closed=True)


admin.site.register(Counterparty)
admin.site.register(PaymentStages)
admin.site.register(SignActStages)
admin.site.register(Payment)
admin.site.register(Coasts)
admin.site.register(ExpenseItem)
