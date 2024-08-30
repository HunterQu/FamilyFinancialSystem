from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

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
    sub_categories = SubCategory.objects.all()
    context = {
        'accounts': all_accounts,
        'sub_categories': sub_categories
    }
    print(context)
    return  render(request, 'accounting/index.html', context)
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
    income_category_ids = Category.objects.filter(category_type="收入").values_list('id', flat=True)
    expense_category_ids = Category.objects.filter(category_type="支出").values_list('id', flat=True)

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




