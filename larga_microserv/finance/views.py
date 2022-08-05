from datetime import datetime, timedelta
import decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Case, When, Q, Value, Subquery

from .forms import CounterpartyForm, ContractForm, PaymentStagesForm, PaymentForm, PaymentStagesFilterForm, PaymentFilterForm, PlanPerForm,\
    ContractFilterForm, FinPlanFilterForm, SignActStagesForm, SignActStagesFilterForm, CoastsForm, ExpenseItemForm
from .models import Counterparty, Contract, PaymentStages, Payment, SignActStages, Coasts, ExpenseItem


def move_plan():
    import datetime
    today = datetime.datetime.today()
    today_format = today.strftime("%d/%m/%Y")
    first_day_this_month = datetime.datetime.today().replace(day=1)
    dt = datetime.timedelta(days=1)
    end_day_last_month = (first_day_this_month - dt)
    first_day_last_month = end_day_last_month.replace(day=1)
    first_day_last_month = first_day_last_month.strftime("%Y-%m-%d")
    end_day_last_month = end_day_last_month.strftime("%Y-%m-%d")

    # TODO удалить после проверки
    # cursor = connection.cursor()
    # query = 'SELECT finance_paymentstages.id from finance_paymentstages where (finance_paymentstages.date BETWEEN %s AND %s) AND finance_paymentstages.id not in (select payment_stages_id from finance_payment where payment_stages_id is not null)'  #
    # cursor.execute(query, (first_day_last_month, end_day_last_month))
    # qs = dictfetchall(cursor)

    qs = PaymentStages.objects.filter(Q(date__range=(first_day_last_month, end_day_last_month)), ~Q(id__in=Payment.objects.filter(payment_stages__isnull=False).values('payment_stages_id'))).values('id')

    for i in qs:
        obj = PaymentStages.objects.get(pk=i['id'])
        obj.comment += f'** {today_format} добавлен автоматический перенос даты в связи с неоплатой ** '
        obj.date += datetime.timedelta(weeks=4)
        obj.save()


@login_required(redirect_field_name='login')
def index(request):
    move_plan()
    today = datetime.today()
    mounth_int = int(today.strftime("%m"))
    data = []
    data_sum = {'sum_1': 0.00,
                'sum_2': 0.00,
                'sum_3': 0.00,
                'sum_4': 0.00,
                'sum_5': 0.00,
                'sum_6': 0.00,
                'sum_7': 0.00,
                'sum_8': 0.00,
                'sum_9': 0.00,
                'sum_10': 0.00,
                'sum_11': 0.00,
                'sum_12': 0.00,
                'sum_13': 0.00,
                'sum_14': 0.00,
                'sum_15': 0.00,
                'sum_1_': 0.00,
                'sum_2_': 0.00,
                'sum_3_': 0.00,
                'sum_4_': 0.00,
                'sum_5_': 0.00,
                'sum_6_': 0.00,
                'sum_7_': 0.00,
                'sum_8_': 0.00,
                'sum_9_': 0.00,
                'sum_10_': 0.00,
                'sum_11_': 0.00,
                'sum_12_': 0.00,
                'sum_13_': 0.00,
                'sum_14_': 0.00,
                'sum_15_': 0.00,
                'sum_contract_sum': 0.00,
                'sum_now': 0.00,
                'sum_next': 0.00,
                'sum_delta': 0.00,
                'sum_saldo': 0.00,
                }
    now = datetime.now()
    year_now = now.strftime("%Y")
    year_next = str(int(year_now) + 1)
    start_data_now = datetime.strptime(f"{year_now}-01-01", "%Y-%m-%d").date()
    end_data_now = datetime.strptime(f"{year_now}-12-31", "%Y-%m-%d").date()
    start_data_next = datetime.strptime(f"{year_next}-01-01", "%Y-%m-%d").date()
    end_data_next = datetime.strptime(f"{year_next}-12-31", "%Y-%m-%d").date()
# TODO Удалить после проверки
#     cursor = connection.cursor()
#     query_text = '''SELECT finance_paymentstages.contract_id AS contract_id,
#        finance_counterparty.name AS counterparty_name,
#        finance_contract.title AS contract_title,
#        CASE WHEN finance_contract.be_nds = True THEN finance_contract.sum_with_nds ELSE finance_contract.sum END AS contract_sum,
#        finance_contract.number AS contract_number,
#        finance_contract.date AS contract_date,
#        finance_contract.sum_incorrect AS contract_sum_incorrect
# FROM (SELECT DISTINCT finance_paymentstages.contract_id
#       FROM finance_paymentstages AS finance_paymentstages WHERE finance_paymentstages.date BETWEEN %s AND %s) AS finance_paymentstages
#          LEFT JOIN finance_contract AS finance_contract ON finance_paymentstages.contract_id = finance_contract.id
#          LEFT JOIN finance_counterparty AS finance_counterparty
#                    ON finance_contract.counterparty_id = finance_counterparty.id WHERE finance_contract.is_plan = %s and finance_contract.is_closed = FALSE'''
#     add_title_text = ' [только действующие]'
#     if request.method == 'POST':
#         if 'is_closed' in request.POST:
#             query_text = query_text.replace('finance_contract.is_plan = %s and finance_contract.is_closed = FALSE', 'finance_contract.is_plan = %s')
#             cursor.execute(query_text, (start_data_now, end_data_now, is_plan))
#             add_title_text = ' [по всем контрактам]'
#     cursor.execute(query_text, (start_data_now, end_data_now, is_plan))
    add_title_text = ' [только действующие]'
    qs1 = PaymentStages.objects.filter(date__range=(start_data_now, end_data_now)).values_list('contract_id')
    qs3 = Contract.objects.select_related('counterparty').filter(Q(is_plan=False), Q(is_closed=False), Q(id__in=Subquery(qs1)))
    if request.method == 'POST':
        if 'is_closed' in request.POST:
            qs3 = Contract.objects.select_related('counterparty').filter(Q(is_plan=False), Q(id__in=Subquery(qs1)))
            add_title_text = ' [по всем контрактам]'
    qs4 = qs3.annotate(contract_sum=Sum(Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum'))))
    for el in qs4:
        insert_data = {'counterparty': el.counterparty.name, 'contract': el.title, 'contract_number': el.number, 'sum_incorrect': el.sum_incorrect,
                       'contract_data': el.date.strftime("%Y-%M-%d"), 'contract_sum': el.contract_sum, 'now': get_full_payment(el.id), 'saldo': el.contract_sum - get_full_payment(el.id),
                       'next': get_paymentstages_next_year(el.id, start_data_next, end_data_next)}
        for i in range(1, 16):
            if (i > 12):
                return_data = get_payment_in_month(start_data_next, end_data_next, i - 12, el.id)
            else:
                return_data = get_payment_in_month(start_data_now, end_data_now, i, el.id)
            if not return_data == 0:
                insert_data[str(i)] = round(return_data['sum_fact'], 2)
                insert_data[str(i) + '_'] = round(return_data['sum_plan'], 2)
            else:
                insert_data[str(i)] = 0.00
                insert_data[str(i) + '_'] = 0.00
        data.append(insert_data)

    # TODO удалить после проверки
    # qs = dictfetchall(cursor)
    # for el in qs:
    #     insert_data = {'counterparty': el['counterparty_name'], 'contract': el['contract_title'],
    #                    'contract_number': el['contract_number'], 'sum_incorrect': el['contract_sum_incorrect'],
    #                    'contract_data': el['contract_date'].strftime("%Y-%M-%d"),
    #                    'contract_sum': el['contract_sum'], 'now': get_full_payment(el['contract_id']), 'saldo': el['contract_sum'] - get_full_payment(el['contract_id']),
    #                    'next': get_paymentstages_next_year(el['contract_id'], start_data_next, end_data_next)}
    #     for i in range(1, 16):
    #         if (i > 12):
    #             return_data = get_payment_in_month(start_data_next, end_data_next, i - 12, el['contract_id'])
    #         else:
    #             return_data = get_payment_in_month(start_data_now, end_data_now, i, el['contract_id'])
    #         if not return_data == 0:
    #             insert_data[str(i)] = round(return_data['sum_fact'], 2)
    #             insert_data[str(i) + '_'] = round(return_data['sum_plan'], 2)
    #         else:
    #             insert_data[str(i)] = 0.00
    #             insert_data[str(i) + '_'] = 0.00
    #     data.append(insert_data)
    # # print(data=data1)
    for el in data:
        for i in range(1, 16):
            key_plan = str(i) + '_'
            key_fact = str(i)
            if key_plan in el:
                data_sum['sum_' + key_plan] = round(data_sum['sum_' + key_plan] + float(el[str(i) + '_']), 2)
            if key_fact in el:
                data_sum['sum_' + key_fact] = round(data_sum['sum_' + key_fact] + float(el[str(i)]), 2)
            if i == mounth_int:
                data_sum['sum_delta'] = data_sum['sum_' + key_fact] - data_sum['sum_' + key_plan]
        if 'contract_sum' in el:
            data_sum['sum_contract_sum'] = round(data_sum['sum_contract_sum'] + float(el['contract_sum']), 2)
        if 'now' in el:
            data_sum['sum_now'] = round(data_sum['sum_now'] + float(el['now']), 2)
        if 'saldo' in el:
            data_sum['sum_saldo'] = round(data_sum['sum_saldo'] + float(el['saldo']), 2)
        if 'next' in el:
            data_sum['sum_next'] = round(data_sum['sum_next'] + float(el['next']), 2)

    #
    for i in range(1, 16):
        key_plan = str(i) + '_'
        key_fact = str(i)
        if i < mounth_int:
            data_sum['sum_' + key_plan] = ''
        elif i > mounth_int:
            data_sum['sum_' + key_fact] = data_sum['sum_' + key_plan]
            data_sum['sum_' + key_plan] = ''

    for i in data:
        for i1 in range(1, 16):
            key_plan = str(i1) + '_'
            key_fact = str(i1)
            if i1 < mounth_int:
                i[key_plan] = ''
                if i[key_fact] == 0.0:
                    i[key_fact] = ''
            elif i1 > mounth_int:
                if i[key_plan] == 0.0:
                    i[key_plan] = ''
                i[key_fact] = i[key_plan]
                i[key_plan] = ''
    return render(request, 'finance/index.html', {'data': data, 'add_title_text': add_title_text, 'form_filter': FinPlanFilterForm, 'data_sum': data_sum, 'mounth_int': mounth_int, 'title': 'Финансовый план', 'year_now': year_now, 'year_next': year_next, })


@login_required(redirect_field_name='login')
def plan(request):
    today = datetime.today()
    mounth_int = int(today.strftime("%m"))
    data = []
    data_sum = {'sum_1': 0.00,
                'sum_2': 0.00,
                'sum_3': 0.00,
                'sum_4': 0.00,
                'sum_5': 0.00,
                'sum_6': 0.00,
                'sum_7': 0.00,
                'sum_8': 0.00,
                'sum_9': 0.00,
                'sum_10': 0.00,
                'sum_11': 0.00,
                'sum_12': 0.00,
                'sum_13': 0.00,
                'sum_14': 0.00,
                'sum_15': 0.00,
                'sum_1_': 0.00,
                'sum_2_': 0.00,
                'sum_3_': 0.00,
                'sum_4_': 0.00,
                'sum_5_': 0.00,
                'sum_6_': 0.00,
                'sum_7_': 0.00,
                'sum_8_': 0.00,
                'sum_9_': 0.00,
                'sum_10_': 0.00,
                'sum_11_': 0.00,
                'sum_12_': 0.00,
                'sum_13_': 0.00,
                'sum_14_': 0.00,
                'sum_15_': 0.00,
                'sum_contract_sum': 0.00,
                'sum_now': 0.00,
                'sum_next': 0.00,
                'sum_delta': 0.00,
                'sum_saldo': 0.00,
                }
    now = datetime.now()
    year_now = now.strftime("%Y")
    year_next = str(int(year_now) + 1)
    start_data_now = datetime.strptime(f"{year_now}-01-01", "%Y-%m-%d").date()
    end_data_now = datetime.strptime(f"{year_now}-12-31", "%Y-%m-%d").date()
    start_data_next = datetime.strptime(f"{year_next}-01-01", "%Y-%m-%d").date()
    end_data_next = datetime.strptime(f"{year_next}-12-31", "%Y-%m-%d").date()
#     cursor = connection.cursor()
#     cursor.execute('''SELECT finance_paymentstages.contract_id AS contract_id,
#        finance_counterparty.name AS counterparty_name,
#        finance_contract.title AS contract_title,
#        CASE WHEN finance_contract.be_nds = True THEN finance_contract.sum_with_nds ELSE finance_contract.sum END AS contract_sum,
#        finance_contract.number AS contract_number,
#        finance_contract.date AS contract_date,
#        finance_contract.sum_incorrect AS contract_sum_incorrect
# FROM (SELECT DISTINCT finance_paymentstages.contract_id
#       FROM finance_paymentstages AS finance_paymentstages WHERE finance_paymentstages.date BETWEEN %s AND %s) AS finance_paymentstages
#          LEFT JOIN finance_contract AS finance_contract ON finance_paymentstages.contract_id = finance_contract.id
#          LEFT JOIN finance_counterparty AS finance_counterparty
#                    ON finance_contract.counterparty_id = finance_counterparty.id WHERE finance_contract.is_plan = %s''', (start_data_now, end_data_next, is_plan))
    qs1 = PaymentStages.objects.filter(date__range=(start_data_now, end_data_now)).values_list('contract_id')
    qs3 = Contract.objects.select_related('counterparty').filter(Q(is_plan=True), Q(id__in=Subquery(qs1)))
    qs4 = qs3.annotate(contract_sum=Sum(Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum'))))

    # qs = dictfetchall(cursor)
    # for el in qs:
    #     insert_data = {'counterparty': el['counterparty_name'], 'contract': el['contract_title'],
    #                    'contract_number': el['contract_number'], 'sum_incorrect': el['contract_sum_incorrect'],
    #                    'contract_data': el['contract_date'].strftime("%Y-%M-%d"),
    #                    'contract_sum': el['contract_sum'], 'now': get_full_payment(el['contract_id']), 'saldo': el['contract_sum'] - get_full_payment(el['contract_id']),
    #                    'next': get_paymentstages_next_year(el['contract_id'], start_data_next, end_data_next)}

    for el in qs4:
        insert_data = {'counterparty': el.counterparty.name, 'contract': el.title,
                       'contract_number': el.number, 'sum_incorrect': el.sum_incorrect,
                       'contract_data': el.date.strftime("%Y-%M-%d"),
                       'contract_sum': el.contract_sum, 'now': get_full_payment(el.id), 'saldo': el.contract_sum - get_full_payment(el.id),
                       'next': get_paymentstages_next_year(el.id, start_data_next, end_data_next)}
        for i in range(1, 16):
            if (i > 12):
                return_data = get_payment_in_month(start_data_next, end_data_next, i - 12, el.id)
            else:
                return_data = get_payment_in_month(start_data_now, end_data_now, i, el.id)
            if not return_data == 0:
                insert_data[str(i)] = round(return_data['sum_fact'], 2)
                insert_data[str(i) + '_'] = round(return_data['sum_plan'], 2)
            else:
                insert_data[str(i)] = 0.00
                insert_data[str(i) + '_'] = 0.00
        data.append(insert_data)
    for el in data:
        for i in range(1, 16):
            key_plan = str(i) + '_'
            key_fact = str(i)
            if key_plan in el:
                data_sum['sum_' + key_plan] = round(data_sum['sum_' + key_plan] + float(el[str(i) + '_']), 2)
            if key_fact in el:
                data_sum['sum_' + key_fact] = round(data_sum['sum_' + key_fact] + float(el[str(i)]), 2)
            if i == mounth_int:
                data_sum['sum_delta'] = data_sum['sum_' + key_fact] - data_sum['sum_' + key_plan]
        if 'contract_sum' in el:
            data_sum['sum_contract_sum'] = round(data_sum['sum_contract_sum'] + float(el['contract_sum']), 2)
        if 'now' in el:
            data_sum['sum_now'] = round(data_sum['sum_now'] + float(el['now']), 2)
        if 'saldo' in el:
            data_sum['sum_saldo'] = round(data_sum['sum_saldo'] + float(el['saldo']), 2)
        if 'next' in el:
            data_sum['sum_next'] = round(data_sum['sum_next'] + float(el['next']), 2)

    #
    for i in range(1, 16):
        key_plan = str(i) + '_'
        key_fact = str(i)
        if i < mounth_int:
            data_sum['sum_' + key_plan] = ''
        elif i > mounth_int:
            data_sum['sum_' + key_fact] = data_sum['sum_' + key_plan]
            data_sum['sum_' + key_plan] = ''

    for i in data:
        for i1 in range(1, 16):
            key_plan = str(i1) + '_'
            key_fact = str(i1)
            if i1 < mounth_int:
                i[key_plan] = ''
                if i[key_fact] == 0.0:
                    i[key_fact] = ''
            elif i1 > mounth_int:
                if i[key_plan] == 0.0:
                    i[key_plan] = ''
                i[key_fact] = i[key_plan]
                i[key_plan] = ''
    return render(request, 'finance/index.html', {'data': data, 'data_sum': data_sum, 'mounth_int': mounth_int, 'title': 'Воронка', 'add_title_text': '', 'year_now': year_now, 'year_next': year_next})


@login_required(redirect_field_name='login')
def plan_per(request):
    dates = []
    dates_f = []
    return_data = []
    sum_data = []
    sum_data_nac = []
    if request.method == 'POST':
        date_start = request.POST['date_start']
        date_start_f = datetime.strptime(f"{date_start}", "%Y-%m-%d").date()
        date_stop = request.POST['date_stop']
        date_stop_f = datetime.strptime(f"{date_stop}", "%Y-%m-%d").date()
        delta = date_stop_f - date_start_f

        if delta.days > 0:
            for i in range(delta.days + 1):
                dates.append(date_start_f + timedelta(i))
                dates_f.append((date_start_f + timedelta(i)).strftime("%d.%m.%y"))
                sum_data.append(0)
    # TODO удалить после проверка
    #         cursor = connection.cursor()
    #         cursor.execute('''
    #         SELECT finance_paymentstages.id AS id,
    #         finance_paymentstages.title AS paymentstages_title,
    #         finance_counterparty.name AS counterparty_name,
    #         finance_contract.title AS contract_title,
    #         finance_contract.number AS contract_number,
    #         finance_contract.date AS contract_date
    #         FROM finance_paymentstages AS finance_paymentstages
    #         LEFT JOIN finance_contract AS finance_contract ON finance_paymentstages.contract_id = finance_contract.id
    #         LEFT JOIN finance_counterparty AS finance_counterparty ON finance_contract.counterparty_id = finance_counterparty.id
    #                            WHERE finance_paymentstages.date BETWEEN %s AND %s AND finance_contract.is_plan = False ORDER BY
    # "finance_paymentstages"."title" ASC''',
    #                        (date_start, date_stop))

            qs1 = PaymentStages.objects.select_related('contract', 'contract__counterparty').filter(date__range=(date_start, date_stop)).filter(contract__is_plan=False)
            for el in qs1:
                iter_dict = {'paymentstages_title': el.title,
                             'counterparty_name': el.contract.counterparty.name,
                             'contract': el.contract.title + ' (' + el.contract.number + ' от ' + el.contract.date.strftime("%Y-%M-%d") + ')'}
                iter_sum_list = []
                for _date in dates:
                    sum_perem = 0
                    _qs = PaymentStages.objects.filter(pk=el.id, date=_date)
                    if _qs:
                        if _qs[0].be_nds:
                            sum_perem = _qs[0].sum_with_nds
                        else:
                            sum_perem = _qs[0].sum
                    iter_sum_list.append(sum_perem)

                    sum_data[len(iter_sum_list) - 1] += sum_perem

                iter_dict['sums'] = iter_sum_list
                return_data.append(iter_dict)

            # qs = dictfetchall(cursor)
            # for el in qs:
            #     iter_dict = {'paymentstages_title': el['paymentstages_title'],
            #                  'counterparty_name': el['counterparty_name'],
            #                  'contract': el['contract_title'] + ' (' + el['contract_number'] + ' от ' + el['contract_date'].strftime("%Y-%M-%d") + ')'}
            #     iter_sum_list = []
            #     for _date in dates:
            #         sum_perem = 0
            #         _qs = PaymentStages.objects.filter(pk=el['id'], date=_date)
            #         if _qs:
            #             if _qs[0].be_nds:
            #                 sum_perem = _qs[0].sum_with_nds
            #             else:
            #                 sum_perem = _qs[0].sum
            #         iter_sum_list.append(sum_perem)

            #         sum_data[len(iter_sum_list) - 1] += sum_perem

            #     iter_dict['sums'] = iter_sum_list
            #     return_data.append(iter_dict)
        nar_itog = 0
        for ind, znach in enumerate(sum_data):
            nar_itog += znach
            sum_data_nac.append(nar_itog)

    return render(request, 'finance/plan_per.html', {'form': PlanPerForm(), 'dates': dates_f, 'return_data': return_data, 'sum_list': sum_data, 'sum_list_nac': sum_data_nac})


@login_required(redirect_field_name='login')
def plan_act(request):

    def row_report(d_pay, project, payment_stages, expected_payments, coast, variance, progressive_total, comment):
        obj_row_report = {
            'd_pay': d_pay,
            'project': project,
            'payment_stages': payment_stages,
            'expected_payments': expected_payments,
            'coast': coast,
            'variance': variance,
            'progressive_total': progressive_total,
            'comment': comment}
        return obj_row_report

    date_last_pay = None
    total_start = []
    qs_payment_stages = []
    qs_coasts = []
    qs_coasts_is_payout = []
    report_body = []
    if request.method == 'POST':
        date_start = request.POST['date_start']
        date_start_f = datetime.strptime(f"{date_start}", "%Y-%m-%d").date()
        # находим дату последней выплаты меньше заданной
        qs_date_last_pay = Coasts.objects.filter(is_payout=True, date_plan__lte=date_start_f).order_by('-date_plan').first()
        if qs_date_last_pay is None:
            return render(request, 'finance/plan_act.html', {'form': PlanPerForm(), 'table': False})

        # итого накопительное начало отчета
        date_last_pay = qs_date_last_pay.date_plan
        payment_stages_sum_with_nds_aggr = PaymentStages.objects.filter(date__lte=date_last_pay).annotate(
            ps_sum=Case(
                When(Q(sum_with_nds__isnull=False) & ~Q(sum_with_nds=0), then=F('sum_with_nds')),
                When(be_nds=True, then=(F('sum') * decimal.Decimal('1.20'))),
                default=F('sum'))).aggregate(Sum('ps_sum'))

        coasts_sum_plan_aggr = Coasts.objects.filter(date_plan__lte=date_last_pay).aggregate(Sum('sum_plan'))
        # сторно на 21.07.2022
        Initial_balance = decimal.Decimal('56213761.99')
        total_start = payment_stages_sum_with_nds_aggr['ps_sum__sum'] - coasts_sum_plan_aggr['sum_plan__sum'] - Initial_balance

        qs_payment_stages = PaymentStages.objects.filter(date__gt=date_last_pay).select_related('contract', 'contract__counterparty').annotate(
            ps_sum=Case(
                When(Q(sum_with_nds__isnull=False) & ~Q(sum_with_nds=0), then=F('sum_with_nds')),
                When(be_nds=True, then=(F('sum') * decimal.Decimal('1.20'))),
                default=F('sum'))).order_by('date')
        qs_coasts = Coasts.objects.filter(date_plan__gt=date_last_pay).select_related('expense_item').order_by('date_plan')
        qs_coasts_is_payout = Coasts.objects.filter(is_payout=True, date_plan__gt=date_last_pay).order_by('date_plan')

        report_body = []
        # шапка
        # report_body.append(row_report('Дата оплаты', 'Проект', 'Платежный этап', 'Ожидаемые оплаты', 'Расходы', 'Сальдо', 'Нарастающий итог', 'Комментарий'))
        # прошлый итог
        report_body.append(row_report(date_last_pay, '-', '-', payment_stages_sum_with_nds_aggr['ps_sum__sum'], coasts_sum_plan_aggr['sum_plan__sum'], '-', total_start, 'сторно -56 213 761.99 на 21.07.2022'))

        idate_last_pay = date_last_pay
        ipayout_total = total_start
        for ipayout in qs_coasts_is_payout:
            payment = 0
            coast = 0
            variance = 0
            for ipstage in qs_payment_stages:
                if ipstage.date > idate_last_pay and ipstage.date <= ipayout.date_plan:
                    # оплаты
                    report_body.append(row_report(ipstage.date, ipstage.contract, ipstage.title, ipstage.ps_sum, '-', '-', '-', ipstage.comment))
                    payment += ipstage.ps_sum
            for icoast in qs_coasts:
                if icoast.date_plan > idate_last_pay and icoast.date_plan <= ipayout.date_plan:
                    # расходы
                    report_body.append(row_report(icoast.date_plan, '-', icoast.expense_item, '-', icoast.sum_plan, '-', '-', icoast.comment))
                    coast += icoast.sum_plan
            variance = payment - coast
            ipayout_total += variance
            # выплата
            report_body.append(row_report(ipayout.date_plan, 'Выплата', '-', payment, coast, variance, ipayout_total, '-'))
            idate_last_pay = ipayout.date_plan
        payment = 0
        coast = 0
        variance = 0
        for ipstage in qs_payment_stages:
            if ipstage.date > idate_last_pay:
                # оплаты после последней выплаты все
                report_body.append(row_report(ipstage.date, ipstage.contract, ipstage.title, ipstage.ps_sum, '-', '-', '-', ipstage.comment))
                payment += ipstage.ps_sum
        ipayout_total += payment
        # общий итог
        report_body.append(row_report('-', 'Итого', '-', payment, '-', '-', ipayout_total, '-'))

    return render(request, 'finance/plan_act.html', {'form': PlanPerForm(), 'table': True, 'report_body': report_body})


def get_payment_in_month(start_data_now, end_data_now, month_, contract_id):
    # TODO удалить после проверки
    # cursor = connection.cursor()
    # #     cursor.execute('''SELECT contract_id, SUM(sum_fact) AS sum_fact, SUM(sum_plan) AS sum_plan FROM
    # # (SELECT contract_id, SUM(sum) sum_fact, 0 AS sum_plan FROM finance_payment WHERE CAST(strftime('%m', date) AS integer) = %s AND date between %s AND %s GROUP BY contract_id
    # # UNION ALL
    # # SELECT contract_id, 0, SUM(sum) FROM finance_paymentstages WHERE CAST(strftime('%m', date) AS integer) = %s AND date between %s AND %s GROUP BY contract_id) GROUP BY contract_id
    # # ''', (month_, start_data_now, end_data_now, month_, start_data_now, end_data_now))
    # query = f'''SELECT contract_id, SUM(sum_fact) AS sum_fact, SUM(sum_plan) AS sum_plan FROM
    # (SELECT contract_id, SUM(CASE WHEN be_nds = True THEN sum_with_nds ELSE sum END) sum_fact, 0 AS sum_plan FROM finance_payment WHERE finance_payment.contract_id={contract_id} AND date_part('month',date) = {month_} AND date between '{start_data_now}' AND '{end_data_now}' GROUP BY contract_id
    # UNION ALL
    # SELECT contract_id, 0, SUM(CASE WHEN be_nds = True THEN sum_with_nds ELSE sum END) FROM finance_paymentstages WHERE finance_paymentstages.contract_id={contract_id} AND date_part('month',date) = {month_} AND date between '{start_data_now}' AND '{end_data_now}' GROUP BY contract_id) AS T GROUP BY contract_id
    # '''
    qs1 = Payment.objects.filter(Q(date__range=(start_data_now, end_data_now)), Q(contract_id=contract_id), Q(date__month=month_)).values('contract_id').annotate(sum_fact=Sum(Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum')))).annotate(sum_plan=Value(decimal.Decimal('0')))
    qs2 = PaymentStages.objects.filter(Q(date__range=(start_data_now, end_data_now)), Q(contract_id=contract_id), Q(date__month=month_)).annotate(sum_fact=Value(decimal.Decimal('0'))).values('contract_id', 'sum_fact').annotate(sum_plan=Sum(Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum'))))
    # FIXME
    # Не поддерживается annotate после union пример:
    # q4 = qs3.values_list('contract_id').annotate(sum_plan1=Sum('sum_plan1'), sum_plan=Sum('sum_plan'))
    qs3 = qs1.union(qs2, all=True)
    return_data1 = 0

    if len(qs3):
        return_data1 = {'contract_id': '', 'sum_fact': decimal.Decimal('0'), 'sum_plan': decimal.Decimal('0')}
        for iqs3 in qs3:
            return_data1['contract_id'] = iqs3['contract_id']
            if iqs3['sum_fact'] != 0:
                return_data1['sum_fact'] = decimal.Decimal(iqs3['sum_fact'])
            if iqs3['sum_plan'] != 0:
                return_data1['sum_plan'] = decimal.Decimal(iqs3['sum_plan'])
    return return_data1

    # TODO удалить после проверки
    # cursor.execute(query)
    # qs = dictfetchall(cursor)
    # return_data = 0
    # if len(qs):
    #     return_data = qs[0]
    #     print(return_data == return_data1)
    # return return_data


def get_full_payment(contract_id):
    # TODO удалить после проверки
    # cursor = connection.cursor()
    # query = f'''SELECT SUM(CASE WHEN be_nds = True THEN sum_with_nds ELSE sum END) sum FROM finance_payment WHERE contract_id = {contract_id} GROUP BY contract_id
    #     '''
    # cursor.execute(query)
    # qs = dictfetchall(cursor)
    qs = Payment.objects.filter(contract_id=contract_id).annotate(ps_sum=Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum'))).aggregate(sum=Sum('ps_sum'))
    return_data = 0
    if len(qs) and qs['sum']:
        return_data = round(qs['sum'], 2)
    return return_data


def get_paymentstages_next_year(contract_id, start_data_next, end_data_next):
    # TODO удалить после проверки
    # cursor = connection.cursor()
    # query = f'''SELECT SUM(CASE WHEN be_nds = True THEN sum_with_nds ELSE sum END) sum FROM finance_paymentstages WHERE contract_id = {contract_id} AND date between '{start_data_next}' AND '{end_data_next}' GROUP BY contract_id
    #     '''
    # cursor.execute(query)
    # qs = dictfetchall(cursor)
    qs = PaymentStages.objects.filter(date__range=(start_data_next, end_data_next), contract_id=contract_id).annotate(ps_sum=Case(When(be_nds=True, then=F('sum_with_nds')), default=F('sum'))).aggregate(sum=Sum('ps_sum'))
    return_data = 0
    if len(qs) and qs['sum']:
        return_data = round(qs['sum'], 2)
    return return_data


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


@login_required(redirect_field_name='login')
def default_list(request, object_name):
    objects_list = return_object_list(object_name, request)
    if False:
        # это данные заблюрить после загрузки в тествых базах
        for obj in objects_list:
            if getattr(obj, 'name', False):
                obj.name = f'{object_name} {obj.id}'
                if object_name == 'Counterparty':
                    obj.tin = (str(obj.id) * 12)[:12]
                    obj.iec = obj.tin[:9]
                obj.save()
            if getattr(obj, 'title', False):
                obj.title = f'{object_name} {obj.id}'
                obj.save()
    titles_list = get_full_data_about_object(object_name)['titles_list']
    fields_list = get_full_data_about_object(object_name)['fields_list']
    form_filter = get_full_data_about_object(object_name)['form_filter']
    if object_name == 'PaymentStages' or object_name == 'SignActStages':
        if request.method == 'POST':
            if request.POST['contract']:
                form_filter = form_filter(initial={'contract': Contract.objects.get(pk=request.POST['contract'])})
        if request.method == 'GET':
            if 'contract' in request.GET:
                form_filter = form_filter(initial={'contract': Contract.objects.get(pk=request.GET['contract'])})
    return render(request, 'finance/default_list.html',
                  {'title': get_full_data_about_object(object_name)['title_list'], 'objects_list': objects_list,
                   'table': create_table(get_full_data_about_object(object_name)['model'], object_name, objects_list, titles_list,
                                         fields_list), 'object': object_name,
                   'button_list': create_button_list(object_name, request), 'form_filter': form_filter})


def return_object_list(object_name, request):
    objects_list = ''
    if request.method == 'GET':
        if object_name == 'PaymentStages' or object_name == 'SignActStages':
            request_data = request.GET
            if 'contract' in request_data:
                if object_name == 'PaymentStages':
                    objects_list = PaymentStages.objects.filter(contract_id__exact=request_data['contract'])
                if object_name == 'SignActStages':
                    objects_list = SignActStages.objects.filter(contract_id__exact=request_data['contract'])
                return objects_list
    if request.method == 'POST':
        if object_name == 'PaymentStages':
            request_data = request.POST
            if request_data['contract']:
                objects_list = PaymentStages.objects.filter(contract_id__exact=request_data['contract'])
                return objects_list
        elif object_name == 'SignActStages':
            request_data = request.POST
            if request_data['contract']:
                objects_list = SignActStages.objects.filter(contract_id__exact=request_data['contract'])
                return objects_list
        elif object_name == 'Contract':
            request_data = request.POST
            if request_data['counterparty']:
                objects_list = Contract.objects.filter(counterparty_id__exact=request_data['counterparty'])
                return objects_list
        elif object_name == 'Payment':
            request_data = request.POST
            if request_data['contract']:
                objects_list = Payment.objects.filter(contract_id__exact=request_data['contract'])
                return objects_list
    objects_list = get_full_data_about_object(object_name)['model'].objects.all()
    return objects_list


@login_required(redirect_field_name='login')
def default_add(request, object_name):
    is_new = True
    error = ''
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('../default_list/' + str(object_name))
        else:
            form = get_full_data_about_object(object_name)['form'](request.POST)
            if form.is_valid():
                obj_ = form.save()
                if 'save_exit' in request.POST:
                    return redirect('../default_list/' + str(object_name))
                else:
                    return redirect('../default_edit/' + str(object_name) + '/' + str(obj_.id))
            else:
                error = 'Форма была заполнена неверно!'
    form = get_full_data_about_object(object_name)['form']()
    return render(request, 'finance/default_add_edit.html',
                  {'title': get_full_data_about_object(object_name)['title_add'], 'object': object_name, 'form': form,
                   'error': error, 'buttons_add_edit': create_button_add_edit(is_new, request, object_name, 1, None)})


@login_required(redirect_field_name='login')
def default_edit(request, object_name, id_obj):
    object_from_model = get_object_or_404(get_full_data_about_object(object_name)['model'], id=id_obj)
    error = ''
    is_new = False
    if request.method == 'POST':
        redirect_string = '../../' + get_url_redirect(object_name, id_obj)
        if 'delete' in request.POST:
            error = ''
            object_del = get_full_data_about_object(object_name)['model'].objects.filter(id__exact=id_obj)
            parent_model = get_full_data_about_object(object_name)['parent']
            if parent_model:
                field_object_ = get_full_data_about_object(object_name)['model']._meta.get_field(
                    parent_model[0].lower() + parent_model[1:])
                parent_id = field_object_.value_from_object(object_del[0])
            try:
                object_del.delete()
            except Exception:
                error = 'Нельзя удалить, поскольку есть связанные объекты!'
            if parent_model:
                get_full_data_about_object(object_name)['parent_model'].objects.get(id=parent_id).save()
            if len(error) == 0:
                return redirect(redirect_string)
        elif ('save' in request.POST) or ('save_exit' in request.POST):
            form = get_full_data_about_object(object_name)['form'](request.POST, instance=object_from_model)
            if form.is_valid():
                object_from_model = form.save(commit=False)
                object_from_model.save()
                if 'save_exit' in request.POST:
                    return redirect(redirect_string)
            else:
                error = 'Форма была заполнена неверно!'
    form = get_full_data_about_object(object_name)['form'](instance=object_from_model)
    return render(request, 'finance/default_add_edit.html', {
        'title': get_full_data_about_object(object_name)['title'] + str(get_title_edit(object_from_model, object_name)) + '"',
        'object': object_name, 'form': form, 'error': error,
        'buttons_add_edit': create_button_add_edit(is_new, request, object_name, 2, id_obj, True)})


def get_full_data_about_object(object_name):
    data_list = {}
    if object_name == 'Counterparty':
        data_list = {'model': Counterparty,
                     'form': CounterpartyForm,
                     'form_filter': '',
                     'title': 'КОНТРАГЕНТ "',
                     'title_add': 'НОВЫЙ КОНТРАГЕНТ',
                     'title_list': 'СПИСОК КОНТРАГЕНТОВ',
                     'titles_list': ['Наименование', 'ИНН', 'КПП'],
                     'fields_list': ['name', 'tin', 'iec'],
                     'key_fields_list': ['_no_', '_no_', '_no_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent_model': '',
                     'parent': '', }
    elif object_name == 'Contract':
        data_list = {'model': Contract,
                     'form': ContractForm,
                     'form_filter': ContractFilterForm,
                     'title': 'ДОГОВОР "',
                     'title_add': 'НОВЫЙ ДОГОВОР',
                     'title_list': 'СПИСОК ДОГОВОРОВ',
                     'titles_list': ['Наименование', 'Контрагент', 'Номер', 'Плановый контракт', 'От', 'Закрыт', 'Сумма'],
                     'fields_list': ['title', 'counterparty', 'number', 'is_plan', 'date', 'is_closed', 'sum'],
                     'key_fields_list': ['_no_', 'name', '_no_', '_b_', '_no_', '_b_', '_fd_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent': '', }
    elif object_name == 'PaymentStages' or object_name == 'Payment_stages':
        data_list = {'model': PaymentStages,
                     'form': PaymentStagesForm,
                     'form_filter': PaymentStagesFilterForm,
                     'title': 'ЭТАП ОПЛАТЫ ПО ДОГОВОРУ "',
                     'title_add': 'НОВЫЙ ЭТАП ОПЛАТЫ ПО ДОГОВОРУ',
                     'title_list': 'СПИСОК ЭТАПОВ ОПЛАТЫ ПО ДОГОВОРАМ',
                     'titles_list': ['Название', 'Договор', 'Этап актирования', 'Дата', 'Сумма', 'Сумма с НДС', 'Оплачен', 'Комментарий'],
                     'fields_list': ['title', 'contract', 'signActStages', 'date', 'sum', 'sum_with_nds', 'paymented', 'comment'],
                     'key_fields_list': ['_no_', 'title', 'title', '_no_', '_fd_', '_r_', '_b_', '_no_', ],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent': '', }
    elif object_name == 'Payment':
        data_list = {'model': Payment,
                     'form': PaymentForm,
                     'form_filter': PaymentFilterForm,
                     'title': 'ОПЛАТА "',
                     'title_add': 'НОВАЯ ОПЛАТА',
                     'title_list': 'СПИСОК ОПЛАТ',
                     'titles_list': ['Дата', 'Номер пл.поруч.', 'Контрагент', 'Договор', 'Этап оплаты', 'Сумма'],
                     'fields_list': ['date', 'number', 'counterparty', 'contract', 'payment_stages', 'sum'],
                     'key_fields_list': ['_no_', '_no_', 'name', 'title', 'title', '_fd_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent': '', }
    elif object_name == 'SignActStages':
        data_list = {'model': SignActStages,
                     'form': SignActStagesForm,
                     'form_filter': SignActStagesFilterForm,
                     'title': 'ЭТАП АКТИРОВАНИЯ ПО ДОГОВОРУ "',
                     'title_add': 'НОВЫЙ ЭТАП АКТИРОВАНИЯ ПО ДОГОВОРУ',
                     'title_list': 'СПИСОК ЭТАПОВ АКТИРОВАНИЯ ПО ДОГОВОРАМ',
                     'titles_list': ['Название', 'Договор', 'Дата', 'Сумма', 'Сумма с НДС', 'Подписан', 'Комментарий'],
                     'fields_list': ['title', 'contract', 'date', 'sum', 'sum_with_nds', 'signed', 'comment'],
                     'key_fields_list': ['_no_', 'title', '_no_', '_fd_', '_r_', '_b_', '_no_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent': '', }
    elif object_name == 'Coasts':
        data_list = {'model': Coasts,
                     'form': CoastsForm,
                     'form_filter': '',
                     'title': 'Документ расхода ДС "',
                     'title_add': 'НОВЫЙ ДОКУМЕНТ РАСХОДА ДС',
                     'title_list': 'СПИСОК ДОКУМЕНТОВ РАСХОДА ДС',
                     'titles_list': ['Плановая дата', 'Статья расхода', 'Плановая сумма', 'Фактическая дата', 'Фактическая сумма', 'Выплата-ориентир'],
                     'fields_list': ['date_plan', 'expense_item', 'sum_plan', 'date_fact', 'sum_fact', 'is_payout'],
                     'key_fields_list': ['_no_', 'title', '_fd_', '_no_', '_fd_', '_b_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent_model': '',
                     'parent': '', }
    elif object_name == 'Expense_item' or object_name == 'ExpenseItem':
        data_list = {'model': ExpenseItem,
                     'form': ExpenseItemForm,
                     'form_filter': '',
                     'title': 'Статья расхода ДС "',
                     'title_add': 'НОВАЯ СТАТЬЯ РАСХОДА ДС',
                     'title_list': 'СПИСОК СТАТЕЙ РАСХОДА ДС',
                     'titles_list': ['Наименование'],
                     'fields_list': ['title'],
                     'key_fields_list': ['_no_'],
                     'link_list': 'default_add',
                     'link_list_edit': 'default_edit',
                     'parent_model': '',
                     'parent': '', }
    return data_list


def create_table(model, object_name, objects_list, titles_list, fields_list):
    link_list = get_full_data_about_object(object_name)['link_list_edit']
    code_line = '''<table class="table table-striped">
    <thead>
    <tr>
      <th scope="col">#</th>'''
    for title_from_list in titles_list:
        code_line += '<th scope="col">' + title_from_list + '</th>'
    code_line += '''
     </tr>
  </thead>
  <tbody>'''
    i = 0
    for object_obj in objects_list:
        i += 1
        link_line = '<a href="../' + link_list + '/' + str(object_name) + '/' + str(object_obj.id) + '">'
        code_line += '''<tr>
  <th scope="row">''' + link_line + str(i) + '</a></th>'
        ii = 0
        for field_from_list in fields_list:
            try:
                field_object = model._meta.get_field(field_from_list)
                field_value = field_object.value_from_object(object_obj)
            except Exception:
                field_object = None
                field_value = None
            key_field_value = get_full_data_about_object(object_name)['key_fields_list'][ii]
            ii += 1
            if key_field_value == '_no_':
                if field_from_list == 'date' or field_from_list == 'sum':
                    code_line += '<td class="text-nowrap">' + link_line + str(field_value) + '</a></td>'
                else:
                    code_line += '<td>' + link_line + str(field_value) + '</a></td>'
                # code_line += '<td>' + link_line + str(field_value) + '</a></td>'
            elif key_field_value == '_fd_':
                code_line += '<td class="text-nowrap">' + link_line + return_correct_string(str(field_value)) + '</a></td>'
            elif key_field_value == '_b_':
                if field_value:
                    field_value = '&#10003;'
                else:
                    field_value = ''
                code_line += '<td>' + link_line + str(field_value) + '</a></td>'
            elif key_field_value == '_r_':
                code_line += '<td class="text-nowrap">' + link_line + return_result(object_name, field_from_list, object_obj.id) + '</a></td>'
            else:
                support_model = get_full_data_about_object(field_from_list[0:1].upper() + field_from_list[1:])['model']
                support_qs = support_model.objects.filter(id__exact=field_value)
                if support_qs.count():
                    support_object = support_qs[0]
                    field_object_ = support_model._meta.get_field(key_field_value)
                    field_value_ = field_object_.value_from_object(support_object)
                    code_line += '<td>' + link_line + str(field_value_) + '</a></td>'
                else:
                    code_line += '<td>' + link_line + '</a></td>'
        code_line += '</tr>'
    code_line += '</tbody></table>'
    return code_line


def create_button_list(object_name, request):
    link_list = get_full_data_about_object(object_name)['link_list']
    code_line = '<a href="../' + link_list + '/' + object_name + '" class="btn btn-success my-2 float-right" role="button">Добавить (+)</a>'
    return code_line


def copy(request, object_name, id_obj):
    # TODO через словарь
    if object_name == 'PaymentStages':
        current_object = PaymentStages.objects.get(pk=id_obj)
        current_object.pk = None
        current_object.save()
        return redirect('../../default_edit/' + str(object_name) + '/' + str(current_object.id))
    if object_name == 'Coasts':
        current_object = Coasts.objects.get(pk=id_obj)
        current_object.pk = None
        current_object.save()
        return redirect('../../default_edit/' + str(object_name) + '/' + str(current_object.id))


def create_button_add_edit(is_new, request, object_name, i, id_obj, delete=False, add_string=False):
    code_line = '<a href = "'
    for i in range(i):
        code_line += '../'
    code_line += get_url_redirect(object_name, id_obj) + '" class ="btn btn-info my-2" role="button">Отменить</a>'
    if add_string:
        code_line += '''
        <button name = \'add_string\' type = "submit" class ="btn btn-secondary">Добавить строку</button>'''
    if not is_new and object_name == 'PaymentStages':
        code_line += f'''
        <a href = "../../copy/PaymentStages/{id_obj}" class ="btn btn-info my-2" role="button">Копировать</a>'''
    # TODO дублирование кнопки копировать
    if not is_new and object_name == 'Coasts':
        code_line += f'''
        <a href = "../../copy/Coasts/{id_obj}" class ="btn btn-info my-2" role="button">Копировать</a>'''
    code_line += '''
    <button name = \'save\' type = "submit" class ="btn btn-success">Сохранить</button>'''
    code_line += '''
        <button name = \'save_exit\' type = "submit" class ="btn btn-success">Сохранить и выйти</button>'''
    if delete:
        code_line += '''
        <button name = \'delete\' type = "submit" class ="btn btn-danger">Удалить</button>'''
    code_line += '''
    <button name = \'print\' class ="btn btn-warning" onClick="window.print()">Печать в PDF</button>'''
    return code_line


def get_title_edit(object_obj, object_name):
    # FIXME тут бы тоже как-то переделать
    if object_name == 'Contract' or object_name == 'PaymentStages' or object_name == 'SignActStages' or object_name == 'ExpenseItem':
        return object_obj.title
    elif object_name == 'Counterparty':
        return object_obj.name
    elif object_name == 'Coasts':
        return f'{object_obj.expense_item.title} от {object_obj.date_plan}'
    elif object_name == 'Payment':
        return_data = " №" + str(object_obj.number) + " от " + str(object_obj.date)
        if object_obj.payment_stages:
            return return_data + "[" + str(object_obj.payment_stages.title) + "]"


def get_url_redirect(object_name, id_obj):
    if object_name == 'PaymentStages' and id_obj:
        object_ps = PaymentStages.objects.get(pk=id_obj)
        # return 'point_edit/Point/' + str(object_point.point.id)
        return 'default_list/' + str(object_name) + '?contract=' + str(object_ps.contract.id)
    elif object_name == 'SignActStages' and id_obj:
        object_ps = SignActStages.objects.get(pk=id_obj)
        # return 'point_edit/Point/' + str(object_point.point.id)
        return 'default_list/' + str(object_name) + '?contract=' + str(object_ps.contract.id)
    else:
        return 'default_list/' + str(object_name)


def return_correct_string(string_integer):
    sum_1 = string_integer[-3:]
    reversed_string = string_integer[-4::-1]
    sum_2 = ' '.join([reversed_string[i:i + 3] for i in range(0, len(reversed_string), 3)])
    reversed_string_2 = sum_2[::-1]
    return str(reversed_string_2) + str(sum_1)


def return_result(object_name, field_from_list, object_id):
    # ??? Какие варианты оптимизаци этого есть?
    return_data = 0
    if object_name == 'PaymentStages':
        if field_from_list == 'sum_with_nds':
            obj = PaymentStages.objects.get(pk=object_id)
            if obj.be_nds:
                return_data = obj.sum_with_nds
            else:
                return_data = obj.sum
    elif object_name == 'SignActStages':
        if field_from_list == 'sum_with_nds':
            obj = SignActStages.objects.get(pk=object_id)
            if obj.be_nds:
                return_data = obj.sum_with_nds
            else:
                return_data = obj.sum
    return return_correct_string(str(round(return_data, 2)))
