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

    income_category = Category.objects.filter(category_type="收入")
    expense_category = Category.objects.filter(category_type="支出")

    income_records = HistoryRecord.objects.filter(
        category__in=income_category,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    expense_records = HistoryRecord.objects.filter(
        category__in=expense_category,
        time_of_occurrence__range=(start_date, end_date)
    ).values('time_of_occurrence__date').annotate(total_amount=Sum('amount')).order_by('time_of_occurrence__date')

    # 准备折线图数据，将 Decimal 转换为 float
    dates = [record['time_of_occurrence__date'].strftime('%Y-%m-%d') for record in income_records]
    income_data = [float(record['total_amount']) for record in income_records]
    expense_data = [float(record['total_amount']) for record in expense_records]

    income_data_pie = HistoryRecord.objects.filter(
        category__in=income_category,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount'))

    expense_data_pie = HistoryRecord.objects.filter(
        category__in=expense_category,
        time_of_occurrence__range=(start_date, end_date)
    ).values('category__name').annotate(total_amount=Sum('amount'))

    categories_income = [record['category__name'] for record in income_data_pie]
    amounts_income = [float(record['total_amount']) for record in income_data_pie]  # 转换为 float

    categories_expense = [record['category__name'] for record in expense_data_pie]
    amounts_expense = [float(record['total_amount']) for record in expense_data_pie]  # 转换为 float

    context = {
        'dates': dates,
        'income_data': income_data,
        'expense_data': expense_data,
        'categories_income': categories_income,
        'amounts_income': amounts_income,
        'categories_expense': categories_expense,
        'amounts_expense': amounts_expense,
    }

    return render(request, 'accounting/charts.html', context)
