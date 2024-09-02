from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from datetime import timedelta
from .forms import HistoryRecordForm,TransferRecordForm
import decimal
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout
from django.contrib import messages


#注册
def register(request):
    if request.method == 'GET':
        return render(request, 'basic/register.html')

    elif request.method == 'POST':
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        pwd = request.POST.get('password', '')

        if User.objects.filter(username=user_name).exists():
            # 用户已存在，返回注册页面并显示提示
            return render(request, 'accounting/login.html', {'exists': True, 'show_register': True})

        nor_user = NormalUser(name=user_name)
        nor_user.save()
        user = User.objects.create_user(username=user_name, password=pwd, email=email)
        user.save()

        # 注册成功，返回登录页面并显示提示
        return render(request, 'accounting/login.html', {'success': True, 'show_login': True})

    return JsonResponse({'code': 403, 'msg': '被禁止的请求'})


from .models import *
def index(request):
    if request.user.is_authenticated:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        today = datetime.date.today()
        cur_user = NormalUser.objects.filter(name=request.user)[0]
        all_accounts = Account.objects.filter(owner=cur_user)
        currencies = Currency.objects.all()
        # history_records = HistoryRecord.objects.filter(username=cur_user ,time_of_occurrence__year=today.year, time_of_occurrence__month=today.month).order_by("-time_of_occurrence")
        # transfer_records = TransferRecord.objects.filter(username=cur_user ,time_of_occurrence__year=today.year,time_of_occurrence__month=today.month).order_by("-time_of_occurrence")
        history_records = HistoryRecord.objects.filter(
            username=cur_user,
            time_of_occurrence__gte=thirty_days_ago
        ).order_by("-time_of_occurrence")
        transfer_records = TransferRecord.objects.filter(
            username=cur_user,
            time_of_occurrence__gte=thirty_days_ago
        ).order_by("-time_of_occurrence")
        ie_types = Category.CATEGORY_TYPES

        income = 0
        expense = 0
        day_has_record = []
        current_month_records = {}
        day_income_expense = {}

        for hr in history_records:
            if hr.category.category_type.lower() == "expense":
                expense -= hr.amount
            elif hr.category.category_type.lower() == "income":
                income += hr.amount
            day_occur = hr.time_of_occurrence.strftime("%Y-%m-%d %A")
            if day_occur not in day_has_record:
                day_has_record.append(day_occur)
                current_month_records[day_occur] = [hr]
                day_income_expense[day_occur] = {"income": 0, "expense": 0}
                if hr.category.category_type.lower() == "expense":
                    day_income_expense[day_occur]["expense"] += hr.amount
                elif hr.category.category_type.lower() == "income":
                    day_income_expense[day_occur]["income"] += hr.amount
            else:
                current_month_records[day_occur].append(hr)
                if hr.category.category_type.lower() == "expense":
                    day_income_expense[day_occur]["expense"] += hr.amount
                elif hr.category.category_type.lower() == "income":
                    day_income_expense[day_occur]["income"] += hr.amount
        day_has_record.sort(reverse=True)

        for tr in transfer_records:
            day_occur = tr.time_of_occurrence.strftime("%Y-%m-%d %A")
            if day_occur not in day_has_record:
                day_has_record.append(day_occur)
                current_month_records[day_occur] = [tr]
                day_income_expense[day_occur] = {"income": 0, "expense": 0}
            else:
                current_month_records[day_occur].append(tr)
        day_has_record.sort(reverse=True)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>分析数据获取<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        food_category_name = "饮食"

        # 获取收入和支出类别的所有记录
        income_records = HistoryRecord.objects.filter(category__category_type="income")
        expense_records = HistoryRecord.objects.filter(category__category_type="expense")

        # 获取总收入金额
        total_income = income_records.aggregate(total=Sum('amount'))['total'] or 0

        # 获取总支出金额
        total_expense = expense_records.aggregate(total=Sum('amount'))['total'] or 0

        # 获取饮食类别的所有支出记录
        food_expense_records = expense_records.filter(
	        Q(category__name=food_category_name) | Q(sub_category__parent__name=food_category_name)
        )

        # 获取饮食支出的总金额
        food_expense_total = food_expense_records.aggregate(total=Sum('amount'))['total'] or 0

        # 计算饮食支出占总支出的比例
        if total_expense > 0:
	        food_expense_ratio = (food_expense_total / total_expense) * 100
        else:
	        food_expense_ratio = 0

        # 计算结余或赤字
        balance = total_income - total_expense
        if balance > 0:
	        suggestion = f"你的收入大于支出，结余金额为：{balance:.2f}元。建议你继续保持储蓄习惯。"
        else:
	        suggestion = f"你的支出大于收入，赤字金额为：{abs(balance):.2f}元。建议你控制支出。"

        # 生活质量评估
        if food_expense_ratio > 60:
	        quality_evaluation = "生活品质较差"
        elif 50 < food_expense_ratio <= 60:
	        quality_evaluation = "生活品质一般"
        elif 40 < food_expense_ratio <= 50:
	        quality_evaluation = "生活品质较好"
        else:
	        quality_evaluation = "生活品质优秀"
        car_loan_category_name = "车贷"
        house_loan_category_name = "房贷"
        investment_category_name = "理财"

        # 获取车贷和房贷的支出记录
        car_loan_expense_records = expense_records.filter(
	        Q(category__name=car_loan_category_name) | Q(sub_category__parent__name=car_loan_category_name)
        )
        house_loan_expense_records = expense_records.filter(
	        Q(category__name=house_loan_category_name) | Q(sub_category__parent__name=house_loan_category_name)
        )

        # 获取车贷和房贷的总支出金额
        car_loan_expense_total = car_loan_expense_records.aggregate(total=Sum('amount'))['total'] or 0
        house_loan_expense_total = house_loan_expense_records.aggregate(total=Sum('amount'))['total'] or 0

        # 获取理财产品投资记录
        investment_records = HistoryRecord.objects.filter(
	        Q(category__name=investment_category_name) | Q(sub_category__parent__name=investment_category_name)
        )

        # 获取理财产品投资的总金额
        investment_total = investment_records.aggregate(total=Sum('amount'))['total'] or 0

        # 计算车贷、房贷支出占总支出的比例
        if total_expense > 0:
	        car_loan_ratio = (car_loan_expense_total / total_expense) * 100
	        house_loan_ratio = (house_loan_expense_total / total_expense) * 100
        else:
	        car_loan_ratio = 0
	        house_loan_ratio = 0

        context = {
            'transfer_records': transfer_records,
            'accounts': all_accounts,
            'currencies': currencies,
            'ie_types': ie_types,
            'day_has_record': day_has_record,
            'history_records': history_records,
            'current_month_income': income,
            'current_month_expense': expense,
            'surplus': income + expense,
            'current_month_records': current_month_records,
            'day_income_expense': day_income_expense,
	        'food_expense_ratio': f"{food_expense_ratio:.2f}%",
	        'quality_evaluation': quality_evaluation,
	        'suggestion': suggestion,
	        'car_loan_ratio': f"{car_loan_ratio:.2f}%",
	        'house_loan_ratio': f"{house_loan_ratio:.2f}%",
	        'investment_total': f"{investment_total:.2f}",
        }
        return render(request, 'accounting/index.html', context)
    else:
        return render(request, 'accounting/index.html')

def transfer_between_accounts(request):
    pass

def retrieve_category(request):
    if request.user.is_authenticated:
        ie_type = request.POST.get('ie_type')
        categories = Category.objects.filter(category_type=ie_type)
        category_list = []
        for c in categories:
            category_list.append((c.id, c.name))
        # return HttpResponse(f'{"categories": {categories}}', content_type='application/json')
        return JsonResponse({"categories": category_list})
    else:
        return JsonResponse({"error": "unauthenticated"})

def retrieve_subcategory(request):
    if request.user.is_authenticated:
        category_type = request.POST.get('category_type')
        current_category = Category.objects.filter(name=category_type)[0]
        subcategories = SubCategory.objects.filter(parent=current_category)
        subcategory_list = []
        for sc in subcategories:
            subcategory_list.append((sc.id, sc.name))
        return JsonResponse({"subcategories": subcategory_list})
    else:
        return JsonResponse({"error": "unauthenticated"})

def record_income_expense(request):
    if request.user.is_authenticated:
        sub_category = request.POST.get('sub_category')
        time_now = timezone.now()
        # print(request.user)
        if sub_category == "select value":
            try:
                username = NormalUser.objects.filter(name=request.user)[0]
                account = request.POST.get('account')
                category = request.POST.get('category')
                currency = request.POST.get('currency')
                amount = request.POST.get('amount')
                comment = request.POST.get('comment')
                time_occur = request.POST.get('time_of_occurrence')
                history_record = HistoryRecord(username=username,
                                               account_id=account,
                                               category_id=category,
                                               currency_id=currency,
                                               amount=amount,
                                               comment=comment,
                                               time_of_occurrence=time_occur,
                                               created_date=time_now,
                                               updated_date=time_now
                                               )
                history_record.save()
                current_account = Account.objects.filter(id=account)[0]
                current_ie_type = Category.objects.filter(id=category)[0].category_type
                if current_ie_type.lower() == "expense":
                    current_account.amount -= decimal.Decimal(amount)
                elif current_ie_type.lower() == "income":
                    current_account.amount += decimal.Decimal(amount)
                current_account.save()
            except Exception as e:
                print("not valid in request with error: %s" % str(e))
        else:
            form = HistoryRecordForm(request.POST)
            if form.is_valid():
                username = NormalUser.objects.filter(name=request.user)[0]
                account = form.cleaned_data['account']
                category = form.cleaned_data['category']
                sub_category = form.cleaned_data['sub_category']
                currency = form.cleaned_data['currency']
                amount = form.cleaned_data['amount']
                comment = form.cleaned_data['comment']
                time_occur = form.cleaned_data['time_of_occurrence']
                history_record = HistoryRecord(username=username,
                                               account=account,
                                               category=category,
                                               sub_category=sub_category,
                                               currency=currency,
                                               amount=amount,
                                               comment=comment,
                                               time_of_occurrence=time_occur,
                                               created_date=time_now,
                                               updated_date=time_now
                                               )
                history_record.save()
                current_ie_type = category.category_type
                if current_ie_type.lower() == "expense":
                    account.amount -= decimal.Decimal(amount)
                elif current_ie_type.lower() == "income":
                    account.amount += decimal.Decimal(amount)
                account.save()
            else:
                print("not valid in form")
        return redirect(index)
    else:
        return JsonResponse({"error": "unauthenticated"})

def login(request):
    return  render(request, 'accounting/login.html')

#图表
from django.shortcuts import render
from .models import HistoryRecord, Category
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def charts_view(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)

    # 获取收入和支出类别
    income_category_ids = Category.objects.filter(category_type="income").values_list('id', flat=True)
    expense_category_ids = Category.objects.filter(category_type="expense").values_list('id', flat=True)

    # 查询收入记录
    income_records = HistoryRecord.objects.filter(
        category_id__in=income_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    # 查询支出记录
    expense_records = HistoryRecord.objects.filter(
        category_id__in=expense_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    # 准备折线图数据，将 Decimal 转换为 float
    income_dates = [record['time_of_occurrence__date'].strftime('%Y-%m-%d') for record in income_records]
    income_values = [float(record['total_amount']) for record in income_records]

    expense_dates = [record['time_of_occurrence__date'].strftime('%Y-%m-%d') for record in expense_records]
    expense_values = [float(record['total_amount']) for record in expense_records]

    # 准备饼状图数据，将 Decimal 转换为 float
    income_pie_data = HistoryRecord.objects.filter(
        category_id__in=income_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount'))

    expense_pie_data = HistoryRecord.objects.filter(
        category_id__in=expense_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount'))

    income_pie = [
        {'name': record['category__name'], 'value': float(record['total_amount'])}
        for record in income_pie_data
    ]

    expense_pie = [
        {'name': record['category__name'], 'value': float(record['total_amount'])}
        for record in expense_pie_data
    ]

    context = {
        'income_dates': income_dates,
        'income_values': income_values,
        'expense_dates': expense_dates,
        'expense_values': expense_values,
        'income_pie': income_pie,
        'expense_pie': expense_pie,
    }

    return render(request, 'accounting/charts.html', context)


    #登录
def login_in(request):
    if request.method == 'GET':
        return render(request, 'accounting/login.html')

    elif request.method == 'POST':
        user_name = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(username=user_name, password=pwd)

        if user:
            if user.is_active:
                auth_login(request, user)
                return redirect('/accounting/')
            else:
                return render(request, 'accounting/login.html', {'login_failed': True, 'msg': '用户未激活'})
        else:
            # 设置错误消息，并返回登录页面
            return render(request, 'accounting/login.html', {'login_failed': True, 'msg': '账户名或密码错误，请重新登录'})

    # 处理其他请求方法
    return JsonResponse({'code': 405, 'msg': '方法不允许'}, status=405)


def logout_(request):
	logout(request)
	return redirect('/accounting/login')

def retrieve_year_has_data(request):
    if request.user.is_authenticated:
        hr_first = HistoryRecord.objects.order_by("time_of_occurrence").first()
        hr_last = HistoryRecord.objects.order_by("time_of_occurrence").last()
        year_list = [y for y in range(hr_last.time_of_occurrence.year, hr_first.time_of_occurrence.year-1, -1)]
        return JsonResponse({"years": year_list})
    else:
        return JsonResponse({"error": "unauthenticated"})


def retrieve_month_has_data(request):
    if request.user.is_authenticated:
        year = request.POST.get('year')
        hr = HistoryRecord.objects.filter(time_of_occurrence__year=year).order_by("time_of_occurrence")
        hr_first = hr.first()
        hr_last = hr.last()
        month_list = [m for m in range(hr_last.time_of_occurrence.month, hr_first.time_of_occurrence.month-1, -1)]
        return JsonResponse({"months": month_list})
    else:
        return JsonResponse({"error": "unauthenticated"})

def filter_record_by_date(request):
    if request.user.is_authenticated:
        post_year = request.POST.get('year')
        post_month = request.POST.get('month')
        username = NormalUser.objects.filter(name=request.user)[0]
        history_records = HistoryRecord.objects.filter(username=username, time_of_occurrence__year=post_year, time_of_occurrence__month=post_month).order_by("-time_of_occurrence")
        transfer_records = TransferRecord.objects.filter(username=username, time_of_occurrence__year=post_year, time_of_occurrence__month=post_month).order_by("-time_of_occurrence")
        day_has_record = []
        custom_month_records = {}
        for hr in history_records:
            day_occur = hr.time_of_occurrence.strftime("%Y-%m-%d %A")
            if hr.sub_category:
                sub_category = hr.sub_category.name
            else:
                sub_category = "no sub category"
            if hr.comment:
                comment = hr.comment
            else:
                comment = ""
            new_hr = {
                "category": hr.category.name,
                "subcategory": sub_category,
                "amount": hr.amount,
                "comment": comment,
                "account": hr.account.name,
                "ie_type": hr.category.category_type.lower(),
                "record_type": "income_expense"
            }
            if day_occur not in day_has_record:
                day_has_record.append(day_occur)
                custom_month_records[day_occur] = [new_hr]
            else:
                custom_month_records[day_occur].append(new_hr)
        for tr in transfer_records:
            day_occur = tr.time_of_occurrence.strftime("%Y-%m-%d %A")
            if tr.comment:
                comment = tr.comment
            else:
                comment = ""
            new_tr = {
                "amount": tr.amount,
                "comment": comment,
                "from_account": tr.from_account.name,
                "to_account": tr.to_account.name,
                "record_type": "transfer"
            }
            if day_occur not in day_has_record:
                day_has_record.append(day_occur)
                custom_month_records[day_occur] = [new_tr]
            else:
                custom_month_records[day_occur].append(new_tr)
        return JsonResponse({'day_has_record': day_has_record, "records": custom_month_records})
    else:
        return JsonResponse({"error": "unauthenticated"})

def transfer_between_accounts(request):
    if request.user.is_authenticated:
        time_now = timezone.now()
        form = TransferRecordForm(request.POST)
        if form.is_valid():
            username = NormalUser.objects.filter(name=request.user)[0]
            from_account = form.cleaned_data['from_account']
            to_account = form.cleaned_data['to_account']
            if from_account != to_account:
                transfer_amount = form.cleaned_data['amount']
                transfer_comment = form.cleaned_data['comment']
                time_occur = form.cleaned_data['time_of_occurrence']
                transfer_record = TransferRecord(username=username,
                                                 from_account=from_account,
                                                 to_account=to_account,
                                                 amount=transfer_amount,
                                                 comment=transfer_comment,
                                                 time_of_occurrence=time_occur,
                                                 created_date=time_now,
                                                 updated_date=time_now
                                                 )
                transfer_record.save()
                from_account.amount -= decimal.Decimal(transfer_amount)
                from_account.save()
                to_account.amount += decimal.Decimal(transfer_amount)
                to_account.save()
            else:
                print("WARNING: You are transferring money amount between the same account!")
        return redirect(index)
    else:
        return JsonResponse({"error": "unauthenticated"})

def search_record(request):
    if request.user.is_authenticated:
        username = NormalUser.objects.filter(name=request.user)[0]
        keyword = request.POST.get('keyword')
        categories = Category.objects.filter(name__icontains=keyword)
        subcategories = SubCategory.objects.filter(name__icontains=keyword)
        hrs = HistoryRecord.objects.filter(username=username).filter(Q(category__in=categories) | Q(sub_category__in=subcategories) | Q(comment__icontains=keyword) | Q(amount__icontains=keyword))
        records = []
        for hr in hrs:
            day_occur = hr.time_of_occurrence.strftime("%Y-%m-%d %A")
            if hr.sub_category:
                sub_category = hr.sub_category.name
            else:
                sub_category = "no sub category"
            if hr.comment:
                comment = hr.comment
            else:
                comment = ""
            records.append({
                "day": day_occur,
                "category": hr.category.name,
                "subcategory": sub_category,
                "amount": hr.amount,
                "comment": comment,
                "account": hr.account.name,
                "ie_type": hr.category.category_type.lower()
            })
        return JsonResponse({"records": records})
    else:
        return JsonResponse({"error": "unauthenticated"})