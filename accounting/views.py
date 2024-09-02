from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import HistoryRecordForm
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

        user = User.objects.create_user(username=user_name, password=pwd, email=email)
        user.save()

        # 注册成功，返回登录页面并显示提示
        return render(request, 'accounting/login.html', {'success': True, 'show_login': True})

    return JsonResponse({'code': 403, 'msg': '被禁止的请求'})


from .models import *
def index(request):
    all_accounts = Account.objects.all()
    categories = Category.objects.all()
    sub_categories = SubCategory.objects.all()
    currencies = Currency.objects.all()
    ie_types = []
    for t in Category.CATEGORY_TYPES:
        ie_types.append(t)
    context = {
        'accounts': all_accounts,
        'categories': categories,
        'sub_categories': sub_categories,
        'currencies': currencies,
        'ie_types': ie_types
    }
    return render(request, 'accounting/index.html', context)
def retrieve_category(request):
    ie_type = request.POST.get('ie_type')
    categories = Category.objects.filter(category_type=ie_type)
    category_list = []
    for c in categories:
        category_list.append((c.id, c.name))
    # return HttpResponse(f'{"categories": {categories}}', content_type='application/json')
    return JsonResponse({"categories": category_list})

def retrieve_subcategory(request):
    category_type = request.POST.get('category_type')
    current_category = Category.objects.filter(name=category_type)[0]
    subcategories = SubCategory.objects.filter(parent=current_category)
    subcategory_list = []
    for sc in subcategories:
        subcategory_list.append((sc.id, sc.name))
    return JsonResponse({"subcategories": subcategory_list})

def record_income_expense(request):
    if request.user.is_authenticated:
        sub_category = request.POST.get('sub_category')
        time_now = timezone.now()
        if sub_category == "select value":
            try:
                account = request.POST.get('account')
                category = request.POST.get('category')
                currency = request.POST.get('currency')
                amount = request.POST.get('amount')
                comment = request.POST.get('comment')
                time_occur = request.POST.get('time_of_occurrence')
                history_record = HistoryRecord(account_id=account,
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
                account = form.cleaned_data['account']
                category = form.cleaned_data['category']
                sub_category = form.cleaned_data['sub_category']
                currency = form.cleaned_data['currency']
                amount = form.cleaned_data['amount']
                comment = form.cleaned_data['comment']
                time_occur = form.cleaned_data['time_of_occurrence']
                history_record = HistoryRecord(account=account,
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
from datetime import timedelta  # Make sure to import timedelta

def charts_view(request):
    # 获取用户选择的时间范围，默认为7天
    days = int(request.GET.get('days', 7))

    # 获取用户选择的收入和支出类别（可以是多个类别）
    selected_income_categories = request.GET.getlist('income_categories')
    selected_expense_categories = request.GET.getlist('expense_categories')

    # 处理类别参数（将字符串 ID 转换为整数列表）
    income_category_ids = [int(id) for id in selected_income_categories if id]
    expense_category_ids = [int(id) for id in selected_expense_categories if id]

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days + 1)]

    # 查询收入记录
    income_records = HistoryRecord.objects.filter(
        category_id__in=income_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    income_dict = {record['time_of_occurrence__date'].strftime('%Y-%m-%d'): float(record['total_amount']) for record in income_records}

    # 查询支出记录
    expense_records = HistoryRecord.objects.filter(
        category_id__in=expense_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    expense_dict = {record['time_of_occurrence__date'].strftime('%Y-%m-%d'): float(record['total_amount']) for record in expense_records}

    income_values = [income_dict.get(date, 0) for date in all_dates]
    expense_values = [expense_dict.get(date, 0) for date in all_dates]

    # 查询并处理饼状图数据
    income_pie_data = HistoryRecord.objects.filter(
        category_id__in=income_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount')).order_by('category__name')

    expense_pie_data = HistoryRecord.objects.filter(
        category_id__in=expense_category_ids,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount')).order_by('category__name')

    income_pie = [
        {'name': record['category__name'], 'value': float(record['total_amount'])}
        for record in income_pie_data
    ]

    expense_pie = [
        {'name': record['category__name'], 'value': float(record['total_amount'])}
        for record in expense_pie_data
    ]

    income_colors = ['#CCD5AE', '#E0E5B6', '#FAEDCE', '#FEFAE0']
    expense_colors = ['#0B2F9F', '#161D6F', '#98DED9', '#C7FFD8']

    for i, data in enumerate(income_pie):
        data['itemStyle'] = {'color': income_colors[i % len(income_colors)]}

    for i, data in enumerate(expense_pie):
        data['itemStyle'] = {'color': expense_colors[i % len(expense_colors)]}

    # 获取所有收入和支出类别
    all_income_categories = Category.objects.filter(category_type="income")
    all_expense_categories = Category.objects.filter(category_type="expense")

    context = {
        'income_dates': all_dates,
        'income_values': income_values,
        'expense_dates': all_dates,
        'expense_values': expense_values,
        'income_pie': income_pie,
        'expense_pie': expense_pie,
        'days': days,
        'all_income_categories': all_income_categories,
        'all_expense_categories': all_expense_categories,
        'selected_income_categories': selected_income_categories,
        'selected_expense_categories': selected_expense_categories
    }

    return render(request, 'accounting/charts.html', context)

    #登录
def login_in(request):
    if request.method == 'GET':
        return render(request, 'accounting/login.html')

    elif request.method == 'POST':
        user_name = request.POST.get('username', '')
        pwd = request.POST.get('password', '')

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


