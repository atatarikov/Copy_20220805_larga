from django import forms

from .models import Counterparty, Contract, PaymentStages, Payment, SignActStages, Coasts, ExpenseItem


class CounterpartyForm(forms.ModelForm):
    tin = forms.CharField(max_length=12, label='ИНН', required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', }))
    iec = forms.CharField(max_length=9, label='КПП', required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', }))
    comment = forms.CharField(max_length=250, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))

    class Meta:
        model = Counterparty
        fields = ['name', 'tin', 'iec', 'comment', ]
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', })}


class ContractForm(forms.ModelForm):
    date = forms.DateField(label='Дата', required=False, widget=forms.DateInput(attrs={'class': 'form-control'}))
    number = forms.CharField(max_length=50, label='№ договора', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', }))
    comment = forms.CharField(max_length=250, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))
    sum = forms.DecimalField(max_digits=25, decimal_places=2, label='Сумма договора', localize=True, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', }))

    class Meta:
        model = Contract
        fields = ['title', 'counterparty', 'number', 'date', 'sum', 'be_nds', 'sum_with_nds', 'comment', 'days_for_payment', 'is_plan', 'is_border_contract', 'is_closed']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', }),
                   'counterparty': forms.Select(attrs={'class': 'form-control', }),
                   'is_plan': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   'is_border_contract': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   'sum_with_nds': forms.TextInput(attrs={'class': 'form-control', }),
                   'be_nds': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   'is_closed': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   }


class PlanPerForm(forms.Form):
    date_start = forms.DateField(label='Дата начала', widget=forms.DateInput(attrs={'class': 'form-control'}))
    date_stop = forms.DateField(label='Дата окончания', widget=forms.DateInput(attrs={'class': 'form-control'}))


class ContractFormList(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['is_closed']
        widgets = {
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-control', }),
        }


class PaymentStagesForm(forms.ModelForm):
    comment = forms.CharField(max_length=2000, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))

    def __init__(self, *args, **kwargs):
        super(PaymentStagesForm, self).__init__(*args, **kwargs)
        if 'contract' in self.initial.keys():
            self.fields['signActStages'].queryset = SignActStages.objects.filter(contract=self.initial['contract'])

    class Meta:
        model = PaymentStages
        fields = ['title', 'contract', "signActStages", 'date', 'sum', 'be_nds', 'sum_with_nds', 'comment', 'paymented']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', }),
                   'contract': forms.Select(attrs={'class': 'form-control', }),
                   "signActStages": forms.Select(attrs={"class": "form-control", }),
                   'date': forms.DateInput(attrs={'class': 'form-control', }),
                   'sum': forms.TextInput(attrs={'class': 'form-control', }),
                   'sum_with_nds': forms.TextInput(attrs={'class': 'form-control', }),
                   'be_nds': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   'paymented': forms.CheckboxInput(attrs={'class': 'form-control', }), }


class PaymentStagesFilterForm(forms.ModelForm):
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, label='Договор',
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = PaymentStages
        fields = ['contract', ]


class FinPlanFilterForm(forms.Form):
    is_closed = forms.BooleanField(required=False, label='Показать все договоры, включая закрытые',
                                   widget=forms.CheckboxInput(attrs={'class': 'form-control'}))


class ContractFilterForm(forms.Form):
    counterparty = forms.ModelChoiceField(queryset=Counterparty.objects.all(), required=False, label='Контрагент',
                                          widget=forms.Select(attrs={'class': 'form-control'}))


class PaymentFilterForm(forms.ModelForm):
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, label='Договор',
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Payment
        fields = ['contract', ]


class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        if 'counterparty' in self.initial.keys():
            self.fields['contract'].queryset = Contract.objects.filter(counterparty=self.initial['counterparty'])
        if 'contract' in self.initial.keys():
            self.fields['payment_stages'].queryset = PaymentStages.objects.filter(contract=self.initial['contract'])

    number = forms.CharField(max_length=50, label='№ п/п', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', }))
    comment = forms.CharField(max_length=250, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))
    payment_stages = forms.ModelChoiceField(queryset=PaymentStages.objects.all(), required=False, label='Этап оплаты',
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    counterparty = forms.ModelChoiceField(queryset=Counterparty.objects.all(), required=False, label='Контрагент',
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, label='Договор',
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(label='Дата оплаты', required=False, widget=forms.DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Payment
        fields = ['counterparty', 'contract', 'payment_stages', 'number', 'date', 'sum', 'be_nds', 'sum_with_nds', 'comment', ]
        widgets = {'sum': forms.TextInput(attrs={'class': 'form-control', }), 'sum_with_nds': forms.TextInput(attrs={'class': 'form-control', }), 'be_nds': forms.CheckboxInput(attrs={'class': 'form-control', }), }


class SignActStagesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SignActStagesForm, self).__init__(*args, **kwargs)
        if 'counterparty' in self.initial.keys():
            self.fields['contract'].queryset = Contract.objects.filter(counterparty=self.initial['counterparty'])

    comment = forms.CharField(max_length=2000, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))

    class Meta:
        model = SignActStages
        fields = ['title', "counterparty", 'contract', 'date', "days_for_payment", 'sum', 'be_nds', 'sum_with_nds', 'comment', 'signed']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', }),
                   'contract': forms.Select(attrs={'class': 'form-control', }),
                   "counterparty": forms.Select(attrs={"class": "form-control", }),
                   'date': forms.DateInput(attrs={'class': 'form-control', }),
                   'sum': forms.TextInput(attrs={'class': 'form-control', }),
                   'sum_with_nds': forms.TextInput(attrs={'class': 'form-control', }),
                   'be_nds': forms.CheckboxInput(attrs={'class': 'form-control', }),
                   'signed': forms.CheckboxInput(attrs={'class': 'form-control', }), }


class SignActStagesFilterForm(forms.ModelForm):
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, label='Договор',
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SignActStages
        fields = ['contract', ]


class CoastsForm(forms.ModelForm):
    comment = forms.CharField(max_length=2000, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))

    class Meta:
        model = Coasts
        fields = ['expense_item', "date_plan", 'sum_plan', "date_fact", 'sum_fact', 'is_payout', 'comment']
        widgets = {'expense_item': forms.Select(attrs={'class': 'form-control', }),
                   'date_plan': forms.DateInput(attrs={'class': 'form-control', }),
                   'date_fact': forms.DateInput(attrs={'class': 'form-control', }),
                   'sum_plan': forms.TextInput(attrs={'class': 'form-control', }),
                   'sum_fact': forms.TextInput(attrs={'class': 'form-control', }),
                   'is_payout': forms.CheckboxInput(attrs={'class': 'form-control', })}


class ExpenseItemForm(forms.ModelForm):
    comment = forms.CharField(max_length=2000, label='Комментарий', required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))

    class Meta:
        model = ExpenseItem
        fields = ['title', 'comment']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', })}
